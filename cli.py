import sys
import os
import argparse
import datetime
import tempfile
import wave
import numpy as np
import sounddevice as sd
from transcriber_engine import TranscriberEngine
from utils import welcome_banner, log_info, log_error, log_success, log_warning, console

STOP_PHRASE = "done over"

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
    
    parser = argparse.ArgumentParser(description="Elite Transcriber Tool V2")
    parser.add_argument("-f", "--file", help="Path to a single audio/video file")
    parser.add_argument("-d", "--dir", help="Path to a directory containing audio/video files")
    parser.add_argument("--listen", action="store_true", help="Start live microphone transcription")
    parser.add_argument("--model", default="base", help="Whisper model size (tiny, base, small, medium, large-v3)")
    parser.add_argument("--lang", help="Force a specific language (e.g., ur, hi, en)")
    parser.add_argument("--prompt", help="Provide context keywords")
    parser.add_argument("--txt", action="store_true", help="Save transcript to a .txt file")
    parser.add_argument("--srt", action="store_true", help="Save transcript to an .srt file")
    parser.add_argument("--stop-word", default=STOP_PHRASE, help="Stop phrase for --listen mode (default: 'done over')")

    args, unknown = parser.parse_known_args(processed_args[1:])
    
    welcome_banner()

    if not args.file and not args.dir and not args.listen:
        log_error("No input specified. Use /f [file], /d [directory], or --listen.")
        parser.print_help()
        sys.exit(1)

    try:
        engine = TranscriberEngine(model_size=args.model)
    except Exception:
        sys.exit(1)

    if args.listen:
        run_listen_mode(engine, args.lang, args.prompt, args.stop_word)
    elif args.file:
        process_file(engine, args.file, args.lang, args.prompt, args.txt, args.srt)
    elif args.dir:
        process_directory(engine, args.dir, args.lang, args.prompt, args.txt, args.srt)

def run_listen_mode(engine, lang, prompt, stop_word):
    """Live microphone listening mode."""
    sample_rate = 16000
    chunk_duration = 5  # seconds
    
    log_info(f"🎤 Listening... (Say '{stop_word}' to stop)")
    console.rule("[brand]Live Transcription[/brand]")
    
    full_text = []
    
    try:
        while True:
            # Record a chunk
            audio_chunk = sd.rec(int(chunk_duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
            sd.wait()
            
            # Save to temp file for Whisper
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
                audio_int16 = (audio_chunk * 32767).astype(np.int16)
                with wave.open(tmp_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sample_rate)
                    wf.writeframes(audio_int16.tobytes())
            
            # Transcribe chunk
            transcript, _ = engine.transcribe(tmp_path, language=lang, initial_prompt=prompt, silent=True)
            os.remove(tmp_path)
            
            if transcript:
                console.print(f"[cyan]>[/cyan] {transcript}")
                full_text.append(transcript)
                
                # Check for stop phrase
                if stop_word.lower() in transcript.lower():
                    log_success(f"Stop phrase '{stop_word}' detected. Ending session.")
                    break
                    
    except KeyboardInterrupt:
        log_warning("Session interrupted by user.")
    
    console.rule("[brand]Session Ended[/brand]")
    log_info(f"Total transcribed: {len(full_text)} segments.")

def process_file(engine, file_path, lang=None, prompt=None, save_txt=False, save_srt=False):
    if not os.path.isfile(file_path):
        log_error(f"'{file_path}' is not a valid file.")
        return
    
    transcript, segments = engine.transcribe(file_path, language=lang, initial_prompt=prompt)
    if transcript:
        log_success(f"Successfully transcribed {os.path.basename(file_path)}")
        if save_txt:
            save_transcript(file_path, transcript)
        if save_srt:
            save_srt_file(file_path, segments)

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

def save_srt_file(file_path, segments):
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

def process_directory(engine, dir_path, lang=None, prompt=None, save_txt=False, save_srt=False):
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
        process_file(engine, file_path, lang, prompt, save_txt, save_srt)
        print("\n")

if __name__ == "__main__":
    main()
