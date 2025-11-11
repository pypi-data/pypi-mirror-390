#  gptquery/gptquery/tools/tool_eulaw_citations/select_citations/prompts/__init__.py

# PAGE Deliveratly left blank
from .default import prompt_select_citations, SELECTION_SYSTEM_MESSAGE
from .legacy_stdid import prompt_select_basic_legacy, SELECTION_SYSTEM_MESSAGE_LEGACY

prompt_registry = {
    "legacy": {
        "prompt_func": prompt_select_basic_legacy,
        "system_message": SELECTION_SYSTEM_MESSAGE_LEGACY
    },
    "default": {
        "prompt_func": prompt_select_citations,
        "system_message": SELECTION_SYSTEM_MESSAGE
    }
}
