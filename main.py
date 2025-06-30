from transcript_wisper import TranscriptWisper
from create_embedding_users import CreateEmbeddingUsers

class Main:
    def __init__(self,audio_peth, users_time):
        self.audio_peth = audio_peth
        self.users_time = users_time
        self.users_embedding = None
        self.create_embedding_users = CreateEmbeddingUsers(self.audio_peth, self.users_time)
        self.transcript_wisper = None


    def run(self):
        self.users_embedding = self.create_embedding_users.run()
        self.transcript_wisper = TranscriptWisper(self.audio_peth,self.users_embedding)