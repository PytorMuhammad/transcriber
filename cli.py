import sys
import os
import argparse
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

    if args.file:
        process_file(engine, args.file, args.lang, args.prompt)
    elif args.dir:
        process_directory(engine, args.dir, args.lang, args.prompt)

def process_file(engine, file_path, lang=None, prompt=None):
    if not os.path.isfile(file_path):
        log_error(f"'{file_path}' is not a valid file.")
        return
    
    transcript = engine.transcribe(file_path, language=lang, initial_prompt=prompt)
    if transcript:
        # For now, we just log completion as per user request (logs only, no save unless specified)
        # But let's show a snippet or confirm it's done.
        log_success(f"Successfully transcribed {os.path.basename(file_path)}")

def process_directory(engine, dir_path, lang=None, prompt=None):
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
        process_file(engine, file_path, lang, prompt)
        print("\n")

if __name__ == "__main__":
    main()
