from settings import SETTINGS
from pydub import AudioSegment
from io import BytesIO
import traceback
import librosa
import numpy as np
import requests
import json
import os
from tqdm import tqdm
from embedding import Embedding

class TranscriptWisper:
    def __init__(self,wav_path,users_embeddins):
        self.wav_path = wav_path
        self.max_size = SETTINGS.max_size_audio
        self.openai_api_key = SETTINGS.openai_api_key
        self.language = SETTINGS.language
        self.output_dir = os.path.dirname(wav_path)
        self.folder_name = os.path.basename(wav_path)
        self.embedding = Embedding(users_embeddins)
        self.full_transcription = []


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

    def prepare_transcription(self, full_transcription_json):
        """Prepare transcription in the format: 'Speaker: Text' for each line."""
        formatted_transcription = []
        for entry in full_transcription_json:
            speaker = entry.get("speaker", "unknown")
            text = entry.get("text", "")
            formatted_transcription.append(f"{speaker}: {text}")
        return "\n".join(formatted_transcription)

    def run(self):
        try:
            audio = self.load_and_clean_audio()
            audio.export(f"{self.wav_path}_clean.wav", format="wav")
            audio_chunks = self.split_audio_if_needed(audio)
        except Exception as e:
            print(f"Error loading audio file: {e}")
            traceback.print_exc()
            return None

        for chunk in tqdm(audio_chunks, desc="processing chunks..."):
            if len(chunk) < 1000:
                print(f"❌ Skipping short chunk ({len(chunk)}ms)")
                continue

            try:
                # Step 1: Transcribe audio with Whisper
                json_transcription = self.transcribe_audio_with_whisper(chunk)
                if not json_transcription:
                    print("json_transcription is None")
                    continue
                transcription_with_clusters = self.embedding.process_transcription_with_clustering(
                    json_transcription, chunk
                )

            except Exception as e:
                print(f"Error in transcription processing: {e}")
                traceback.print_exc()
                continue
            self.full_transcription.extend(transcription_with_clusters)
        try:
            # Step 4: Infer speaker names based on full transcription
            transcription_json = [
                {"speaker":seg["speaker"], "text": seg["text"]}
                for seg in self.full_transcription
            ]

            output_path_json = os.path.join(self.output_dir, f"transcription_{self.folder_name}.json")
            output_path_txt = os.path.join(self.output_dir, f"transcription_{self.folder_name}.txt")

                # Ensure output directory exists
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

                # Save transcription to JSON
            with open(output_path_json, "w", encoding="utf-8") as f:
                json.dump(transcription_json, f, ensure_ascii=False, indent=4)

                # Convert transcription to text format and save
            with open(output_path_json, 'r', encoding="utf-8") as f:
                full_transcription_json = json.load(f)
                full_transcription_txt = self.prepare_transcription(full_transcription_json)

            with open(output_path_txt, "w", encoding="utf-8") as f:
                f.write(full_transcription_txt)
            return output_path_txt,output_path_json
        except Exception as e:
            print(f"Error in saving transcription: {e}")
            traceback.print_exc()
            return None