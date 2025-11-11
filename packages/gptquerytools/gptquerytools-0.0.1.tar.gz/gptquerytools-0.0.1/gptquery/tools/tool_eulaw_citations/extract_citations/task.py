# gptquery/gptquery/tools/tool_eulaw_citations/extract_citations/task.py
"""
Execution of extraction tasks for missing legal citations using
list-based output with direct citation matching.

Provides functions to run extraction on pandas DataFrames with
multi-provider AI model support (OpenAI, Perplexity), including
rate limiting and error handling via throttling strategies.

Core functions:
- run_extract: Execute extraction with custom prompt functions,
  throttling, and provider/model flexibility.
- run_extract_basic: Convenience wrapper for basic extraction
  using the default prompt template and typical parameters.

Outputs:
- DataFrame with new 'missing_citations' column containing lists
  of extracted citation strings or error indicators.

Includes internal utilities to parse and standardize GPT extraction
results, and detailed progress and error reporting.
"""
import pandas as pd
from typing import Optional, Callable, Any, List
from ....core.client import GPTClient, RateLimitError, APIError, AuthenticationError, ModelValidationError
from ....processing.utils import validate_required_columns
from .log import ExtractCitationsLogger

# Create logger instance
logger = ExtractCitationsLogger()

@logger.log_execution
def run_extract(df: pd.DataFrame, prompt_func: Callable, api_key: str, 
                throttler: Optional[Any] = None, model: str = "gpt-4.1-mini",
                provider: str = "openai", progress: bool = True, 
                system_message: str = "", **kwargs) -> pd.DataFrame:
    """
    Run extraction task on DataFrame with system message separation.
    
    Args:
        system_message: Custom system message (uses default if empty)
        df: DataFrame with required columns (defined by prompt_func)
        prompt_func: Prompt template function to use
        api_key: API key for the chosen provider
        throttler: Throttling strategy (defaults to SimpleThrottler)
        model: Model to use (provider-specific)
        provider: AI provider to use ("openai" or "perplexity")
        progress: Whether to print progress updates
        **kwargs: Additional parameters passed to prompt_func
        
    Returns:
        DataFrame with new 'missing_citations' column containing list of citation strings
        
    Raises:
        ValueError: If required columns are missing or invalid provider
        AuthenticationError: If API key is invalid
        ModelValidationError: If model is invalid for the provider
    """
    
     # Import system message if not provided
    if not system_message:
        from .prompts.default import EXTRACTION_SYSTEM_MESSAGE
        system_message = EXTRACTION_SYSTEM_MESSAGE
    
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
                text=user_message,           # User message (dynamic question data)
                prompt=system_message,       # System message (static instructions)
                model=model,
                temperature=0.0,             # Deterministic for extraction
                max_tokens=kwargs.get('max_tokens', 5000)  # Extraction may need more tokens
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
    result_df['missing_citations'] = results
    
    if progress:
        successful_extractions = sum(1 for r in results if r != ["ERROR"] and len(r) > 0)
        empty_results = sum(1 for r in results if r == [])
        error_count = sum(1 for r in results if r == ["ERROR"])
        single_missing = sum(1 for r in results if len(r) == 1 and r != ["ERROR"])
        multiple_missing = sum(1 for r in results if len(r) > 1 and r != ["ERROR"])
        
        print(f"\nExtraction completed using {provider}:")
        print(f"  Single missing citations: {single_missing}")
        print(f"  Multiple missing citations: {multiple_missing}")
        print(f"  No missing citations: {empty_results}")
        print(f"  Successes: {successful_extractions}")
        print(f"  Errors: {error_count}")
        print(f"  Total: {total_rows}")
    
    return result_df

def _process_extraction_result(result: str) -> List[str]:
    """
    Process GPT extraction result into list of citation strings.
    Args:
        result: Raw GPT response (potentially multiple citations separated by newlines)
    Returns:
        List of citation strings, or empty list if no missing citations found
    """
    result = result.strip()
    
    # Handle "NONE" response
    if result.upper() == "NONE" or not result:
        return []
    
    # Split by newlines and clean each citation
    citations = []
    for line in result.split('\n'):
        line = line.strip()
        if line and line.upper() != "NONE":
            # Remove any leading/trailing quotes or formatting
            line = line.strip('"\'')
            if line:
                citations.append(line)
    
    # Return empty list if no valid citations found
    if not citations:
        return []
    
    return citations

DEFAULT_MODEL_OPENAI = "gpt-4.1-mini"
DEFAULT_MODEL_PERPLEXITY = "sonar-pro"

def run_extract_basic(df: pd.DataFrame, api_key: str, 
                     granularity: str = "full", provider: str = "openai",
                     model: str = DEFAULT_MODEL_OPENAI,
                     system_message: str = "", **kwargs) -> pd.DataFrame:
    """
    Convenience function for basic extraction with system message separation.
    """
    from .prompts.default import prompt_extract_missing

    # Switch model for Perplexity only if user didn't override the default
    if model == DEFAULT_MODEL_OPENAI and provider == "perplexity":
        model = DEFAULT_MODEL_PERPLEXITY

    return run_extract(
        df=df,
        prompt_func=prompt_extract_missing,
        api_key=api_key,
        granularity=granularity,
        provider=provider,
        model=model,
        system_message=system_message,
        **kwargs
    )




# Example usage strings
EXAMPLES = """
# Basic extraction (OpenAI - default)
df_result = run_extract_basic(df, "openai-api-key")

# Perplexity extraction
df_result = run_extract_basic(df, "perplexity-api-key", provider="perplexity")

# Specific models
df_result = run_extract_basic(df, "openai-key", provider="openai", model="gpt-4-turbo")
df_result = run_extract_basic(df, "perplexity-key", provider="perplexity", model="sonar-small")

# Advanced usage with custom throttling #1
from processing.throttling import TokenBucketThrottler
throttler = TokenBucketThrottler(rpm=30, burst_size=5)
df_result = run_extract(df, prompt_extract_missing, "api-key",
                       throttler=throttler, provider="perplexity", model="sonar-pro")

# Advanced usage with custom throttling #2
# Create throttler with 30 requests per minute, 1 million tokens per minute, and burst capacity 5
throttler = TokenBucketThrottler(rpm=30, tpm=1_000_000, burst_size=5)
df_result = run_extract(df, prompt_extract_missing, "api-key",
                       throttler=throttler, provider="perplexity", model="sonar-pro")

# With granularity parameter
df_result = run_extract_basic(df, "api-key", granularity="article", provider="openai")

# Compare providers on same data
df_openai = run_extract_basic(df, openai_key, provider="openai")
df_perplexity = run_extract_basic(df, perplexity_key, provider="perplexity")

# Result DataFrame has new 'missing_citations' column:
# [[], ["citation1"], ["citation1", "citation2"], ["ERROR"]]
"""