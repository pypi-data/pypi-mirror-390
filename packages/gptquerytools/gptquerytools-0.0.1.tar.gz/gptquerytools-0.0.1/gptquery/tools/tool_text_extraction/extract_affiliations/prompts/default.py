# gptquery\tools\tool_text_extraction\extract_authornames\prompts\default.py

"""
EXTRACTOR prompt template for getting authors affiliations from text data.

Each prompt template must clearly document its expected parameters - this is the 
"contract" between user and tool.
"""

from .....processing.utils import requires_columns


# Static system message for extraction
EXTRACTION_SYSTEM_MESSAGE = """
You are an information extraction expert specializing in extracting academic or organizational author affiliations from text.

# Task
Extract only institution or organization names that appear as author credentials or bylines—typically found immediately after author names, in author footnotes, or in "by" statements.

# Critical Rules
1. Extract ONLY institutions directly linked to authors as their professional affiliation.
2. Look for affiliations in these locations:
   - After author names (e.g., "John Smith, Harvard University")
   - In bylines (e.g., "By Jane Doe, Lecturer in Laws, University College London")
   - In author footnotes or credentials sections
3. DO NOT extract organizations that are merely mentioned in the text content, even if they are government bodies, courts, or commissions.
4. DO NOT extract: faculties, departments, research groups, job titles, degrees, addresses, or office locations.
5. Include only: universities, research institutes, government ministries, law firms, courts (including international and supranational courts), or organizations when they appear as the author's institutional home.
6. If no author affiliations are found, return "NONE".
7. Standardize names: 
   - Use modern spelling (Leyden → Leiden)
   - Translate well-known institutions to English (Università di Bologna → University of Bologna, Rijksuniversiteit Groningen → University of Groningen, Universität Wien → University of Vienna)

# Output Format
Institutions separated by semicolons, or "NONE"

# Examples
Text: "By E.D. Brown, Lecturer in Laws, University College London"
Output: University College London

Text: "Professor of European Law, Rijksuniversiteit Groningen"
Output: University of Groningen

Text: "Professor of European Law, Rijksuniversiteit Groningen; Barrister, Cleary Gottlieb Steen & Hamilton"
Output: University of Groningen; Cleary Gottlieb Steen & Hamilton

Text: "The Commission approved the decision..."
Output: NONE

Text: "Case brought by plaintiffs against the E.E.C. Commission..."
Output: NONE

Text: "Judge at the Court of Justice of the European Communities"
Output: Court of Justice of the European Communities
"""

@requires_columns("first_page_text")
def prompt_extract_affiliations(first_page_text: str, **kwargs) -> str:
    """
    Create a USER MESSAGE for extracting institutions/organizations from a text.
    System message handles the detailed instructions; this generates only the dynamic content.

    Required DataFrame columns: first_page_text

    Args:
        first_page_text (str): Text where the affiliations are listed.
        **kwargs: Additional parameters (ignored)

    Returns:
        str: Formatted user message for GPT (system message handled separately)
        
    Expected GPT Output: "Institution 1, Institution 2, Institution 3"
    """
    # Create user message (dynamic content only)
    user_message = f"""TEXT TO ANALYZE:
{first_page_text}

EXTRACTION TASK: Extract all institutions or organizations associated with the authors. 
Include universities, ministries, commissions, research institutes, or other organizations. 
Separate each institution with a comma. Ignore faculties, departments, research groups, addresses, or individual offices."""

    return user_message.strip()

