from scipy.spatial.distance import cosine
import numpy as np
from io import BytesIO
from pyannote.audio import Model, Inference
from settings import SETTINGS
class Embedding:
    def __init__(self,users_embedding=None):
        self.huggingface_api_key = SETTINGS.huggingface_api_key
        self.users_embedding = users_embedding or  {}
        self.inference = self.load_model()

    def load_model(self):
        """Loads the pre-trained speaker embedding model."""
        model = Model.from_pretrained("pyannote/embedding", use_auth_token=self.huggingface_api_key)
        return Inference(model, window="whole")

    def extract_embedding(self,audio_clip):
        """
        Extracts the embedding from an audio clip.

        Args:
            audio_clip (pydub.AudioSegment): The audio clip to extract the embedding from.

        Returns:
            numpy.ndarray: The speaker embedding.
        """
        buffer = BytesIO()
        audio_clip.export(buffer, format="wav")
        buffer.seek(0)
        return self.inference(buffer)

    def get_closest_speaker(self, segment_embedding):
        """
        Finds the closest speaker to a given embedding using weighted cosine similarity.

        Args:
            segment_embedding (numpy.ndarray): The embedding to compare.
            self.users_embedding (dict, optional): A dictionary of known speaker embeddings. Defaults to self.embeddings.
        Returns:
            tuple: The closest speaker label and the minimum distance.
        """
        closest_speaker = None
        min_distance = float("inf")

        for speaker in self.users_embedding.keys():
            embedding = self.users_embedding[speaker]
            # Compute cosine similarity against multiple embeddings
            distance = cosine(segment_embedding, embedding)
            if distance < min_distance:
                min_distance = distance
                closest_speaker = speaker

        return closest_speaker, min_distance

    def assign_speaker(self, audio_clip):
        """
        Assigns a speaker to an audio clip using similarity checks.

        Args:
            audio_clip (pydub.AudioSegment): The audio clip to assign a speaker to.

        Returns:
            str: The assigned speaker label.
        """
        if len(audio_clip) < 400:
            return "Little_segment"

        embedding = self.extract_embedding(audio_clip)
        closest_speaker, min_distance = self.get_closest_speaker(embedding)
        return closest_speaker

    def process_transcription_with_clustering(self, json_transcription, audio_chunk):
        """
        Processes a transcription with speaker clustering.

        Args:
            json_transcription (dict): The JSON transcription.
            audio_chunk (pydub.AudioSegment): The audio chunk.

        Returns:
            list: A list of dictionaries representing the conversation with speaker labels.
        """
        speakers = []
        segments = json_transcription["segments"]
        for segment in segments:
            start_ms = int(segment["start"] * 1000)
            end_ms = int(segment["end"] * 1000)
            segment_audio = audio_chunk[start_ms:end_ms]
            speaker_label = self.assign_speaker(segment_audio)
            speakers.append(speaker_label)
        conversation = [{"start": seg["start"], "end": seg["end"], "text": seg["text"], "speaker": speakers[i]} for
                        i, seg in enumerate(segments)]
        return conversation