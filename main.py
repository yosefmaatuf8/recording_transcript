from transcript_wisper import TranscriptWisper
from create_embedding_users import CreateEmbeddingUsers
from utils import *
from transcription_mail_sender import TranscriptEmailSender


class Main:
    def __init__(self,audio_peth, users_time, email):
        self.audio_peth = audio_peth
        self.users_time = users_time
        self.email = email
        self.users_embedding = None
        self.create_embedding_users = CreateEmbeddingUsers(self.audio_peth, self.users_time)
        self.transcript_wisper = None
        self.transcript_file_path = None
        self.transcription_mail_sender = None


    def run(self):
        self.users_embedding = self.create_embedding_users.run()
        self.transcript_wisper = TranscriptWisper(self.audio_peth,self.users_embedding)

        txt_path ,self.transcript_file_path = self.transcript_wisper.run()
        self.transcription_mail_sender = TranscriptEmailSender()
        self.transcription_mail_sender.run(self.email, txt_path)


if __name__ == '__main__':
    timeuser = {
    "מירית": {
        "start": time_str_to_seconds("00:00"),
        "end": time_str_to_seconds("00:15")
    }}
    test = Main("uploads/yosef/2025-07-02_07-50-09/audio.wav",timeuser,"yosefmaatuf@848@gmail.com")
    test.run()