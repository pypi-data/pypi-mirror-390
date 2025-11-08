import logging
from abc import ABC, abstractmethod

from src.masterframework.evaluation.result_parser import IssueParser, BanditParser, SemgrepParser, CodeQLParser, BearerParser
import os
import subprocess

ANALYZER_FILES = {
    "BanditAnalyzer": "bandit_report.json",
    "SemgrepAnalyzer": "semgrep_report.json",
    "BearerAnalyzer": "bearer_report.json",
    "CodeQLAnalyzer": "codeql_report.csv",
}


class SecurityAnalyzer(ABC):

    @abstractmethod
    def analyze(self, path, output_path, language: str):
        """Generate a security analysis report for the given path."""
        pass

    @abstractmethod
    def supported_languages(self) -> set[str]:
        """Return a list of supported programming languages."""
        pass

    @abstractmethod
    def get_issue_parser(self) -> IssueParser:
        """Return the issue parser associated with this analyzer."""
        pass

    def is_supported(self, language) -> bool:
        """Check if the given programming language is supported."""
        return language in self.supported_languages()


class BanditAnalyzer(SecurityAnalyzer):
    LANGUAGES = {"python"}

    def analyze(self, path, output_path, language: str):
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        cmd = [
            "bandit",
            "-r", path,
            "-f", "json",
            "-o", output_path,
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode >= 2:
            raise RuntimeError(
                f"Bandit failed with exit code {result.returncode}: {result.stderr.strip()}"
            )

        return output_path

    def supported_languages(self) -> set[str]:
        return self.LANGUAGES

    def get_issue_parser(self) -> IssueParser:
        return BanditParser()

    def __str__(self):
        return "BanditAnalyzer"


class SemgrepAnalyzer(SecurityAnalyzer):
    LANGUAGES = {
        "python", "javascript"
    }

    def analyze(self, path, output_path, language: str):
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        cmd = [
            "semgrep",
            "ci",
            "--subdir", path,
            "--json",
            f"--json-output={output_path}",
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode >= 2:
            raise RuntimeError(
                f"Semgrep failed with exit code {result.returncode}: {result.stderr.strip()}"
            )

        return output_path

    def supported_languages(self) -> set[str]:
        return self.LANGUAGES

    def get_issue_parser(self) -> IssueParser:
        return SemgrepParser()

    def __str__(self):
        return "SemgrepAnalyzer"


class CodeQLAnalyzer(SecurityAnalyzer):
    LANGUAGES = {
        "python", "javascript"
    }

    def __init__(self, codeql_path: str):
        self.codeql_path = codeql_path

    def initialize(self, path: str, language: str, db_path: str):
        """Initialize the CodeQL database"""
        logging.info(f"Initializing CodeQL database for {language} at {db_path}")

        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        cmd = [
            self.codeql_path,
            "database",
            "create",
            db_path,
            f"--language={language}",
            f"--source-root={path}"
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"CodeQL database creation failed with exit code {result.returncode}: {result.stderr.strip()}"
            )

    def analyze(self, path, output_path, language: str):
        # check if the codeql database is initialized
        db_path = self.codeql_db_path(output_path)
        if not os.path.exists(db_path):
            self.initialize(path, language, db_path)

        # run the analysis
        cmd = [
            self.codeql_path,
            "database",
            "analyze",
            db_path,
            "--format=csv",
            f"--output={output_path}",
            "codeql/python-queries:codeql-suites/python-security-extended.qls"
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"CodeQL analysis failed with exit code {result.returncode}: {result.stderr.strip()}"
            )

    def codeql_db_path(self, output_path: str):
        # TODO: make this configurable
        return os.path.join("codeql_test", "codeql_db")

    def supported_languages(self) -> set[str]:
        return self.LANGUAGES

    def get_issue_parser(self) -> IssueParser:
        return CodeQLParser()

    def __str__(self):
        return "CodeQLAnalyzer"


class BearerAnalyzer(SecurityAnalyzer):
    LANGUAGES = {
        "python", "javascript"
    }

    def analyze(self, path, output_path, language: str):
        output_dir = os.path.dirname(output_path)
        abs_path = os.path.abspath(path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        base_output_path = os.path.basename(output_path)
        docker_output = f"/tmp/scan/{base_output_path}"

        cmd = [
            "docker",
            "run",
            "-v", f"{abs_path}:/tmp/scan",
            "bearer/bearer:latest-amd64",
            "scan", "/tmp/scan", "--report",
            "security",
            "--format", "json",
            "--output", docker_output,
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            raise RuntimeError(
                f"Bearer failed with exit code {result.returncode}: {result.stderr.strip()}"
            )

        return output_path

    def supported_languages(self) -> set[str]:
        return self.LANGUAGES

    def get_issue_parser(self) -> IssueParser:
        return BearerParser()

    def __str__(self):
        return "BearerAnalyzer"


def analyzer_output_path(run_path: str, analyzer: SecurityAnalyzer) -> str:
    filename = ANALYZER_FILES.get(analyzer.__class__.__name__)
    return os.path.join(run_path, filename)
