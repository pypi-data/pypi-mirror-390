# gptquery\tools\tool_text_extraction\extract_authornames\__init__.py
from .task import run_extract_authors
from .prompts.default import prompt_extract_author

__all__ = ['run_extract_authors', 'prompt_extract_author']
