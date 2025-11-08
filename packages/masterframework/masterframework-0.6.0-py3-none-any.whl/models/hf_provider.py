import json
from openai import OpenAI

from masterframework.models.api_providers import OpenAIProvider

API_URL = "https://router.huggingface.co/v1"


class HFModelProvider(OpenAIProvider):
    def __init__(self, model):
        self.model = model
        with open("config.json", "r") as f:
            self.hf_key = json.load(f)["hf_key"]

        self.client = OpenAI(
            base_url=API_URL,
            api_key=self.hf_key
        )

