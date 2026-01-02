import os
import datetime
import time
from faster_whisper import WhisperModel
from utils import log_info, log_success, log_error, get_progress

def format_timestamp(seconds: float) -> str:
    """Formats seconds into HH:MM:SS string."""
    td = datetime.timedelta(seconds=seconds)
    # Remove microseconds
    s = str(td).split('.')[0]
    if s.count(':') == 1:
        s = "00:" + s
    return s

class TranscriberEngine:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        log_info(f"Initializing transcription model ({model_size})...")
        try:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
            log_success("Model initialized successfully.")
        except Exception as e:
            log_error(f"Failed to initialize model: {e}")
            raise

    def transcribe(self, file_path: str, language=None, initial_prompt=None, silent=False):
        """Transcribes a single file. If silent=True, suppresses console output for live mode."""
        if not os.path.exists(file_path):
            if not silent:
                log_error(f"File not found: {file_path}")
            return None, []

        if not silent:
            log_info(f"Transcribing: {os.path.basename(file_path)}")
        start_time = time.time()
        
        try:
            segments, info = self.model.transcribe(
                file_path, 
                beam_size=5, 
                language=language,
                initial_prompt=initial_prompt
            )
            
            if not silent:
                log_info(f"Language: '{info.language}' (Prob: {info.language_probability:.2f})")
            
            full_transcript = []
            segments_data = []
            
            if silent:
                # Silent mode: just collect segments, no progress bar
                for segment in segments:
                    text = segment.text.strip()
                    if text:
                        full_transcript.append(text)
                        segments_data.append(segment)
            else:
                # Normal mode: show progress
                with get_progress() as progress:
                    task = progress.add_task("[cyan]Processing segments...", total=None)
                    
                    for segment in segments:
                        text = segment.text.strip()
                        if text:
                            print(f"[{format_timestamp(segment.start)} -> {format_timestamp(segment.end)}] {text}")
                            full_transcript.append(text)
                            segments_data.append(segment)
                        progress.update(task, advance=1)

            duration = time.time() - start_time
            if not silent:
                log_success(f"Transcription completed in {duration:.2f}s")
            return " ".join(full_transcript), segments_data
        
        except Exception as e:
            if not silent:
                log_error(f"Error during transcription: {e}")
            return None, []
