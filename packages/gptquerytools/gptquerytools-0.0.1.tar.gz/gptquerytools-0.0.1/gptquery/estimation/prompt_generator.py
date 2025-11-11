# gptquery\estimation\prompt_generator.py

"""
Pure prompt generation utility.
Generates prompt text from DataFrame + prompt function.
"""
import pandas as pd
from typing import Callable

def generate_prompt_texts(df: pd.DataFrame, 
                         prompt_func: Callable,
                         **prompt_kwargs) -> pd.Series:
    """
    Generate prompt strings from DataFrame using your existing prompt function.
    
    Args:
        df: Input DataFrame with columns required by prompt_func
        prompt_func: Your existing prompt function (e.g., prompt_validate_completeness)
        **prompt_kwargs: Arguments for prompt function (e.g., granularity="article")
        
    Returns:
        pd.Series of prompt strings
        
    Example:
        >>> from prompts.validate import prompt_validate_completeness
        >>> prompts = generate_prompt_texts(
        ...     df=df,
        ...     prompt_func=prompt_validate_completeness,
        ...     granularity="article"
        ... )
        >>> print(f"Generated {len(prompts)} prompts")
    """
    return df.apply(
        lambda row: prompt_func(**{**row.to_dict(), **prompt_kwargs}), 
        axis=1
    )

def add_prompt_column(df: pd.DataFrame,
                     prompt_func: Callable, 
                     column_name: str = "prompt_text",
                     **prompt_kwargs) -> pd.DataFrame:
    """
    Add prompt column to DataFrame.
    Useful for integrating with your existing token analysis functions.
    
    Args:
        df: Input DataFrame
        prompt_func: Your prompt function
        column_name: Name for new column containing prompts
        **prompt_kwargs: Arguments for prompt function
        
    Returns:
        DataFrame with new prompt column
        
    Example:
        >>> df_with_prompts = add_prompt_column(
        ...     df=df,
        ...     prompt_func=prompt_validate_completeness,
        ...     column_name="full_prompt",
        ...     granularity="article"
        ... )
        >>> # Now use your existing functions:
        >>> df_analyzed = max_tokens_in_column(df_with_prompts, "full_prompt")
    """
    df_result = df.copy()
    df_result[column_name] = generate_prompt_texts(df, prompt_func, **prompt_kwargs)
    return df_result
