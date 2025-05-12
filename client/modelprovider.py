
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class ModelProvider:
    anthropic = Anthropic()
    mode = "anthropic"

    def set_mode(self, mode):
        self.mode = mode

    def get_response(self, messages, system_prompt, available_tools):
        if self.mode == "anthropic":
            return self.anthropic.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=1000,
                messages=messages,
                system=system_prompt,
                tools=available_tools
            )