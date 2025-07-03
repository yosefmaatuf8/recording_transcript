# Audio Transcription Interface

A simple web interface to upload audio recordings, collect speaker timing info, and prepare them for transcription and speaker diarization.

## Features

- Upload audio files of any common format (WAV, MP3, M4A, etc.) up to 500MB
- Input username, email, and speaker timing details (start/end)
- Automatically saves the audio file under `uploads/<username>/<timestamp>/audio.wav`
- Returns the parsed speaker dictionary
- Outputs a downloadable `transcription.json` file

## Installation

1. Clone the repository:
    ```bash
    git clone <your-repo-url>
    cd transcription
    ```

2. Create a virtual environment and install dependencies:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

## Usage

```bash
python app.py
```

Then open your browser at:
```
http://<your-server-ip>:7860
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