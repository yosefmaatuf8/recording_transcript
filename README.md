# Audio Transcription App

A simple Gradio-based app to upload audio, define speaker segments, generate transcripts and PDF, and send to email.

---

## 🛠️ Requirements

Make sure you have the following installed:

### 1. System (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install \
  build-essential \
  libjpeg-dev \
  zlib1g-dev \
  libpng-dev \
  libfreetype6-dev \
  libfontconfig1-dev \
  python3-dev \
  pandoc \
  texlive-xetex \
  ffmpeg
```
## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yosefmaatuf8/recording_transcript.git
    cd recording_transcript
    ```

2. Create a virtual environment and install dependencies:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    ```

## Usage

```bash
python3 GUI.py
```

Open your browser to:
```
 http://0.0.0.0:5000.
```

## Folder Structure

Uploaded audio and transcription files are saved in:

```
uploads/
  └── <username>/
      └── <timestamp>/
          ├── audio.wav
          └── transcription.json
```

## License

MIT License
