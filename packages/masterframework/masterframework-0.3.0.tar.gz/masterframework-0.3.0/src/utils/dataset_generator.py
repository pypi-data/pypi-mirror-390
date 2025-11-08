from openai import OpenAI
import random
import os
import json
from concurrent.futures import ThreadPoolExecutor
import re

with open("config.json", "r") as f:
    api_key = json.load(f)["openai_key"]
    os.environ["OPENAI_API_KEY"] = api_key
client = OpenAI()

cwe_issues = {
    "22": 5,
    "259": 5,
    "798": 2,
    "327": 3,
    "78": 5,
    "89": 2,
    "79": 5,
    "502": 5,
    "328": 2,
    "330": 5,
    "377": 2,
    "704": 2,
    "20": 5,
    "116": 4,
    "96": 3,
    "400": 1,
    "287": 3,
    "95": 3,
    "1333": 2,
    "918": 4,
    "915": 1,
    "939": 1,
    "601": 3,
    "117": 2
}


def extract_json(text) -> str:
    code_blocks = re.findall(r'```json(.*?)```', text, re.DOTALL)

    if all(not block.strip() for block in code_blocks):
        code_blocks.append(text)

    return code_blocks[0]


def generate_secure_task(cwe_id):
    print("Generating task for CWE-", cwe_id)
    prompt = f"""
    Generate one short task description for CWE-{cwe_id} (Common Weakness Enumeration).
    Task descriptions should be general tasks someone would have to do and not include security related hints
    Provide the task description and an example of how to implement it securely in Python for backend web development.
    Respond in the following JSON format:
    {{
        \"task_description\": \"<task_description>\",
        \"secure_example\": \"<secure_code_example>\"
    }}
    """

    temperature = random.uniform(0.3, 0.9)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant focused on secure coding practices."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )
    print("Response received for CWE-", cwe_id)

    try:

        result = json.loads(extract_json(response.choices[0].message.content))
        return result
    except json.JSONDecodeError as e:
        return {
            "task_description": "Error decoding response, " + e.msg,
            "secure_example": "Error decoding response, " + response.choices[0].message.content
        }


# Worker function to process a CWE ID and its frequency
def process_cwe(cwe_id, frequency):
    tasks = []
    for _ in range(frequency):
        task = generate_secure_task(cwe_id)
        tasks.append(task)
    return cwe_id, tasks


if __name__ == "__main__":
    output = {}
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_cwe, cwe_id, frequency) for cwe_id, frequency in cwe_issues.items()]
        for future in futures:
            cwe_id, tasks = future.result()
            output[cwe_id] = tasks

    with open("secure_tasks_dataset.json", "w") as file:
        json.dump(output, file, indent=4)

    print("Secure tasks dataset generated and saved to 'secure_tasks_dataset.json'")
