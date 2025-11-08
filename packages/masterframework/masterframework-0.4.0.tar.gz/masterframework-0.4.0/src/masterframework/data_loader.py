import json

import pandas as pd


class Task:
    def __init__(self, task):
        self.prompt = task["prompt"]
        self.id = task["taskId"]
        self.language = task["language"]
        self.type = task["type"]
        self.cwe_id: list[str] = task["CWE_ID"]


    @staticmethod
    def create_task(prompt, task_id, language, type, cwe_id):
        return Task({
            "prompt": prompt,
            "taskId": task_id,
            "language": language,
            "type": type,
            "CWE_ID": cwe_id
        })

    def __str__(self):
        return f"Task ID: {self.id}, Prompt: {self.prompt}, Language: {self.language}"


class DatasetLoader:
    def __init__(self, path="data/dataset.json", data=None):
        if data is None:
            self.data = []
        self.path = path

    def load_data(self):
        """
        Load the dataset from a JSON file specified by the path attribute.
        Updates the data attribute with the loaded data.
        Returns the DatasetLoader instance for method chaining.
        """
        with open(self.path, 'r') as f:
            data = json.load(f)
            self.data = data

        return self

    def prompts(self):
        """
        Retrieve all prompts from the loaded dataset.
        Returns a list of prompt strings.
        """
        return [d["prompt"] for d in self.data]

    def tasks(self) -> list[Task]:
        """
        Convert the loaded dataset into a list of Task objects.
        Returns a list of Task instances.
        """
        return [Task(d) for d in self.data]

    def filter(self, language=None, instruct_type=None):
        """
        Filter the dataset based on the specified language and instruction type.
        Modifies the data attribute to only include entries matching the criteria.
        Returns the DatasetLoader instance for method chaining.
        """
        self.data = [d for d in self.data if (language is None or d["language"] == language) and (
                instruct_type is None or d["type"] == instruct_type)]
        return self

    def to_pd(self):
        """
        Convert the current dataset into a pandas DataFrame.
        Returns a DataFrame containing the dataset.
        """
        return pd.DataFrame(self.data)
