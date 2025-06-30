import os
from dotenv import find_dotenv, load_dotenv
class Settings:
    def __init__(self):
        env_path = find_dotenv()
        load_dotenv(env_path, override=True)
        self.output_path = self.validate_path("OUTPUT_PATH")
        # OpenAI
        self.max_tokens = int(self.validate_env("MAX_TOKENS"))
        self.openai_api_key = self.validate_env("OPENAI_API_KEY")
        self.openai_model_name = self.validate_env("OPENAI_MODEL_NAME")
        self.language = "he"
        self.max_size_audio = 10
        # huggingface
        self.huggingface_api_key = self.validate_env("HUGGINGFACE_API_KEY")

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
