from abc import ABC, abstractmethod
import re

from data_loader import Task


class ModelProvider(ABC):
    model: str

    @abstractmethod
    def generate(self, task) -> str:
        pass

    def extract_code(self, task: Task, content) -> list:
        # Remove thinking <think> tags if any
        if "<think>" in content and "</think>" in content:
            # take everything after </think>
            content = content.split("</think>")[-1]

        if task.language == "python":
            code_blocks = re.findall(r'```python(.*?)```', content, re.DOTALL)
        else:
            code_blocks = re.findall(r'```javascript(.*?)```', content, re.DOTALL)

        if all(not block.strip() for block in code_blocks):
            code_blocks.append(content)

        return code_blocks
