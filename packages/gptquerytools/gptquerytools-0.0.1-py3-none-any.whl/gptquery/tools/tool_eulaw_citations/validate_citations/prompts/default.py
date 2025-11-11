# gptquery/tools/tool_eulaw_citations/validate_citations/prompts/default.py

"""
Simplified validation prompt templates for checking citation completeness with simple format input.
Parallel version using simplified citation format: "32002F0584,main,body article 4 paragraph 6"

Each prompt template must clearly document its expected parameters - this is the 
"contract" between user and tool.
"""

from .....processing.utils import requires_columns

# Static system message for validation message

VALIDATION_SYSTEM_MESSAGE = """
You are a legal citation completeness validator specializing in EUROPEAN UNION LAW. Your task is to determine whether the provided citations are all and the same as those mentioned in the provided question text.

CRITICAL INSTRUCTIONS:
1. FOCUS ONLY ON EU LEGAL INSTRUMENTS - ignore national or non-EU sources
2. VALIDATE ONLY DIRECT REFERENCES - check if directly mentioned legal provisions are covered  
3. ANSWER ONLY "complete" OR "incomplete" - no explanations needed

CITATION FORMAT UNDERSTANDING:
The citations are in simplified EU legal format:
- Format: "CELEX_NUMBER,document_part,structural_element"
- Examples:
  * 31977L0388,main,body article 9 paragraph 2 point (e)
  * 62005CJ0119,main,body paragraph 1
  * 12006E018,main,body article 18
  * 32002F0584,main,body article 4 paragraph 6

VALIDATION RULES:
1. Identify ONLY the EU legal provisions explicitly mentioned by name in the question
2. For each mentioned provision, check if there is a corresponding citation:
   - Same legal instrument (same CELEX number)
   - Same article number if specified
   - Same paragraph/point if granularity requires it
3. If ALL explicitly mentioned provisions have matching citations → "complete"
4. If ANY explicitly mentioned provision lacks a matching citation → "incomplete"
5. Ignore national law references, background context, and implied provisions

SPECIAL CASE - NO CITATIONS PROVIDED:
When no citations are provided, determine if citations are actually needed:
1. If the question mentions SPECIFIC EU instruments with numbers/dates or UNAMBIGUOUS references → "incomplete"
   - Examples: "Article 49 TFEU", "the Charter", "the VAT Directive", "Case C-119/05", "Directive 2006/112/EC"
2. If the question discusses GENERAL concepts or AMBIGUOUS references → "complete"
   - Examples: "Community law", "EU law", "the Treaties", "fundamental rights", "European law principles"

EXAMPLES OF CORRECT VALIDATION:

Question: "Article 9(2)(e) of Directive 77/388/EEC requires..."
Citation: 31977L0388,main,body article 9 paragraph 2 point (e)
Result: complete

Question: "Case C-119/05 Lucchini and Article 18 EC Treaty..."
Citations: 
62005CJ0119,main,body paragraph 1
12006E018,main,body article 18
Result: complete

Question: "Article 4(3)(b) of Regulation 1408/71 and Article 18 EC Treaty..."
Citations: 31971R1408,main,body article 40 paragraph 3 point (b)
Result: incomplete (missing Article 18 EC Treaty)

NO CITATIONS EXAMPLES:

Question: "Does Article 49 TFEU conflict with the Services Directive?"
Citations: No citations provided
Result: incomplete (specific instruments mentioned but not cited)

Question: "What are the general principles of EU law regarding proportionality?"
Citations: No citations provided  
Result: complete (general EU law principles, no specific instruments mentioned)

Question: "How does the Charter protect fundamental rights?"
Citations: No citations provided
Result: incomplete (the Charter is unambiguous reference to Charter of Fundamental Rights)

Question: "Do the Treaties establish free movement principles?"
Citations: No citations provided
Result: complete (the Treaties is ambiguous - could be TEU, TFEU, protocols, etc.)

GRANULARITY EXAMPLES:

Input: "Where for VAT purposes, and in accordance with Article 9(2)(e) of the Sixth Council Directive 77/388/EEC..."
Citations: 31977L0388,main,body article 9 paragraph 2 point (e)
Output: complete

Input: "Are Article 4(3)(b) of Regulation EEC No 1408/71 and Article 18 of the EC Treaty contrary..."
Citations: 31971R1408,main,body article 40 paragraph 3 point (b)
Output: incomplete (missing Article 18 EC Treaty)

Input: "Does Community law preclude the application of national law in tax disputes?"
Citations: 12008E018,main,body article 18
Output: complete (general Community law principle covered)

OUTPUT INSTRUCTIONS:
Return exactly one word: "complete" or "incomplete"
Do not provide explanations, reasoning, or additional text.
Base your assessment on whether the citations adequately cover the EU legal provisions directly mentioned in the question.
"""

@requires_columns('question_text', 'potential_citations')
def prompt_validate_completeness(question_text: str, potential_citations: str, 
                                 granularity: str = "full", **kwargs) -> str:
    """
    Create a USER MESSAGE for simplified format validation prompt (system message handled separately).
    
    Required DataFrame columns: question_text, potential_citations
    
    Args:
        question_text (str): The legal question to analyze
        potential_citations (str): Newline-separated citations in simplified format
        granularity (str): Validation granularity ("full", "article", "paragraph")
        system_message (str): Custom system message (optional, uses default if empty)
        **kwargs: Additional parameters (ignored)
    
    Returns:
        str: Formatted user message for GPT (system message handled separately)
        
    Expected GPT Output: "complete" or "incomplete"
    """
    
    # Handle empty or missing citations safely
    if not isinstance(potential_citations, str) or potential_citations.strip() == "":
        citations_text = "No EU citations provided."
    else:
        citations_text = f"Citations to validate:\n{potential_citations.strip()}"
    
    # Define granularity-specific instructions for user message
    granularity_instructions = {
        "full": "Validate if the citations cover all EU legal instruments directly mentioned in the question. Focus on whether the legal instruments themselves are present.",
        
        "article": "Validate if the citations cover all EU legal instruments AND specific articles directly mentioned in the question. Pay attention to article numbers and references.",
        
        "paragraph": "Validate if the citations cover all EU legal instruments, articles, AND specific paragraphs/points directly mentioned in the question. Pay attention to paragraph numbers, points, and sub-sections."
    }
    
    granularity_instruction = granularity_instructions.get(
        granularity, granularity_instructions["full"]
    )
    
    # Create user message (dynamic content only)
    user_message = f"""QUESTION TO ANALYZE:
{question_text}

{citations_text}

VALIDATION TASK:
Determine if the provided citations adequately cover ALL EU legal provisions that are DIRECTLY mentioned in the question and necessary to answer it.

GRANULARITY GUIDANCE:
{granularity_instruction}

TASK: Validate citation completeness for this EU legal question."""

    return user_message.strip()

@requires_columns('question_text', 'potential_citations')
def prompt_validate_basic(question_text: str, potential_citations: str, **kwargs) -> str:
    """
    Basic simplified validation prompt with default granularity.
    
    Required DataFrame columns: question_text, potential_citations
    
    Args:
        question_text (str): The legal question to analyze
        potential_citations (str): Newline-separated simplified citations
        **kwargs: Additional parameters (ignored)
    
    Returns:
        str: Formatted user message for GPT
        
    Expected GPT Output: "complete" or "incomplete"
    """
    return prompt_validate_completeness(
        question_text=question_text,
        potential_citations=potential_citations,
        granularity="full",
        **kwargs
    )
