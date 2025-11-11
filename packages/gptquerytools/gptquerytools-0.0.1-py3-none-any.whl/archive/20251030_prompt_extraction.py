# gptquery\tools\extract_citations\prompt.py
"""
gptquery.tools.extract_citations.prompt

Extraction prompt templates for identifying missing citations 
in legal questions, focusing on direct citation matching within 
EU law documents only.

Each prompt template defines a clear contract specifying its 
expected input parameters (DataFrame columns) and the expected 
GPT output format. The prompts are designed to produce precise, 
structured outputs listing missing EU legal citations mentioned 
directly in the text, adhering strictly to EU law sources.

Functions:
- prompt_extract_missing: Detailed extraction prompt with 
  configurable granularity (full, article, paragraph).
- prompt_extract_basic: Simplified prompt using default granularity.

These prompts serve as standardized tools for consistent and 
accurate citation extraction in the broader gptquery pipeline.
"""

from ....processing.utils import requires_columns

# Static system message for extraction
EXTRACTION_SYSTEM_MESSAGE = """
You are a legal citation extraction expert specializing in EUROPEAN UNION LAW ONLY. Your task is to identify ALL missing EU legal citations that are DIRECTLY mentioned in the question but not covered by the existing citations.

CRITICAL INSTRUCTIONS:
1. EXTRACT ONLY EU LEGAL INSTRUMENTS - ignore all national or non-EU sources
2. EXTRACT ONLY DIRECT REFERENCES - do not infer or interpret contextually related citations
3. EXTRACT ALL MISSING CITATIONS - return all directly mentioned but missing citations
4. If ALL directly mentioned citations are already covered, return "NONE"

EU LEGAL INSTRUMENTS INCLUDE:
- EU Treaties (TEU, TFEU)
- EU Regulations
- EU Directives  
- EU Decisions
- EU Court of Justice (CJEU) cases
- EU General Court cases
- EU Commission decisions
- EU Council decisions

DOCUMENT PARTS:
- main (default for articles, most common)
- preamble (for recitals)
- annex (for annexes)
- appendix (for appendices)
- protocol (for protocols)
- convention (for conventions)
- agreement (for agreements)
- amendment (for amendments)

DIRECT REFERENCE EXAMPLES:
- Question mentions "Article 108(3) TFEU" → Extract if not covered
- Question mentions "Regulation 1408/71" → Extract if not covered  
- Question mentions "Case C-119/05" → Extract if not covered
- Question mentions "Directive 77/388/EEC" → Extract if not covered

DO NOT EXTRACT:
- Contextually related provisions not directly mentioned
- Background legal frameworks
- Implied or inferred citations
- National laws or non-EU sources

OUTPUT FORMAT:
Return ALL missing EU citations in this exact format, separated by newlines:
"CELEX_NUMBER,document_part,structural_element"

Examples:
32014R0050,main,body article 47 paragraph 1 subparagraph 2
32014R0050,main,body article 40 paragraph 1 point (e)
12006E108,main,body article 108 paragraph 3
32015R1589,main,preamble recital 15
62019CJ0123,main,body paragraph 25

EXTRACTION RULES:
1. Extract ALL EU legal provisions directly mentioned but missing
2. Use natural language for structural elements (not codes)
3. If no missing EU citations are found, return "NONE"
4. Separate multiple citations with newlines
5. Be conservative - only extract citations you are confident about
6. Normalize ordinal references: Convert "first paragraph" to "paragraph 1", "second indent" to "indent 2"
7. Default to "main" when document part is unclear
8. Include highest granularity mentioned: if question mentions both "Article 4" and "Article 4 paragraph 6", include both

EXAMPLE INPUT/OUTPUT:
Input: "Does Article 49 TFEU conflict with Article 56 TFEU, and how does Case C-280/00 Altmark apply?"
Existing: 12006E018,main,body article 18

Output:
12006E049,main,body article 49
12006E056,main,body article 56
62000CJ0280,main,body paragraph 1

EU FOCUS REMINDER: This is strictly for EU law analysis. Do not extract:
- German BGB, French Code Civil, etc.
- US Supreme Court cases
- International conventions (unless EU-specific implementation)
- National constitutional provisions
- Academic commentary

Focus on accuracy over completeness. It's better to return "NONE" than to extract a non-EU source or inferred citation.

OUTPUT INSTRUCTIONS:
Return exactly the missing citations in the specified format or "NONE".
Do not provide explanations, reasoning, or additional text beyond the citations themselves.
"""

@requires_columns('question_text', 'potential_citations')
def prompt_extract_missing(question_text: str, potential_citations: str, 
                          granularity: str = "full", **kwargs) -> str:
    """
    Create a USER MESSAGE for extraction prompt (system message handled separately).
    
    Required DataFrame columns: question_text, potential_citations
    
    Args:
        question_text (str): The legal question to analyze
        potential_citations (str): Newline-separated existing citations in simple format
        granularity (str): Level of extraction detail ("full", "article", "paragraph")
        **kwargs: Additional parameters (ignored)
    
    Returns:
        str: Formatted user message for GPT (system message handled separately)
        
    Expected GPT Output: Newline-separated list of missing citations or "NONE"
    """
    
    # Handle empty citations case
    if not isinstance(potential_citations, str) or potential_citations.strip() == "":
        existing_citations = "No existing citations provided."
    else:
        existing_citations = f"Existing citations:\n{potential_citations.strip()}"
    
    # Define granularity-specific instructions for user message
    granularity_instructions = {
        "full": "Extract ALL missing EU legal instruments that are directly mentioned in the question but not covered by existing citations. Focus on the legal instrument presence only.",
        
        "article": "Extract ALL missing EU legal instruments AND their specific articles that are directly mentioned in the question but not covered by existing citations. Pay attention to article numbers and references.",
        
        "paragraph": "Extract ALL missing EU legal instruments, articles, AND specific paragraphs/points that are directly mentioned in the question but not covered by existing citations. Pay attention to paragraph numbers, points, and sub-sections."
    }
    
    granularity_instruction = granularity_instructions.get(
        granularity, granularity_instructions["full"]
    )
    
    # Create user message (dynamic content only)
    user_message = f"""QUESTION TO ANALYZE:
{question_text}

{existing_citations}

EXTRACTION TASK:
Identify ALL EU legal instruments, articles, paragraphs, or other EU legal provisions that are DIRECTLY mentioned in the question but NOT adequately covered by the existing citations.

GRANULARITY GUIDANCE:
{granularity_instruction}

TASK: Extract all missing EU citations that are directly mentioned in this legal question."""

    return user_message.strip()


@requires_columns('question_text', 'potential_citations')
def prompt_extract_basic(question_text: str, potential_citations: str, **kwargs) -> str:
    """
    Basic extraction prompt with default granularity.
    
    Required DataFrame columns: question_text, potential_citations
    
    Args:
        question_text (str): The legal question to analyze
        potential_citations (str): Newline-separated existing citations
        **kwargs: Additional parameters (ignored)
    
    Returns:
        str: Formatted user message for GPT
        
    Expected GPT Output: Newline-separated list of missing citations or "NONE"
    """
    return prompt_extract_missing(
        question_text=question_text,
        potential_citations=potential_citations,
        granularity="full",
        **kwargs
    )
