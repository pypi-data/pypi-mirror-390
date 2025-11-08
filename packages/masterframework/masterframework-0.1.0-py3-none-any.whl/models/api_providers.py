from openai import OpenAI
import os
import re
import json

from data_loader import Task
from src.models.model_provider import ModelProvider


class OpenAIProvider(ModelProvider):
    def __init__(self, model, base_url=None, client=None):
        self.model = model
        if not client:
            if "OPENAI_API_KEY" not in os.environ:
                with open("config.json", "r") as f:
                    api_key = json.load(f)["openai_key"]
                    os.environ["OPENAI_API_KEY"] = api_key

            if base_url:
                self.client = OpenAI(base_url=base_url)
            else:
                self.client = OpenAI()
        else:
            self.client = client

    def generate(self, task: Task) -> str:
        prompt = task.prompt
        if task.type == "complete":
            prompt = f"Complete the following code, return the full code not just your completion:\n{prompt}"

        #print("Prompt sent to model:\n", prompt)
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional python programmer, only respond with code."},
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=self.model,
        )

        return response.choices[0].message.content


class OllamaProvider(OpenAIProvider):
    def __init__(self, model):
        self.model = model
        self.client = OpenAI(
            base_url="http://localhost:11434/v1/",
            api_key="ollama"
        )

    def extract_code(self, task: Task, content) -> list:


        content = content.replace("```python", "```")
        code_blocks = re.findall(r'```(.*?)```', content, re.DOTALL)
        if all(not block.strip() for block in code_blocks):
            code_blocks.append(content)

        return code_blocks
