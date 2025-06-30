from settings import SETTINGS
from pydub import AudioSegment
from io import BytesIO
from pyannote.audio import Audio
import librosa
import numpy as np
import requests
from tqdm import tqdm


class TranscriptWisper:
    def __init__(self,wav_path):
        self.wav_path = wav_path
        self.max_size = SETTINGS.max_size_audio
        self.openai_api_key = SETTINGS.openai_api_key
        self.language = SETTINGS.language

    def split_audio_if_needed(self, audio):
        """Split audio into smaller chunks if it exceeds the maximum file size."""

        # Step 1: Get full audio size
        buffer = BytesIO()
        audio.export(buffer, format="wav")  # Save to buffer
        full_audio_size = len(buffer.getvalue())  # Size in bytes
        full_audio_duration = len(audio)  # Duration in milliseconds

        max_size_bytes = self.max_size * 1024 * 1024  # Convert MB to bytes

        # Step 2: Check if the audio needs splitting
        if full_audio_size > max_size_bytes:
            print(
                f"Audio size is {full_audio_size / (1024 * 1024):.2f}MB, exceeding the limit of {self.max_size}MB. Splitting...")
            chunks = []
            num_chunks = (full_audio_size // max_size_bytes) + 1
            chunk_duration = full_audio_duration // num_chunks  # Split evenly based on duration

            for start_time in range(0, full_audio_duration, chunk_duration):
                end_time = min(start_time + chunk_duration, full_audio_duration)
                chunk = audio[start_time:end_time]
                chunks.append(chunk)

            return chunks
        else:
            return [audio]

    def remove_silent_parts(self, audio_data, threshold, margin):  # Takes audio data and sample rate
        """Removes silent parts from audio data (NumPy array)."""
        try:
            frame_length = 512
            hop_length = frame_length // 4
            rms = librosa.feature.rms(y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]
            db = librosa.amplitude_to_db(rms + 1e-10)
            silent_frames = np.where(db < np.mean(db) + threshold)[0]
            silent_frames_expanded = []
            for frame in silent_frames:
                silent_frames_expanded.extend(
                    range(max(0, frame - margin // hop_length), min(len(db), frame + margin // hop_length)))
            silent_frames_expanded = sorted(list(set(silent_frames_expanded)))

            mask = np.ones_like(db, dtype=bool)
            mask[silent_frames_expanded] = False

            non_silent_indices = []
            for i in range(len(mask)):
                if mask[i]:
                    start = i * hop_length
                    end = min((i + 1) * hop_length, len(audio_data))
                    non_silent_indices.extend(range(start, end))
            cleaned_audio = audio_data[np.array(non_silent_indices)]

            return cleaned_audio

        except Exception as e:
            print(f"Error processing audio: {e}")
            return None

    def load_and_clean_audio(self, chunk_duration=800, threshold=-10, margin=500):  # Add chunk_duration
        """Loads, cleans audio in chunks, and returns a combined AudioSegment."""
        try:
            audio_segment = AudioSegment.from_file(self.wav_path)
            sr = audio_segment.frame_rate
            total_duration = len(audio_segment)  # in milliseconds
            cleaned_audio_chunks = []

            for start in tqdm(range(0, total_duration, chunk_duration * 1000), desc="Remove silent audio chunks"):
                end = min(start + chunk_duration * 1000, total_duration)
                chunk = audio_segment[start:end]

                samples = np.array(chunk.get_array_of_samples(), dtype=np.int16)
                cleaned_samples = self.remove_silent_parts(samples, threshold, margin)

                if cleaned_samples is not None:
                    cleaned_chunk = AudioSegment(
                        cleaned_samples.tobytes(),
                        frame_rate=sr,
                        sample_width=chunk.sample_width,
                        channels=chunk.channels
                    )
                    cleaned_audio_chunks.append(cleaned_chunk)

            # Concatenate the cleaned chunks back together
            if cleaned_audio_chunks:
                cleaned_audio_segment = cleaned_audio_chunks[0]
                for chunk in cleaned_audio_chunks[1:]:
                    cleaned_audio_segment += chunk
                return cleaned_audio_segment
            else:
                return None

        except Exception as e:
            print(f"Error loading or cleaning audio: {e}")
            return None

    def transcribe_audio_with_whisper(self, audio):
        buffer = BytesIO()
        audio.export(buffer, format="wav")
        buffer.seek(0)
        headers = {"Authorization": f"Bearer {self.openai_api_key}"}
        files = {"file": ("audio.wav", buffer, "audio/wav")}
        data = {
            "model": "whisper-1",
            "language": self.language,
            "response_format": "verbose_json",
            "temperature": 0.0,
        }
        response = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files,
                                 data=data)
        if response.status_code != 200:
            print(response)
        return response.json() if response.status_code == 200 else None

