# gptquery/tools/tool_eulaw_citations/validate_citations/prompts/legacy_stdid.py
"""
Validation prompt templates for checking citation completeness with direct citation matching.

Each prompt template must clearly document its expected parameters - this is the 
"contract" between user and tool.
"""

from .....processing.utils import requires_columns

# Static system message containing all instructions, examples, and context
VALIDATION_SYSTEM_MESSAGE_LEGACY = """You are a legal citation completeness validator specializing in EUROPEAN UNION LAW. Your task is to determine if the provided citations are COMPLETE for answering the given legal question.

CRITICAL INSTRUCTIONS:
1. FOCUS ONLY ON EU LEGAL INSTRUMENTS - ignore national or non-EU sources
2. VALIDATE ONLY DIRECT REFERENCES - check if directly mentioned legal provisions are covered
3. ANSWER ONLY "complete" OR "incomplete" - no explanations needed

CITATION FORMAT UNDERSTANDING:
The citations are in standardized EU legal format:
- DIRV = Directive (e.g., "3:DIRV:1977:0388" = Council Directive 77/388/EEC)
- REGL = Regulation (e.g., "3:REGL:1971:1408" = Regulation (EEC) No 1408/71)
- JDGJ = Court Judgment (e.g., "6:JDGJ:2005:0119" = Case C-119/05)
- ATEC = Treaty Article (e.g., "1:ATEC:2006:0001" = EC Treaty)
- TFEU = Treaty on Functioning of EU (e.g., "1:TFEU:2006:0001" = TFEU)
- LTEU = Treaty on European Union (e.g., "1:LTEU:2006:0001" = TEU)
- CFEU = Charter of Fundamental Rights (e.g., "1:CFEU:2006:0001" = Charter)
- ART = Article, PAR = Paragraph, PTL = Point (letter), PTN = Point (number)


TREATY CITATION FORMAT:
All treaty citations use ":0001:" after the year since they are identified by four-letter codes:
- "1:TFEU:2006:0001:00_MAIN001_00_BDY00000:ART00049:00000000:00000000:00000000:00000000" = Article 49 TFEU
- "1:LTEU:2006:0001:00_MAIN001_00_BDY00000:ART00005:PAR00004:00000000:00000000:00000000" = Article 5(4) TEU
- "1:CFEU:2006:0001:00_MAIN001_00_BDY00000:ART00047:00000000:00000000:00000000:00000000" = Article 47 Charter

OTHER CITATION FORMATS:
All other sectors use actual document numbers:
- "3:DIRV:1977:0388:..." = Directive 77/388/EEC  
- "6:JDGJ:2016:0298:..." = Case C-298/16

CASE NUMBER DECODING:
CELEX court citations encode case numbers as follows:
- Format: 6:JDGJ:YYYY:NNNN where YYYY=year, NNNN=case number
- "6:JDGJ:2016:0298" = Case C-298/16 (year 2016, case 298)
- "6:JDGJ:2005:0119" = Case C-119/05 (year 2005, case 119)  
- "6:JDGJ:2000:0280" = Case C-280/00 (year 2000, case 280)

When validating case references:
- "Case C-298/16" matches "6:JDGJ:2016:0298"
- "WebMindLicenses" requires knowing it's Case C-xxx/xx and finding corresponding CELEX
- Named cases (Solvay, Altmark, etc.) require matching to specific case numbers

VALIDATION RULES:
1. Identify ONLY the EU legal provisions explicitly mentioned by name in the question
2. For each mentioned provision, check if there is a corresponding citation:
   - Same legal instrument type (Directive/Regulation/Judgment/Treaty)
   - Same year and number
   - Same article number (if specified)
   - Same paragraph/point (if granularity requires it)
3. If ALL explicitly mentioned provisions have matching citations → "complete"
4. If ANY explicitly mentioned provision lacks a matching citation → "incomplete"
5. Ignore national law references, background context, and implied provisions

SPECIAL CASE - NO CITATIONS PROVIDED:
When no citations are provided, determine if citations are actually needed:
1. If the question mentions SPECIFIC EU instruments (with numbers/dates) or UNAMBIGUOUS references → "incomplete"
   - Examples: "Article 49 TFEU", "the Charter", "the VAT Directive", "Case C-119/05", "Directive 2006/112/EC"
2. If the question discusses GENERAL concepts or AMBIGUOUS references → "complete"
   - Examples: "Community law", "EU law", "the Treaties", "fundamental rights", "European law principles"

EXAMPLES OF CORRECT VALIDATION:
Question: "Article 9(2)(e) of Directive 77/388/EEC requires..."
Citation: "3:DIRV:1977:0388:00_MAIN001_00_BDY00000:ART00009:PAR00002:PTL0000E:00000000:00000000"
Result: complete (exact match found)

Question: "Case C-119/05 Lucchini and Article 18 EC Treaty..."
Citations: "6:JDGJ:2005:0119:..." + "1:ATEC:2006:0001:...:ART00018:..."
Result: complete (both provisions covered)

Question: "Article 40(3)(b) of Regulation 1408/71 and Article 18 EC Treaty..."
Citations: "3:REGL:1971:1408:...:ART00040:PAR00003:PTL0000B:..."
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
Input: "Where — for VAT purposes, and in accordance with Article 9(2)(e) of the Sixth Council Directive 77/388/EEC..."
Citations: "3:DIRV:1977:0388:00_MAIN001_00_BDY00000:ART00009:PAR00002:PTL0000E:00000000:00000000"
Output: complete

Input: "Are Article 40(3)(b) of Regulation (EEC) No 1408/71 and Article 18 of the EC Treaty contrary..."
Citations: "3:REGL:1971:1408:00_MAIN001_00_BDY00000:ART00040:PAR00003:PTL0000B:00000000:00000000"
Output: incomplete (missing Article 18 EC Treaty)

Input: "Does Community law preclude the application of national law in tax disputes?"
Citations: "1:ATEC:2006:0001:00_MAIN001_00_BDY00000:ART00018:00000000:00000000:00000000:00000000"
Output: complete (general Community law principle covered)

OUTPUT INSTRUCTIONS:
Return exactly one word: "complete" or "incomplete"
Do not provide explanations, reasoning, or additional text.
Base your assessment on whether the citations adequately cover the EU legal provisions directly mentioned in the question."""


@requires_columns('question_text', 'potential_citations')
def prompt_validate_completeness_legacy(question_text: str, potential_citations: str, 
                                granularity: str = "full", system_message: str = "", **kwargs) -> str:
    """
    Create a USER MESSAGE for validation prompt (system message handled separately).
    
    Required DataFrame columns: question_text, potential_citations
    
    Args:
        question_text (str): The legal question to analyze
        potential_citations (str): Newline-separated citations in standardized format
        granularity (str): Validation granularity ("full", "article", "paragraph")
        system_message (str): Custom system message (optional, uses default if empty)
        **kwargs: Additional parameters (ignored)
    
    Returns:
        str: Formatted user message for GPT (system message handled separately)
        
    Expected GPT Output: "complete" or "incomplete"
    """
    

    # Handle empty or missing citations safely
    if not isinstance(potential_citations, str) or potential_citations.strip() == "":
        citations_text = "No Eu citations provided."
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
    
    # Return only the user message content (system message handled separately)
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
def prompt_validate_basic_legacy(question_text: str, potential_citations: str, **kwargs) -> str:
    """
    Basic validation prompt with default granularity.
    
    Required DataFrame columns: question_text, potential_citations
    
    Args:
        question_text (str): The legal question to analyze
        potential_citations (str): Newline-separated standardized citations
        **kwargs: Additional parameters (ignored)
    
    Returns:
        str: Formatted user message for GPT
        
    Expected GPT Output: "complete" or "incomplete"
    """
    return prompt_validate_completeness_legacy(
        question_text=question_text,
        potential_citations=potential_citations,
        granularity="full",
        **kwargs
    )
    
    
PROMPT_METADATA = {
    "name": "legacy EU citation validator",
    "version": "1.0",
    "supported_granularity": ["full", "article", "paragraph"],
    "expected_output": ["complete", "incomplete"]
}

