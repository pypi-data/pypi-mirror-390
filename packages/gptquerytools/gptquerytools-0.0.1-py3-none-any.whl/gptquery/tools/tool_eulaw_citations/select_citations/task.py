# gptquery/tools/tool_eulaw_citations/select_citations/task.py

"""
Selector task execution with list-based output for direct citation matching.
"""
import pandas as pd
from typing import Optional, Callable, Any, List
from ....core.client import GPTClient, RateLimitError, APIError, AuthenticationError, ModelValidationError
from ....processing.utils import validate_required_columns
from .log import SelectCitationsLogger


# Create logger instance
logger = SelectCitationsLogger()

@logger.log_execution
def run_select(df: pd.DataFrame, prompt_func: Callable, api_key: str, 
               throttler: Optional[Any] = None, model: str = "gpt-4.1-mini",
               provider: str = "openai", progress: bool = True, 
               system_message: str = "",**kwargs) -> pd.DataFrame:
    """
    Run selection task on DataFrame with multi-provider support and list-based output per row.
    
    Args:
        df: DataFrame with required columns (defined by prompt_func)
        prompt_func: Prompt template function to use
        api_key: API key for the chosen provider
        throttler: Throttling strategy (defaults to SimpleThrottler)
        model: Model to use (provider-specific)
        provider: AI provider to use ("openai" or "perplexity")
        progress: Whether to print progress updates
        **kwargs: Additional parameters passed to prompt_func
        
    Returns:
        DataFrame with new 'selected_citations' column containing list of citation strings
        
    Raises:
        ValueError: If required columns are missing or invalid provider
        AuthenticationError: If API key is invalid
        ModelValidationError: If model is invalid for the provider
    """
    
    if not system_message:
        from .prompts.default import SELECTION_SYSTEM_MESSAGE
        system_message = SELECTION_SYSTEM_MESSAGE
    
    # Validate required columns before starting
    validate_required_columns(df, prompt_func)
    
    # Default throttler if none provided
    if throttler is None:
        from ....processing.throttling import SimpleThrottler
        throttler = SimpleThrottler(rpm=50)
    
    # Initialize multi-provider client
    client = GPTClient(api_key, model, provider)
    
    
    # Prepare results
    results = []
    total_rows = len(df)
    
    if progress:
        print(f"Starting selection of {total_rows} rows using {provider}...")
    
    # Process each row
    for i, (idx, row) in enumerate(df.iterrows()):
        try:
            # Apply throttling
            if throttler:
                throttler.wait_if_needed()
                        
            # Generate user message only (dynamic content)
            user_message = prompt_func(**row.to_dict(), **kwargs)
            
            # Make API call with system/user message separation
            result = client.extract(
                text=user_message,        # User message (dynamic question data + citations)
                prompt=system_message,    # System message (static instructions)
                model=model 
                )
            
            # Process result - return list of citation strings
            processed_result = _process_selection_result(result)
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
    result_df['selected_citations'] = results
    
    if progress:
        successful_selections = sum(1 for r in results if r != ["ERROR"] and len(r) > 0)
        empty_results = sum(1 for r in results if r == [])
        error_count = sum(1 for r in results if r == ["ERROR"])
        single_citations = sum(1 for r in results if len(r) == 1 and r != ["ERROR"])
        multiple_citations = sum(1 for r in results if len(r) > 1 and r != ["ERROR"])
        
        print(f"\nSelection completed using {provider}:")
        print(f"  Single citations found: {single_citations}")
        print(f"  Multiple citations found: {multiple_citations}")
        print(f"  No direct citations found: {empty_results}")
        print(f"  Successes: {successful_selections}")
        print(f"  Errors: {error_count}")
        print(f"  Total: {total_rows}")
    
    return result_df

def _process_selection_result(result: str) -> List[str]:
    """
    Process GPT selection result into list of citation strings.
    
    Args:
        result: Raw GPT response (potentially multiple citations separated by newlines)
        
    Returns:
        List of citation strings, or empty list if no citations found
    """
    result = result.strip()
    
    # Handle empty or "NONE" response
    if not result or result.upper() == "NONE":
        return []
    
    # Split by newlines and clean each citation
    citations = []
    for line in result.split('\n'):
        line = line.strip()
        if line and line.upper() != "NONE":
            # Clean any formatting (quotes, extra whitespace)
            line = line.strip('"\'')
            if line:
                citations.append(line)
    
    # Return empty list if no valid citations found
    if not citations:
        return []
    
    return citations

def run_select_basic(df: pd.DataFrame, 
                     api_key: str, 
                     provider: str = "openai",
                     model: str = "gpt-4.1-mini", 
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
    from .prompts.default import prompt_select_citations
    
    # Auto-adjust model for provider if using default
    if model == "gpt-4.1-mini" and provider == "perplexity":
        model = "sonar-pro"  # Sensible Perplexity default
    
    return run_select(
        df=df,
        prompt_func=prompt_select_citations,
        api_key=api_key,
        provider=provider,
        model=model,
        **kwargs
    )


# Example usage strings
EXAMPLES = """
# Basic selection (OpenAI - default)
df_result = run_select_basic(df, "openai-api-key")

# Perplexity selection
df_result = run_select_basic(df, "perplexity-api-key", provider="perplexity")

# Specific models
df_result = run_select_basic(df, "openai-api-key", provider="openai", model="gpt-4-turbo")
df_result = run_select_basic(df, "perplexity-api-key", provider="perplexity", model="sonar-small")

# Advanced usage with custom throttling
from processing.throttling import TokenBucketThrottler
throttler = TokenBucketThrottler(rpm=30, burst_size=5)
df_result = run_select(df, prompt_select_citations, "api-key",
                      throttler=throttler, provider="perplexity", model="sonar-pro")

# Compare providers on same data
df_openai = run_select_basic(df, "openai-api-key", provider="openai")
df_perplexity = run_select_basic(df, "perplexity-api-key", provider="perplexity")

# Result DataFrame has new 'selected_citations' column:
# [[], ["citation1"], ["citation1", "citation2"], ["ERROR"]]
"""

