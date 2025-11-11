# gptquery\tools\tool_text_extraction\extract_authornames\prompts\default.py

"""
EXTRACTOR prompt template for getting author names from text data.

Each prompt template must clearly document its expected parameters - this is the 
"contract" between user and tool.
"""

from .....processing.utils import requires_columns

# Static system message for extraction
EXTRACTION_SYSTEM_MESSAGE = """
You are an information extraction expert specializing in extracting author names from text data.

CRITICAL INSTRUCTIONS:
1. Extract the full name of each author, including first name and all last names.
2. Extract multiple authors if listed, in the order they appear.
3. If no author is present in the text, return "NONE".
4. Capitalize the first letter of each name, lowercase the remaining letters (name-case capitalization).
5. Do not provide explanations, reasoning, or any additional text beyond the author names.

OUTPUT FORMAT:
- Author names separated by commas.
- Example one: Katarzyna Zieleskiewicz,Bartlomiej Kurcz
- Example two: Marc Blanquet
"""


@requires_columns("first_page_text")
def prompt_extract_author(first_page_text: str, **kwargs) -> str:
    """
    Create a USER MESSAGE for simplified format validation prompt (system message handled separately).
    
    Required DataFrame columns: question_text, potential_citations
    
    Args:
        first_page_text (str): Text where the author is listed. 
        **kwargs: Additional parameters (ignored)    
    Returns:
        str: Formatted user message for GPT (system message handled separately)
        
    Expected GPT Output: "First name, Last name"
    """ 
    # Create user message (dynamic content only)
    user_message = f"""TEXT TO ANALYZE:
{first_page_text}

EXTRACTION TASK: Extract the full name of the author(s)."""

    return user_message.strip()
    