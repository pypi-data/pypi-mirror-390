# gptquery/tools/tool_eulaw_citations/validate_citations/prompts/__init__.py

from .default import prompt_validate_completeness, VALIDATION_SYSTEM_MESSAGE
from .legacy_stdid import prompt_validate_completeness_legacy, VALIDATION_SYSTEM_MESSAGE_LEGACY

prompt_registry = {
    "legacy": {
        "prompt_func": prompt_validate_completeness_legacy,
        "system_message": VALIDATION_SYSTEM_MESSAGE_LEGACY
    },
    "default": {
        "prompt_func": prompt_validate_completeness,
        "system_message": VALIDATION_SYSTEM_MESSAGE
    }
}
