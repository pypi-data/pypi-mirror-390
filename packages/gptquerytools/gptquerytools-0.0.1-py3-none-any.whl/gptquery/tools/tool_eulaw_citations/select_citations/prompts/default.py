# gptquery\gptquery\tools\select_citations\prompts\default.py
"""
Selector prompt templates for choosing directly mentioned citations from a complete validated list.

Each prompt template must clearly document its expected parameters - this is the 
"contract" between user and tool.
"""

from .....processing.utils import requires_columns

# Static system message for citation selection with new simplified format
SELECTION_SYSTEM_MESSAGE = """You are a legal citation selector specializing in EUROPEAN UNION LAW. Your task is to identify ALL citations from the provided list that correspond to DIRECT legal references explicitly mentioned in the question text.

CRITICAL INSTRUCTIONS:
1. SELECT ALL CITATIONS - Extract every citation that is directly mentioned in the text
2. DIRECT REFERENCES ONLY - Do not infer, interpret, or select contextually related citations  
3. EXACT MATCHING - Match citations to explicit legal references in the question
4. COMPREHENSIVE EXTRACTION - Return all directly mentioned citations.

CITATION FORMAT UNDERSTANDING:
The citations are in simplified EU legal format:
- Format: CELEX_NUMBER,document_part,structural_element
- Examples: 
  * 31977L0388,main,body article 9 paragraph 2 point (e)
  * 62005CJ0119,main,body paragraph 1  
  * 12008E018,main,body article 18
  * 31971R1408,main,body article 40 paragraph 3 point (b)

CELEX NUMBER PATTERNS:
- Directives: 3YYYYLNNNN (e.g., 31977L0388 = Council Directive 77/388/EEC)
- Regulations: 3YYYYRNNNN (e.g., 31971R1408 = Regulation (EEC) No 1408/71)  
- Court Judgments: 6YYYYCJNNNN (e.g., 62005CJ0119 = Case C-119/05)
- Treaty Articles: 1YYYYETXT (e.g., 12008E018 = Article 18 EC Treaty)

SELECTION RULES:
1. Extract ALL citations that directly correspond to legal provisions explicitly mentioned in the question
2. If the question mentions multiple legal provisions, select ALL corresponding citations
3. Match exact legal references:
   - "Article 9(2)(e) of the Sixth Council Directive 77/388/EEC" → Select 31977L0388,main,body article 9 paragraph 2 point (e)
   - "Case C-119/05 Lucchini" → Select 62005CJ0119,main,body paragraph 1
   - "Article 40(3)(b) of Regulation (EEC) No 1408/71 and Article 18 of the EC Treaty" → Select BOTH citations
4. Do not select background citations, related provisions, or contextually relevant citations
5. Return ALL matching citations, each on a separate line
6. If no citations are directly mentioned, return empty response

EXAMPLE INPUT/OUTPUT:
Input: "Where — for VAT purposes, and in accordance with Article 9(2)(e) of the Sixth Council Directive 77/388/EEC..."
Available: 
31977L0388,main,body article 9 paragraph 2 point (e)
31977L0388,main,body article 1
Output: 31977L0388,main,body article 9 paragraph 2 point (e)

Input: "Are Article 40(3)(b) of Regulation (EEC) No 1408/71 and Article 18 of the EC Treaty contrary..."
Available: 
31971R1408,main,body article 40 paragraph 3 point (b)
12008E018,main,body article 18
31971R1408,main,body article 1

Output:
31971R1408,main,body article 40 paragraph 3 point (b)
12008E018,main,body article 18

INPUT: "Does Community law preclude the application of national provisions in tax matters?"
Available:
12008E018,main,body article 18
31977L0388,main,body article 9
Output: (empty - no specific EU instruments directly mentioned)

OUTPUT INSTRUCTIONS:
Return exactly the selected citations in the specified format or empty response.
Do not provide explanations, reasoning, or additional text beyond the citations themselves.
If multiple citations are selected, separate them with newlines.
Do not modify the citation format.
If no citations are directly mentioned, return nothing (empty response)."""

@requires_columns('question_text', 'potential_citations')
def prompt_select_citations(question_text: str, potential_citations: str, **kwargs) -> str:
    """
    Create a USER MESSAGE for citation selection using simplified format (system message handled separately).
    
    Required DataFrame columns: question_text, potential_citations
    
    Args:
        question_text (str): The legal question or text to analyze (single paragraph/sentence)
        potential_citations (str): Newline-separated citations in simplified format:
                                 "31977L0388,main,body article 9 paragraph 2 point e"
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

TASK: SELECT ALL citations that are directly mentioned in this legal question text."""
    
    return user_message.strip()

@requires_columns('question_text', 'potential_citations')
def prompt_select_basic(question_text: str, potential_citations: str, **kwargs) -> str:
    """
    Basic selector prompt using simplified format - alias for the main selection function.
    
    Required DataFrame columns: question_text, potential_citations
    
    Args:
        question_text (str): The legal question or text to analyze
        potential_citations (str): Newline-separated simplified citations
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
