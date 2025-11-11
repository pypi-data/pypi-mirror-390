# /gptquery\tools\tool_text_extraction\extract_authornames\prompts\task.py

"""
Validation task execution with external throttling and robust error handling.
"""
import pandas as pd
from typing import Optional, Callable, List, Any
from ....core.client import GPTClient, RateLimitError, APIError, AuthenticationError, ModelValidationError
from ....processing.utils import validate_required_columns
from .prompts.default import EXTRACTION_SYSTEM_MESSAGE

from .log import ExtractAuthornamesLogger

# Create logger instance
logger = ExtractAuthornamesLogger()

@logger.log_execution
def run_extract_authors(df: pd.DataFrame, 
                        prompt_func: Callable, 
                        api_key: str, 
                        model: str,
                        provider: str, 
                        throttler: Optional[Any] = None,
                        progress: bool = True,
                        system_message: str = "",
                        **kwargs) -> pd.DataFrame:
    """
    Extracts author names from text data in a DataFrame using a GPT-based extraction model.

    This function iterates over each row of the input DataFrame, generates a prompt using
    `prompt_func`, and sends it to the GPT client for extraction. Results are processed 
    into a list of author names and appended as a new column `author_names`.

    Args:
        df (pd.DataFrame): Input DataFrame containing the text data to extract authors from.
        prompt_func (Callable): Function that generates the user message for each row.
        api_key (str): API key for the GPT provider.
        throttler (Optional[Any], default=None): Optional throttler instance to limit request rate.
        model (str, default="gpt-4.1-mini"): GPT model to use for extraction.
        provider (str, default="openai"): GPT provider name.
        progress (bool, default=True): If True, prints progress updates.
        system_message (str, default=""): Static system message for the GPT prompt; 
                                          if empty, uses default extraction system message.
        **kwargs: Additional keyword arguments passed to `prompt_func` or the GPT client
                  (e.g., max_tokens).

    Returns:
        pd.DataFrame: A copy of the input DataFrame with an added column `author_names`,
                      where each cell contains a list of extracted author names or an 
                      empty list if no authors were found. If extraction fails, the list
                      contains ["ERROR"].
    """
    
    # Validate required columns before starting
    validate_required_columns(df, prompt_func)
    
    # Import only when needed
    if throttler is None:
        from ....processing.throttling import SimpleThrottler
        throttler = SimpleThrottler(rpm=50) # type: ignore
    
    # Initialize multi-provider client
    client = GPTClient(api_key, model, provider)
    
    # Prepare results
    results = []
    total_rows = len(df)
    
    if progress:
        print(f"Starting extraction of {total_rows} rows using {provider}...")
    
    # Process each row
    for i, (idx, row) in enumerate(df.iterrows()):
        try:
            # Apply throttling
            if throttler:
                throttler.wait_if_needed()
            
            # Generate user message only (dynamic content)
            user_message = prompt_func(**row.to_dict(), **kwargs)
            
            # Make API call with system/user message separation
            result = client.extract(         # noqa: F841
                text=user_message,           # User message (dynamic prompt data)
                prompt=system_message,       # System message (static instructions)
                model=model,
                temperature=0.0,             # Deterministic for extraction
                max_tokens=kwargs.get('max_tokens', 10000)  # Extraction may need more tokens
            )
            # ADD THIS - Process the result
            processed_result = _process_extraction_result(result)
            results.append(processed_result)
            
        except RateLimitError:
            # Default strategy for rate limits - return ERROR list
            results.append(["ERROR"])
            if progress:
                print(f"Rate limit hit at row {i+1} ({provider})")
                
        except (APIError, AuthenticationError, ModelValidationError):
            # Other errors - return ERROR list
            results.append(["ERROR"])
            if progress:
                print(f"Error at row {i+1} ({provider})")
                
        except Exception:
            # Unexpected errors - return ERROR list
            results.append(["ERROR"])
            if progress:
                print(f"Unexpected error at row {i+1} ({provider})")
        
        # Progress updates every 10%
        if progress and (i + 1) % max(1, total_rows // 10) == 0:
            percentage = ((i + 1) / total_rows) * 100
            print(f"Progress: {i+1}/{total_rows} ({percentage:.1f}%)")
    
    # Create result DataFrame
    result_df = df.copy()
    result_df['author_names'] = results
    
    if progress:
        successful_extractions = sum(1 for r in results if r and r != ["ERROR"])
        empty_results = sum(1 for r in results if r == [])
        error_count = sum(1 for r in results if r == ["ERROR"])
        
        print(f"\nExtraction completed using {provider}:")
        print(f"  Successful extractions: {successful_extractions}")
        print(f"  No authors found: {empty_results}")
        print(f"  Errors: {error_count}")
        print(f"  Total rows processed: {total_rows}")

    return result_df


def _process_extraction_result(result: str) -> List[str]:
    """
    Processes a raw extraction string into a list of author names.

    Args:
        result (str): Raw string from the extraction model, e.g.,
                      "Katarzyna Zieleskiewicz,Bartlomiej Kurcz"

    Returns:
        List[str]: List of author names.
    """
    # Handle the "NONE" case
    if not result or result.strip().upper() == "NONE":
        return []

    # Split by comma and strip whitespace from each name
    authors = [name.strip() for name in result.split(",") if name.strip()]
    
    return authors


def run_extract_authors_basic(df: pd.DataFrame, 
                              api_key: str, 
                              provider: str = "openai",
                              model: str = "gpt-4.1-mini",
                              system_message: str = EXTRACTION_SYSTEM_MESSAGE, 
                              **kwargs) -> pd.DataFrame:
    """
    Convenience function for basic selection with default prompt and multi-provider support.
    
    Args:
        df: DataFrame with 'question_text' and 'potential_citations' columns
        api_key: API key for the chosen provider
        provider: AI provider to use ("openai" or "perplexity")
        model: Model to use (provider-specific, defaults to gpt-4o/sonar-pro)
        **kwargs: Additional parameters for run_select
        
    Returns:
        DataFrame with 'selected_citations' column containing lists of citation strings
    """
    from .prompts.default import prompt_extract_author
    
    # Auto-adjust model for provider if using default
    if model == "gpt-4.1-mini" and provider == "perplexity":
        model = "sonar-pro" # Sensible Perplexity default
    
    return run_extract_authors(
        df=df,
        prompt_func=prompt_extract_author,
        api_key=api_key,
        provider=provider,
        model=model,
        system_message=system_message,
        **kwargs
    )
