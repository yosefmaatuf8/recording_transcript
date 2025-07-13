import os
from dotenv import find_dotenv, load_dotenv
class Settings:
    def __init__(self):
        env_path = find_dotenv()
        load_dotenv(env_path, override=True)
        # OpenAI
        self.openai_api_key = self.validate_env("OPENAI_API_KEY")
        self.language = "he"
        self.max_size_audio = 10
        # huggingface
        self.huggingface_api_key = self.validate_env("HUGGINGFACE_API_KEY")

        # googel_mail
        self.sender_email = self.validate_env("SENDER_EMAIL")
        self.sender_password = self.validate_env("SENDER_PASSWORD")
        
    def validate_env(self, var_name):
        """Validate that the environment variable is set."""
        value = os.getenv(var_name)
        if not value:
            print(f"Error: {var_name} is not set.")
        return value

    def validate_path(self, var_name):
        """Validate that the environment variable is set and points to a valid path."""
        value = os.getenv(var_name)
        if not value:
            print(f"Error: {var_name} is not set.")
        elif not os.path.exists(value):
            print(f"Error: Path does not exist for {var_name}: {value}")
        return value
SETTINGS = Settings()
