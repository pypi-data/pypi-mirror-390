import os
from dataclasses import dataclass
import json
import logging
import pandas as pd
import csv

from masterframework.data_loader import Task
from masterframework.evaluation.result_parser import Issue
from masterframework.evaluation.security_analyzer import SecurityAnalyzer, analyzer_output_path


@dataclass
class ExperimentResults:
    name: str
    issues: int
    tasks_with_issues: int
    secure_ratio: float
    issues_without_debug: int
    secure_ratio_without_debug: float
    loc: int
    vuln_rate: float
    cwe_count: dict[str, int]
    cwe_ratio: dict[str, float]
    task_issues: dict[str, list[str]]

    def save_results(self, path, config):
        results_list = [config.model.model, self.loc, self.issues, self.tasks_with_issues, self.secure_ratio, self.vuln_rate,
                        self.issues_without_debug,
                        self.secure_ratio_without_debug, self.cwe_count,
                        self.cwe_ratio]

        results = pd.DataFrame(results_list,
                               index=["Model", "LOC", "Issues Found", "Tasks with Issues", "Secure Ratio", "Vulnerability Rate",
                                      "Issues no Debug",
                                      "Secure Ratio no Debug", "CWE Count", "CWE Ratio"]).T

        save_path = os.path.join(path, config.name + ".json")
        with open(save_path, 'w') as f:
            json.dump(results.to_dict(orient="records")[0], f)


def create_metrics(path: str, experiment_name: str, analyzers: list[SecurityAnalyzer],
                   tasks: list[Task]) -> ExperimentResults:
    # Parse and merge results from all analyzers
    task_issues, issues = parse_and_merge(path, analyzers)

    df = pd.DataFrame(task_issues.items(), columns=["task_id", "cwe_ids"]).explode("cwe_ids", ignore_index=True)

    issues_found = len(issues)

    # Exclude debug related CWEs from certain metrics
    # They are present in almost every task and can skew results
    debug_cwe = ["489", "94"]
    issues_without_debug = [issue for issue in issues if all(cwe not in issue.cwe_id for cwe in debug_cwe)]
    tasks_without_debug = [task for task, cwe_list in task_issues.items() if
                           any(all(cwe not in task_cwe for cwe in debug_cwe) for task_cwe in cwe_list)]

    task_with_issues = len(task_issues.keys())

    # Count occurrences of each CWE
    cwe_count = df["cwe_ids"].value_counts()
    secure_ratio = (len(tasks) - task_with_issues) / len(tasks) * 100
    secure_ratio_debug = (len(tasks) - len(tasks_without_debug)) / len(tasks) * 100

    # Count the amount of times a CWE was targeted by a task
    total_cwe_amount = {}
    for task in tasks:
        for cwe in task.cwe_id:
            cwe = cwe.split("-")[1]
            total_cwe_amount[cwe] = total_cwe_amount.get(cwe, 0) + 1

    # Calculate the amount of times a CWE that was targeted by a task was detected
    correct_cwe = {}
    for task in tasks:
        detected_cwes = df[df["task_id"] == str(task.id)]["cwe_ids"].values
        for cwe in task.cwe_id:
            cwe = cwe.split("-")[1]
            if cwe in detected_cwes:
                correct_cwe[cwe] = correct_cwe.get(cwe, 0) + 1

    # CWE occurrence rate (%): amount of times detected / times a CWE was targeted by a task
    cwe_ratio = {}
    for cwe, amount in correct_cwe.items():
        cwe_ratio[cwe] = amount / total_cwe_amount[cwe] * 100

    # Total lines of code
    loc = count_loc(path)

    # Vulnerability rate (Vulnerabilities per 100 lines of code)
    vuln_rate = 0
    if loc > 0:
        vuln_rate = issues_found / loc * 100

    return ExperimentResults(
        name=experiment_name,
        issues=issues_found,
        tasks_with_issues=task_with_issues,
        secure_ratio=secure_ratio,
        issues_without_debug=len(issues_without_debug),
        secure_ratio_without_debug=secure_ratio_debug,
        loc=loc,
        vuln_rate=vuln_rate,
        cwe_count=cwe_count.to_dict(),
        cwe_ratio=cwe_ratio,
        task_issues=task_issues
    )



def save_detailed_results(path, experiment_name, task_issues):
    df = pd.DataFrame(task_issues.items(), columns=["task_id", "cwe_ids"])
    df.rename(columns={"cwe_ids": "cwe_id"}, inplace=True)
    df = df.explode("cwe_id", ignore_index=True)
    df.to_csv(f"{path}/{experiment_name}_all.csv", index=False)


def parse_and_merge(path: str, analyzers: list[SecurityAnalyzer]) -> tuple[dict[str, list[str]], list[Issue]]:
    task_issues = dict()
    issues = []

    for analyzer in analyzers:
        analyzer_path = analyzer_output_path(path, analyzer)
        if not os.path.exists(analyzer_path):
            logging.warning(f"Analyzer results not found at {analyzer_path}, skipping...")
            continue

        content = read_content(analyzer_path)
        parsed_issues = analyzer.get_issue_parser().parse_issues(content)

        for task in parsed_issues:
            cwe_ids = task.cwe_id
            task_cwes = task_issues.get(task.task_id, [])

            for cwe_id in cwe_ids:
                if cwe_id not in task_cwes:
                    task_cwes.append(cwe_id)
                    task_issues[task.task_id] = task_cwes
                    issues.append(task)

    return task_issues, issues


def count_loc(path: str):
    """
    Finds all code files in the path and subfolders and counts the lines of code.
    Comments and blank lines are not counted.
    """
    total_lines = 0
    supported_extensions = {'.py', '.js'}

    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)

            if ext.lower() in supported_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            stripped_line = line.strip()
                            if not stripped_line:
                                continue

                            if ext.lower() == '.py' and stripped_line.startswith('#'):
                                continue
                            elif ext.lower() == '.js' and stripped_line.startswith('//'):
                                continue

                            total_lines += 1

                except (UnicodeDecodeError, IOError) as e:
                    logging.warning(f"Could not read file {file_path}: {e}")
                    continue

    return total_lines


def read_content(path: str):
    if path.endswith(".json"):
        with open(path, 'r') as f:
            return json.load(f)
    elif path.endswith(".csv"):
        # CSV parsing for CodeQL results
        with open(path, 'r') as f:
            content = csv.reader(f, delimiter=",")
            return content
    else:
        raise ValueError(f"Unsupported file format: {path}")
