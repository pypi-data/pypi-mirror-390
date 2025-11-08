import logging
from dataclasses import dataclass
import json
import os
from datetime import datetime

from src.masterframework.augmentation.augmentation import Augmentation
from src.masterframework.augmentation.generator import CodeGenerator
from src.masterframework.augmentation.rag import RagDatabase
from data_loader import DatasetLoader
from src.masterframework.evaluation.metrics import create_metrics, save_detailed_results
from src.masterframework.evaluation.security_analyzer import SecurityAnalyzer, BanditAnalyzer, SemgrepAnalyzer, analyzer_output_path
from src.masterframework.models.model_provider import ModelProvider

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

DEFAULT_ANALYZERS = [BanditAnalyzer(), SemgrepAnalyzer()]


@dataclass
class ExperimentConfig:
    model: ModelProvider
    name: str
    analyzers: list[SecurityAnalyzer] = None
    language: str = "python"
    augmentations: list[Augmentation] = None
    output_path: str = "../../runs/"
    loader: DatasetLoader = None
    dataset_path: str = "data/dataset.json"
    samples: int = 1
    concurrent: bool = False


class ExperimentRunner:
    def __init__(self, config: ExperimentConfig):
        if not self.validate_config(config):
            return

        self.config = config
        self.model = config.model
        self.name = config.name
        self.language = config.language
        self.dataset_path = config.dataset_path
        self.output_path = config.output_path
        self.samples = config.samples
        self.augmentations = config.augmentations if config.augmentations else []
        self.concurrent = config.concurrent
        self.tasks = []

        if config.analyzers:
            self.analyzers = [analyzer for analyzer in config.analyzers if analyzer.is_supported(self.language)]
        else:
            self.analyzers = DEFAULT_ANALYZERS

        if config.loader:
            self.data = config.loader
        else:
            self.data = DatasetLoader(self.dataset_path)

        self.start_time = None

        self.setup()

        self.rag_db = RagDatabase()

    def validate_config(self, config: ExperimentConfig) -> bool:
        required_fields = ["model", "name"]
        for field in required_fields:
            if not hasattr(config, field):
                logging.error(f"Required field {field} is not present in the config")
                return False
        return True

    def setup(self):
        if "OPENAI_API_KEY" not in os.environ:
            with open("../../config.json", "r") as f:
                api_key = json.load(f)["openai_key"]
                os.environ["OPENAI_API_KEY"] = api_key

        self.data.load_data()
        self.tasks = self.data.filter(language=self.language).tasks()

    def setup_experiment(self):
        # self.rag_db.initialize()
        self.start_time = datetime.now()

        os.makedirs(self.output_path, exist_ok=True)

    def run(self):
        logging.info(f"Starting Experiment: {self.name} ...")
        self.setup_experiment()

        self.generate_code()

        if len(self.analyzers) > 0:
            self.evaluate_code()
            self.generate_metrics()
        else:
            logging.warning(f"None of the provided analyzers support {self.language}, skipping evaluation.")

        running_time = (datetime.now() - self.start_time).total_seconds()
        logging.info(
            f"Experiment {self.name} completed in {running_time} seconds. \nResults can be found in {self.run_path()}")

        return running_time, self.run_path()

    def generate_code(self):
        generator = CodeGenerator(
            tasks=self.tasks,
            model=self.model,
            augmentations=self.augmentations,
            output_path=self.run_path(),
        )
        generator.generate_code(self.samples, self.concurrent)

    def evaluate_code(self):
        for analyzer in self.analyzers:
            analyzer_type = analyzer.__class__.__name__
            logging.info(f"Evaluating code with {analyzer_type} ...")
            result_path = analyzer_output_path(self.run_path(), analyzer)

            analyzer.analyze(self.run_path(), result_path, self.language)
            logging.info(f"Results saved to {result_path}")

    def generate_metrics(self):
        logging.info("Generating experiment metrics ...")

        self.data.load_data()
        results = create_metrics(self.run_path(), self.name, self.analyzers,
                                 self.data.filter(language=self.language).tasks())

        logging.info(f"LOC: {results.loc}")
        logging.info(f"Total issues found: {results.issues}")
        logging.info(f"Total tasks with issues: {results.tasks_with_issues}")
        logging.info(f"Total tasks without issues: {len(self.tasks) - results.tasks_with_issues}")
        logging.info(f"Secure ratio: {results.secure_ratio}%")
        logging.info(f"Secure ratio (no Debug): {results.secure_ratio_without_debug}%")
        logging.info(f"Vulnerability Rate: {results.vuln_rate}")

        results.save_results(self.run_path(), self.config)
        save_detailed_results(self.run_path(), self.name, results.task_issues)

    def compare_results(self):
        pass

    def run_path(self):
        return os.path.join(self.output_path, self.name)


