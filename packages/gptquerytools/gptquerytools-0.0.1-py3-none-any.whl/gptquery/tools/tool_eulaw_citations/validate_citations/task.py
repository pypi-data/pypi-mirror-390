# gptquery/tools/tool_eulaw_citations/validate_citations/task.py

"""
Validation task execution with external throttling and robust error handling.
"""
import pandas as pd
from typing import Optional, Callable, Any
from ....core.client import GPTClient, RateLimitError, APIError, AuthenticationError, ModelValidationError
from ....processing.utils import validate_required_columns
from ....processing.throttling import SimpleThrottler
from .log import ValidateCitationsLogger

# Create logger instance
logger = ValidateCitationsLogger()

@logger.log_execution
def run_validate(df: pd.DataFrame, prompt_func: Callable, api_key: str, 
                throttler: Optional[Any] = None, model: str = "gpt-4.1-mini",
                provider: str = "openai", progress: bool = True, 
                temperature: float = 0.0, system_message: str = "", **kwargs) -> pd.DataFrame:
    """
    Run validation task on DataFrame with multi-provider support and system message separation.
    
    Args:
        df: DataFrame with required columns (defined by prompt_func)
        prompt_func: Prompt template function to use
        api_key: API key for the chosen provider
        throttler: Throttling strategy (defaults to SimpleThrottler)
        model: Model to use (provider-specific)
        provider: AI provider to use ("openai", "perplexity", or "claude")
        progress: Whether to print progress updates
        temperature: Sampling temperature (0.0 for deterministic)
        system_message: Custom system message (uses default if empty)
        **kwargs: Additional parameters passed to prompt_func
        
    Returns:
        DataFrame with new 'is_complete' column containing validation results
        
    Raises:
        ValueError: If required columns are missing or invalid provider
        AuthenticationError: If API key is invalid
        ModelValidationError: If model is invalid for the provider
    """
    
    # Validate required columns before starting
    validate_required_columns(df, prompt_func)
    
    # Default throttler if none provided
    if throttler is None:
        throttler = SimpleThrottler(rpm=50) # type: ignore
    
    # Initialize multi-provider client
    client = GPTClient(api_key, model, provider)
    
    # Use provided system message or default from prompt file
    if not system_message:
        from .prompts.default import VALIDATION_SYSTEM_MESSAGE
        system_message = VALIDATION_SYSTEM_MESSAGE
    
    # Prepare results
    results = []
    total_rows = len(df)
    
    if progress:
        print(f"Starting validation of {total_rows} rows using {provider}...")
    
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
                text=user_message,        # User message (dynamic question data)
                prompt=system_message,    # System message (static instructions)
                model=model,
                temperature=temperature,  # Deterministic temperature
                max_tokens=kwargs.get('max_tokens', 1000)  # Shorter responses for validation
            )
            
            # Clean result (should be "complete" or "incomplete")
            result = result.strip().lower()
            if result not in ["complete", "incomplete"]:
                # If GPT returns unexpected format, try to parse
                if "complete" in result:
                    result = "complete"
                elif "incomplete" in result:
                    result = "incomplete"
                else:
                    result = f"ERROR: Unexpected response format: {result}"
            
            results.append(result)
            
        except RateLimitError:
            # Default strategy for rate limits - assume incomplete
            results.append("incomplete")
            if progress:
                print(f"Rate limit hit at row {i+1} ({provider}), defaulting to 'incomplete'")
                
        except (APIError, AuthenticationError, ModelValidationError) as e:
            # Other errors - encode in output for debugging
            results.append(f"ERROR: {str(e)}")
            if progress:
                print(f"Error at row {i+1} ({provider}): {str(e)}")
                
        except Exception as e:
            # Unexpected errors - encode in output
            results.append(f"ERROR: Unexpected error: {str(e)}")
            if progress:
                print(f"Unexpected error at row {i+1} ({provider}): {str(e)}")
        
        # Progress updates every 10%
        if progress and (i + 1) % max(1, total_rows // 10) == 0:
            percentage = ((i + 1) / total_rows) * 100
            print(f"Progress: {i+1}/{total_rows} ({percentage:.1f}%)")
    
    # Create result DataFrame
    result_df = df.copy()
    result_df['is_complete'] = results
    
    if progress:
        complete_count = sum(1 for r in results if r == "complete")
        incomplete_count = sum(1 for r in results if r == "incomplete")
        error_count = sum(1 for r in results if r.startswith("ERROR"))
        
        print(f"\nValidation completed using {provider}:")
        print(f"  Complete: {complete_count}")
        print(f"  Incomplete: {incomplete_count}")
        print(f"  Errors: {error_count}")
        print(f"  Total: {total_rows}")
    
    return result_df

def run_validate_basic(df: pd.DataFrame, api_key: str, 
                      granularity: str = "full", provider: str = "openai", 
                      model: str = "gpt-4.1-mini", temperature: float = 0.0, 
                      system_message: str = "", **kwargs) -> pd.DataFrame:
    """
    Convenience function for basic validation with system message separation and multi-provider support.
    
    Args:
        df: DataFrame with 'question_text' and 'potential_citations' columns
        api_key: API key for the chosen provider
        granularity: Validation granularity ("full", "article", "paragraph")
        provider: AI provider to use ("openai", "perplexity", or "claude")
        model: Model to use (provider-specific, defaults to gpt-4o/sonar-pro/claude-3-5-sonnet)
        temperature: Sampling temperature (0.0 for deterministic results)
        system_message: Custom system message (uses default if empty)
        **kwargs: Additional parameters for run_validate
        
    Returns:
        DataFrame with new 'is_complete' column containing validation results
    """
    from .prompts.default import prompt_validate_completeness
    
    # Auto-adjust model for provider if using default
    if model == "gpt-4.1-mini" and provider == "perplexity":
        model = "sonar-pro"  # Sensible Perplexity default
    elif model == "gpt-4.1-mini" and provider == "claude":
        model = "claude-3-5-sonnet-20241022"  # Sensible Claude default
    
    return run_validate(
        df=df,
        prompt_func=prompt_validate_completeness,
        api_key=api_key,
        granularity=granularity,
        provider=provider,
        model=model,
        temperature=temperature,       
        system_message=system_message,
        **kwargs
    )


# Example usage strings with new parameters:
EXAMPLES = """
# Basic validation with deterministic temperature (OpenAI - default)
df_result = run_validate_basic(df, "openai-api-key", temperature=0.0)

# Perplexity validation with deterministic results
df_result = run_validate_basic(df, "perplexity-api-key", provider="perplexity", temperature=0.0)

# Claude validation with custom system message
strict_system = "You are an extremely strict EU legal expert. Only mark complete if EVERY referenced provision is cited."
df_result = run_validate_basic(df, "claude-key", provider="claude", 
                              temperature=0.0, system_message=strict_system)

# Specific models with temperature control
df_result = run_validate_basic(df, "openai-key", provider="openai", 
                              model="gpt-4-turbo", temperature=0.0)
df_result = run_validate_basic(df, "perplexity-key", provider="perplexity", 
                              model="sonar-small", temperature=0.0)

# Advanced usage with custom throttling and system message
from processing.throttling import TokenBucketThrottler
throttler = TokenBucketThrottler(rpm=30, burst_size=5)

custom_system = "You are a conservative EU legal validator. Be extremely precise in citation matching."
df_result = run_validate(df, prompt_validate_completeness, "api-key", 
                        throttler=throttler, provider="claude", model="claude-3-5-sonnet-20241022",
                        temperature=0.0, system_message=custom_system)

# Compare providers with same deterministic settings
df_openai = run_validate_basic(df, openai_key, provider="openai", temperature=0.0)
df_perplexity = run_validate_basic(df, perplexity_key, provider="perplexity", temperature=0.0)
df_claude = run_validate_basic(df, claude_key, provider="claude", temperature=0.0)

# Provider-specific system messages for comparison
openai_system = "Be conservative and precise in your legal assessments."
claude_system = "Think step-by-step through each legal requirement before deciding."

df_openai = run_validate_basic(df, openai_key, provider="openai", 
                              temperature=0.0, system_message=openai_system)
df_claude = run_validate_basic(df, claude_key, provider="claude", 
                              temperature=0.0, system_message=claude_system)

# Result DataFrame has new 'is_complete' column:
# ['complete', 'incomplete', 'ERROR: Rate limit exceeded']
"""
