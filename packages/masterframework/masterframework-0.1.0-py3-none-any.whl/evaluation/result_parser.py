from abc import ABC, abstractmethod
import re
from dataclasses import dataclass


@dataclass
class Issue:
    task_id: str
    cwe_id: list
    description: str

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "cwe_id": self.cwe_id,
        }


class IssueParser(ABC):
    @abstractmethod
    def parse_issues(self, content) -> list[Issue]:
        pass


class CodeQLParser(IssueParser):
    def __init__(self):
        self.cwes = {
            'Code injection': '94',
            'Information exposure through an exception': '209',
            'URL redirection from remote source': '601',
            'Use of a broken or weak cryptographic hashing algorithm on sensitive data': '327',
            'Incomplete URL substring sanitization': '79',
            'Flask app is run in debug mode': '489',
            'Clear-text storage of sensitive information': '312',
            'Clear-text logging of sensitive information': '312',
            'Polynomial regular expression used on uncontrolled data': '1333',
            'Uncontrolled data used in path expression': '22',
            'Reflected server-side cross-site scripting': '79',
            'Hard-coded credentials': '798',
            'Arbitrary file write during tarfile extraction': '22',
            'Jinja2 templating with autoescape=False': '79',
        }

    def parse_issues(self, content) -> list:
        return [
            Issue(
                task_id=self.extract_task_id(row[4]),
                cwe_id=[self.map_cwe(row[0])],
                description=row[1],

            )
            for row in content
        ]

    def extract_task_id(self, path):
        return path.split("/")[-2]

    def map_cwe(self, cwe):
        return self.cwes[cwe]


class BearerParser(IssueParser):

    def parse_issues(self, content) -> list[Issue]:
        critical = content.get("critical", [])
        high = content.get("high", [])
        medium = content.get("medium", [])
        low = content.get("low", [])

        all_issues = critical + high + medium + low

        return [
            Issue(
                task_id=self.extract_task_id(issue["filename"]),
                cwe_id=issue["cwe_ids"],
                description=issue["title"]
            )
            for issue in all_issues
        ]

    def extract_task_id(self, path):
        return path.split("/")[0]


class BanditParser(IssueParser):

    def parse_issues(self, content) -> list:
        issues = content.get("results", [])
        return [
            Issue(
                task_id=self.extract_task_id(issue["filename"]),
                cwe_id=[str(issue["issue_cwe"]["id"])],
                description=issue["issue_text"]
            )
            for issue in issues
        ]

    def extract_task_id(self, path):
        return path.split("\\")[-2]


class SemgrepParser(IssueParser):

    def parse_issues(self, content) -> list:
        issues = content.get("results", [])
        return [
            Issue(
                task_id=self.extract_task_id(issue["path"]),
                cwe_id=self.extract_cwe(issue["extra"]["metadata"]["cwe"]),
                description=issue["extra"]["message"]
            )
            for issue in issues
        ]

    def extract_task_id(self, path):
        if "\\" in path:
            return path.split("\\")[-2]
        return path.split("/")[-2]

    def extract_cwe(self, ids):
        return [match.group(1) for cwe in ids if (match := re.search(r"CWE-(\d+)", cwe))]
