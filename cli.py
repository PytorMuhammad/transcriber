import sys
import os
import argparse
import datetime
from transcriber_engine import TranscriberEngine
from utils import welcome_banner, log_info, log_error, log_success, console

def main():
    # Preprocess sys.argv to support /f and /d
    processed_args = []
    for arg in sys.argv:
        if arg.lower() == "/f":
            processed_args.append("-f")
        elif arg.lower() == "/d":
            processed_args.append("-d")
        else:
            processed_args.append(arg)
    
    parser = argparse.ArgumentParser(description="Elite Transcriber Tool")
    parser.add_argument("-f", "--file", help="Path to a single audio/video file")
    parser.add_argument("-d", "--dir", help="Path to a directory containing audio/video files")
    parser.add_argument("--model", default="base", help="Whisper model size (tiny, base, small, medium, large-v3)")
    parser.add_argument("--lang", help="Force a specific language (e.g., ur, hi, en)")
    parser.add_argument("--prompt", help="Provide context keywords (e.g., 'Namma Yatri, Authentication, Firebase')")
    parser.add_argument("--no-save", action="store_true", help="Disable saving transcript to .txt and .srt files")

    args, unknown = parser.parse_known_args(processed_args[1:])
    
    welcome_banner()

        
    if not args.file and not args.dir:
        log_error("No input specified. Use /f [file] or /d [directory].")
        parser.print_help()
        sys.exit(1)

    try:
        engine = TranscriberEngine(model_size=args.model)
    except Exception:
        sys.exit(1)

    save = not args.no_save

    if args.file:
        process_file(engine, args.file, args.lang, args.prompt, save)
    elif args.dir:
        process_directory(engine, args.dir, args.lang, args.prompt, save)

def process_file(engine, file_path, lang=None, prompt=None, save=True):
    if not os.path.isfile(file_path):
        log_error(f"'{file_path}' is not a valid file.")
        return
    
    transcript, segments = engine.transcribe(file_path, language=lang, initial_prompt=prompt)
    if transcript:
        log_success(f"Successfully transcribed {os.path.basename(file_path)}")
        if save:
            save_transcript(file_path, transcript)
            save_srt(file_path, segments)

def save_transcript(file_path, transcript):
    output_path = os.path.splitext(file_path)[0] + ".txt"
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        log_info(f"💾 Saved Text: {os.path.basename(output_path)}")
    except Exception as e:
        log_error(f"Failed to save transcript: {e}")

def format_srt_timestamp(seconds: float) -> str:
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int(td.microseconds / 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def save_srt(file_path, segments):
    output_path = os.path.splitext(file_path)[0] + ".srt"
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, 1):
                start = format_srt_timestamp(segment.start)
                end = format_srt_timestamp(segment.end)
                f.write(f"{i}\n{start} --> {end}\n{segment.text.strip()}\n\n")
        log_info(f"💾 Saved SRT:  {os.path.basename(output_path)}")
    except Exception as e:
        log_error(f"Failed to save SRT: {e}")

def process_directory(engine, dir_path, lang=None, prompt=None, save=True):
    if not os.path.isdir(dir_path):
        log_error(f"'{dir_path}' is not a valid directory.")
        return

    extensions = ('.mp3', '.mp4', '.wav', '.m4a', '.flac', '.ogg', '.mov', '.mkv')
    files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.lower().endswith(extensions)]
    
    if not files:
        log_error(f"No supported audio/video files found in {dir_path}")
        return

    log_info(f"Found {len(files)} files to transcribe.")
    
    for i, file_path in enumerate(files, 1):
        console.rule(f"[brand]File {i}/{len(files)}: {os.path.basename(file_path)}[/brand]")
        process_file(engine, file_path, lang, prompt, save)
        print("\n")

if __name__ == "__main__":
    main()
