import logging
import os

from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

from masterframework.augmentation.augmentation import Augmentation
from masterframework.data_loader import Task
from masterframework.models.model_provider import ModelProvider


class CodeGenerator:
    def __init__(self, tasks: list[Task], model: ModelProvider, augmentations: list[Augmentation], output_path: str):
        self.tasks = tasks
        self.model = model
        self.augmentations = augmentations
        self.output_path = output_path
        self.failed_tasks: list[Task] = []

    def generate_code(self, samples: int, concurrent: bool):
        logging.info(f"Generating code for {len(self.tasks)} tasks...")

        jobs: list[tuple[Task, int]] = []
        for task in self.tasks:
            for i in range(samples):
                if self.file_exists(task.id, i, task.language):
                    logging.info(f"Skipping {task.id}, {i}")
                    continue
                jobs.append((task, i))

        if concurrent:
            max_workers = min(os.cpu_count(), 20)
            logging.info(f"Using {max_workers} workers.")
            with ThreadPoolExecutor(max_workers=max_workers) as executor, tqdm(total=len(jobs),
                                                                               desc="Generating code") as pbar:
                futures = [executor.submit(self._process_generation, task, i) for task, i in jobs]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logging.exception("Error generating code: %s", e)
                    finally:
                        pbar.update(1)
        else:
            with tqdm(total=len(jobs), desc="Generating code") as pbar:
                for task, i in jobs:
                    self._process_generation(task, i)
                    pbar.update(1)

        if self.failed_tasks:
            logging.warning(f"Failed to generate content for {len(self.failed_tasks)} tasks:")
            logging.warning([task.id for task in self.failed_tasks])
            logging.warning("Rerun the generator to attempt these tasks again.")
            self.failed_tasks.clear()

    def prompt_model(self, task: Task):
        task = self.augment_prompt(task)
        content = self.model.generate(task)
        #print(f"prompt:\n{task.prompt}")
        #print("content:\n", content)
        if len(content) == 0:
            self.failed_tasks.append(task)
            logging.warning(f"Generated empty content for task {task.id}")

        return content

    def augment_prompt(self, task: Task) -> Task:
        augmented_prompt = task.prompt

        prefixes = []
        suffixes = []

        for augmentation in self.augmentations:
            augmented_prompt = augmentation.apply(task)

        for augmentation in self.augmentations:
            prefix = augmentation.apply_before(task.prompt)
            suffix = augmentation.apply_after(task.prompt)
            if prefix:
                prefixes.append(prefix)
            if suffix:
                suffixes.append(suffix)

        if prefixes:
            augmented_prompt = "\n".join(prefixes) + "\n" + augmented_prompt

        if suffixes:
            augmented_prompt = augmented_prompt + "\n".join(suffixes)

        # Create a copy of the Task object to avoid mutating the original
        task.prompt = augmented_prompt
        return Task.create_task(
            task_id=task.id,
            prompt=augmented_prompt,
            type=task.type,
            language=task.language,
            cwe_id=task.cwe_id
        )

    def _process_generation(self, task: Task, sample_index: int):
        content = self.prompt_model(task)
        # Don't write empty content
        if len(content.strip()) == 0:
            return

        code_blocks = self.model.extract_code(task, content)
        self.write_to_file(task.id, sample_index, task.language, code_blocks)

    def write_to_file(self, task_id, filename, language, code_blocks):
        location = f"{self.output_path}/{task_id}/"
        if not os.path.exists(location):
            os.makedirs(location)

        file_ending = "py" if language == "python" else "js"
        with open(f"{location}{filename}.{file_ending}", "w", encoding="utf-8") as f:
            for code in code_blocks:
                f.write(code.strip())

    def file_exists(self, task_id, filename, language):
        location = f"{self.output_path}/{task_id}/"
        file_ending = "py" if language == "python" else "js"
        return os.path.exists(f"{location}{filename}.{file_ending}")
