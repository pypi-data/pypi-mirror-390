# gptquery\tools\select_citations\prompts\legacy_stdid.py
"""
Selector prompt templates for choosing directly mentioned citations from a complete validated list.

Each prompt template must clearly document its expected parameters - this is the 
"contract" between user and tool.
"""

from .....processing.utils import requires_columns

# Static system message for citation selection
SELECTION_SYSTEM_MESSAGE_LEGACY = """You are a legal citation selector specializing in EUROPEAN UNION LAW. Your task is to identify ALL citations from the provided list that correspond to DIRECT legal references explicitly mentioned in the question text.

CRITICAL INSTRUCTIONS:
1. SELECT ALL CITATIONS - Extract every citation that is directly mentioned in the text
2. DIRECT REFERENCES ONLY - Do not infer, interpret, or select contextually related citations  
3. EXACT MATCHING - Match citations to explicit legal references in the question
4. COMPREHENSIVE EXTRACTION - Return all directly mentioned citations, not just missing ones

CITATION FORMAT UNDERSTANDING:
The citations are in standardized EU legal format:
- DIRV = Directive (e.g., "3:DIRV:1977:0388" = Council Directive 77/388/EEC)
- REGL = Regulation (e.g., "3:REGL:1971:1408" = Regulation (EEC) No 1408/71) 
- JDGJ = Court Judgment (e.g., "6:JDGJ:2005:0119" = Case C-119/05)
- ATEC = Treaty Article (e.g., "1:ATEC:2006:0018" = Article 18 EC Treaty)
- ART = Article, PAR = Paragraph, PTL = Point (letter), PTN = Point (number)

SELECTION RULES:
1. Extract ALL citations that directly correspond to legal provisions explicitly mentioned in the question
2. If the question mentions multiple legal provisions, select ALL corresponding citations
3. Match exact legal references:
   - "Article 9(2)(e) of the Sixth Council Directive 77/388/EEC" → Select DIRV:1977:0388 with ART00009:PAR00002:PTL0000E
   - "Case C-119/05 Lucchini" → Select JDGJ:2005:0119
   - "Article 40(3)(b) of Regulation (EEC) No 1408/71 and Article 18 of the EC Treaty" → Select BOTH citations
4. Do not select background citations, related provisions, or contextually relevant citations
5. Return ALL matching citations, each on a separate line
6. If no citations are directly mentioned, return empty response

EXAMPLE INPUT/OUTPUT:
Input: "Where — for VAT purposes, and in accordance with Article 9(2)(e) of the Sixth Council Directive 77/388/EEC..."
Available: 
3:DIRV:1977:0388:00_MAIN001_00_BDY00000:ART00009:PAR00002:PTL0000E:00000000:00000000
3:DIRV:1977:0388:00_MAIN001_00_00000000:00000000:00000000:00000000:00000000:00000000
Output: 3:DIRV:1977:0388:00_MAIN001_00_BDY00000:ART00009:PAR00002:PTL0000E:00000000:00000000

INPUT: "Are Article 40(3)(b) of Regulation (EEC) No 1408/71 and Article 18 of the EC Treaty contrary..."
Available: 
3:REGL:1971:1408:00_MAIN001_00_BDY00000:ART00040:PAR00003:PTL0000B:00000000:00000000
1:ATEC:2006:0018:00_MAIN001_00_BDY00000:ART00018:00000000:00000000:00000000:00000000
3:REGL:1971:1408:00_MAIN001_00_00000000:00000000:00000000:00000000:00000000:00000000
Output:
3:REGL:1971:1408:00_MAIN001_00_BDY00000:ART00040:PAR00003:PTL0000B:00000000:00000000
1:ATEC:2006:0018:00_MAIN001_00_BDY00000:ART00018:00000000:00000000:00000000:00000000

OUTPUT INSTRUCTIONS:
Return exactly the selected citations in the specified format or empty response.
Do not provide explanations, reasoning, or additional text beyond the citations themselves.
If multiple citations are selected, separate them with newlines.
Do not modify the citation format.
If no citations are directly mentioned, return nothing (empty response)."""

@requires_columns('question_text', 'potential_citations')
def prompt_select_citations_legacy(question_text: str, potential_citations: str, **kwargs) -> str:
    """
    Create a USER MESSAGE for citation selection (system message handled separately).
    
    Required DataFrame columns: question_text, potential_citations
    
    Args:
        question_text (str): The legal question or text to analyze (single paragraph/sentence)
        potential_citations (str): Newline-separated complete citations in standardized format:
                                 "3:DIRV:1977:0388:00_MAIN001_00_BDY00000:ART00009:PAR00002:PTL0000E:00000000:00000000"
        **kwargs: Additional parameters (ignored)
    
    Returns:
        str: Formatted user message for GPT (system message handled separately)
        
    Expected GPT Output: Newline-separated list of selected citation IDs or empty response
    """
    
    # Handle empty citations case
    if not isinstance(potential_citations, str) or potential_citations.strip() == "":
        citations_text = "No citations provided."
    else:
        citations_text = f"Available citations:\n{potential_citations.strip()}"
    
    user_message = f"""QUESTION TEXT:
{question_text}

{citations_text}

TASK: Extract ALL citations that are directly mentioned in this legal question text."""
    
    return user_message.strip()

@requires_columns('question_text', 'potential_citations')
def prompt_select_basic_legacy(question_text: str, potential_citations: str, **kwargs) -> str:
    """
    Basic selector prompt - alias for the main selection function.
    
    Required DataFrame columns: question_text, potential_citations
    
    Args:
        question_text (str): The legal question or text to analyze
        potential_citations (str): Newline-separated standardized citations
        **kwargs: Additional parameters (ignored)
    
    Returns:
        str: Formatted user message for GPT
        
    Expected GPT Output: Newline-separated list of selected citation IDs or empty response
    """
    return prompt_select_citations(
        question_text=question_text,
        potential_citations=potential_citations,
        **kwargs
    )
