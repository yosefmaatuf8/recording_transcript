from embedding import Embedding
from pydub import AudioSegment

class CreateEmbeddingUsers:
    def __init__(self, audio_path, users_time: dict):
        self.audio_path = audio_path
        self.users_time = users_time
        self.embedding = Embedding()
        self.full_audio = AudioSegment.from_file(audio_path)
        print("Total audio length (ms):", len(self.full_audio))

        self.users_embeddings = {}
    def extract_audio_segment(self, start_time_sec: float, end_time_sec: float, output_path: str = None) -> AudioSegment:
        """
        Cut a segment from the audio file between start_time and end_time in seconds.

        Args:
            start_time_sec (float): Start time in seconds.
            end_time_sec (float): End time in seconds.
            output_path (str, optional): If provided, save the segment to this path.

        Returns:
            AudioSegment: The cut audio segment.
        """
        

        start_ms = int(start_time_sec * 1000)
        end_ms = int(end_time_sec * 1000)
        segment = self.full_audio[start_ms:end_ms]

        if output_path:
            segment.export(output_path, format="wav")

        return segment


    def run(self):
        for user in self.users_time:
            try:
                start = self.users_time[user]["start"]
                end = self.users_time[user]["end"]

                if end <= start:
                    print(f"Skipping {user}: end <= start")
                    continue

                user_clip = self.extract_audio_segment(start, end)

                if user_clip is None or len(user_clip) == 0:
                    print(f"Skipping {user}: empty audio clip")
                    continue

                user_embedding = self.embedding.extract_embedding(user_clip)
                self.users_embeddings[user] = user_embedding

            except Exception as e:
                print("Error to create embedding", e)

        return self.users_embeddings

        # def run(self):
        #     for user in self.users_time.keys():
        #         try:
        #             print("START",self.users_time[user]["start"], "END",self.users_time[user]["end"])
        #             user_clip = self.extract_audio_segment(self.users_time[user]["start"], self.users_time[user]["end"], self.audio_path)
        #             user_embedding = self.embedding.extract_embedding(user_clip)
        #             self.users_embeddings[user] = user_embedding
        #             print(self.users_embeddings)
        #             return self.users_embeddings
        #         except Exception as e:
        #             print("Error to create embedding",e)