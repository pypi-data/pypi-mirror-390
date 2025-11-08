import re
from transformers import AutoTokenizer, AutoModelForCausalLM
from src.masterframework.models.model_provider import ModelProvider


class LocalProvider(ModelProvider):
    def __init__(self, model_name):

        self.model_name = model_name
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def generate(self, task) -> str:
        prompt = task.prompt
        if task.type == "complete":
            prompt = f"Complete the following code, return the full code not just your completion:\n{prompt}"

        messages = [
            {"role": "system",
             "content": "You are a professional python programmer, only respond with valid python code."},
            {
                "role": "user",
                "content": prompt,
            }
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response

    def extract_code(self, task, content) -> list:
        content = content.replace("```python", "```")
        code_blocks = re.findall(r'```(.*?)```', content, re.DOTALL)
        if all(not block.strip() for block in code_blocks):
            code_blocks.append(content)

        return code_blocks
