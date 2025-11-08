import os
import re

def remove_comments(code, language):
    if language == "python":
        return re.sub(r'(#.*|\'\'\'.*?\'\'\'|\"\"\".*?\"\"\")', '', code)
    else:
        return re.sub(r'(//.*|/\*.*?\*/)', '', code)


def file_language(path: str):
    if path.endswith(".py"):
        return "python"
    elif path.endswith(".js"):
        return "javascript"
    else:
        return None

def file_ending(language):
    return "py" if language == "python" else "js"


