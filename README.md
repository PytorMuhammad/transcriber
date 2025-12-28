# 🎙️ Elite Transcriber CLI

![Banner](banner.png)

An "Elite" level command-line interface for high-performance audio and video transcription. Optimized for English, Urdu, and Hindi, powered by `faster-whisper`.

## ✨ Features

- **🚀 Industry-Leading Performance**: Powered by `faster-whisper`, achieving up to 600x realtime transcription on CPU.
- **🌍 Multi-Language Mastery**: Seamlessly detects and transcribes English, Urdu, and Hindi.
- **💎 Premium UX**: Beautiful terminal interface with real-time progress tracking via `rich`.
- **🛠️ Power-User Control**: Force language selection and provide technical context via prompts.
- **📂 Batch Processing**: Transcribe entire directories with a single command.
- **🌎 Global Command**: Run `transcriber` from any PowerShell or CMD window.

## 🚀 Installation

### Prerequisites
- Python 3.10+
- FFmpeg installed and added to PATH

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Transcriber.git
   cd Transcriber
   ```
2. Install dependencies:
   ```bash
   pip install faster-whisper rich pydantic
   ```
3. Add to PATH (Windows):
   - Add the project directory to your User PATH environment variable.
   - Use the included `transcriber.bat` for global access.

## 📖 Usage

### Single File
```powershell
transcriber /f "path/to/media.mp3"
```

### Entire Directory
```powershell
transcriber /d "path/to/folder"
```

### Advanced Precision
```powershell
transcriber /d "path/to/folder" --model large-v3 --lang ur --prompt "Namma Yatri, Authentication, Firebase"
```

## 🛠️ Configuration

| Flag | Description | Default |
| --- | --- | --- |
| `/f`, `--file` | Path to a single file | None |
| `/d`, `--dir` | Path to a directory | None |
| `--model` | Model size (tiny, base, small, medium, large-v3) | `base` |
| `--lang` | Force language (e.g., `ur`, `hi`, `en`) | Auto |
| `--prompt` | Technical context for the AI | None |

## 🤝 Contribution
Built with ❤️ for elite level developers. Feel free to fork and enhance!
