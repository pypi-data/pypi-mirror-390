from abc import ABC, abstractmethod
from pathlib import Path

from data_loader import Task


class Augmentation(ABC):
    """Augmentations are used to modify the prompt that will be provided to a model"""

    def apply(self, task: Task) -> str:
        return task.prompt

    def apply_before(self, task: Task) -> str | None:
        return None

    def apply_after(self, task: Task) -> str | None:
        return None


class SecurityAugmentation(Augmentation):
    """Basic augmentation to add security related information to the prompt"""

    def __init__(self, prefix, suffix=None):
        self.prefix = prefix
        self.suffix = suffix

    def apply_before(self, task: Task) -> str | None:
        return self.prefix

    def apply_after(self, task: Task) -> str | None:
        return self.suffix

    @staticmethod
    def from_template(template: str | Path) -> 'SecurityAugmentation':
        """Read the template file and return a SecurityAugmentation object"""
        # check if the template is a file
        if isinstance(template, Path):
            template_content = template.read_text(encoding='utf-8')
        else:
            template_content = template
        
        if '{PROMPT}' in template_content:
            parts = template_content.split('{PROMPT}')
            prefix = parts[0].strip() if parts[0].strip() else None
            suffix = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
        else:
            prefix = template_content.strip()
            suffix = None
        
        return SecurityAugmentation(prefix, suffix)

