# gptquery/processing/cost_estimator.py
"""
LLM cost estimation toolkit.

Core functions:
- estimate_costs_for_models(): Calculate token usage and costs for DataFrame inputs
- create_cost_matrix(): Format cost estimates into styled comparison tables
- display_gpt_models_df(): Display OpenAI model pricing and token limits
"""

import pandas as pd
import tiktoken
from IPython.display import display
from typing import Callable, Dict, List, Optional
from tokencost import TOKEN_COSTS, calculate_prompt_cost, calculate_completion_cost
from .prompt_generator import generate_prompt_texts

# KEEP your model-to-encoding mapping
CUSTOM_ENCODING_MAP = {
    "gpt-5": "o200k_base",
    "gpt-5-mini": "o200k_base",
    "gpt-5-nano":"o200k_base",
    "gpt-4.1": "o200k_base",
    "gpt-4.1-mini": "o200k_base",
    "gpt-4.1-nano": "o200k_base",
    "gpt-4o": "o200k_base",
    "gpt-4o-mini": "o200k_base",
    "gpt-4o-audio": "o200k_base",
    "chatgpt-4o": "o200k_base",
    "gpt-4": "cl100k_base",
    "gpt-4-turbo": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
}

# MAP new models to closest existing model from tokencost
TOKENCOST_MODEL_MAP = {
    "gpt-4-turbo": "gpt-4-turbo",
    "gpt-3.5-turbo": "gpt-3.5-turbo",
}

# Encoding cache (faster lookups)
ENCODING_CACHE = {}

def _count_tokens(text: str, model: str) -> int:
    """
    Private Function Count tokens using a consistent encoding, avoiding tiktoken warnings.
    """
    if model not in ENCODING_CACHE:
        enc_name = CUSTOM_ENCODING_MAP.get(model, "cl100k_base")
        ENCODING_CACHE[model] = tiktoken.get_encoding(enc_name)
    enc = ENCODING_CACHE[model]
    return len(enc.encode(text))


##############################################################################
# <> FUNC Calculate token usage and costs for DataFrame inputs
# >> >> pd.DataFrame 
##############################################################################
def estimate_costs_for_models(
    df: pd.DataFrame,
    prompt_func: Callable,
    models: List[str],
    system_msg: Optional[str] = "",
    expected_response_length: str = "complete",
    verbose: bool = True,
    **prompt_kwargs
) -> List[Dict]:
    """
    Estimate cost and token usage for all rows across multiple models.

    Args:
        df: Input DataFrame
        prompt_func: Function that builds the user prompt (single row)
        models: List of model names to compare
        system_msg: Optional system message to prepend
        expected_response_length: Used to estimate completion cost
        verbose: Whether to print progress and results (default: True)
        **prompt_kwargs: Extra keyword arguments for prompt_func

    Returns:
        List of cost and token usage breakdowns per model
    """
    if df.empty:
        raise ValueError("Input DataFrame must contain at least one row.")

    # GENERATE user prompt texts from DataFrame
    all_prompt_texts = generate_prompt_texts(df, prompt_func, **prompt_kwargs)

    # Add system message if provided
    full_prompts = [
        f"{system_msg.strip()}\n\n{prompt.strip()}" if system_msg else prompt.strip()
        for prompt in all_prompt_texts
    ]

    # Use the first model to compute tokens once
    model_for_tokens = models[0]
    precomputed_token_counts = [_count_tokens(p, model_for_tokens) for p in full_prompts]

    if verbose:
        print(f"\n=== Model Comparison for {len(df)} rows ===")
    results = []

    for model in models:
        # Use same token counts across models (if encoding matches)
        total_input_tokens = sum(precomputed_token_counts)

        # Map to tokencost-compatible model (fixes warnings)
        tokencost_model = TOKENCOST_MODEL_MAP.get(model, model)

        # But cost must be computed per model (different pricing!)
        total_input_cost = sum(calculate_prompt_cost(p, tokencost_model) for p in full_prompts)
        total_output_cost = calculate_completion_cost(expected_response_length, tokencost_model) * len(df)
        total_cost = total_input_cost + total_output_cost

        if verbose:
            print(f"\nModel: {model}")
            print(f"  Total rows: {len(df)}")
            print(f"  Total input tokens: {total_input_tokens:,}")
            print(f"  Avg input tokens per row: {total_input_tokens // len(df):,}")
            print(f"  Total input cost: ${total_input_cost:.4f}")
            print(f"  Total output cost: ${total_output_cost:.4f}")
            print(f"  Total cost: ${total_cost:.4f}")
            print(f"  Cost per row: ${total_cost / len(df):.4f}")

        results.append({
            "model": model,
            "total_rows": len(df),
            "total_input_tokens": total_input_tokens,
            "avg_input_tokens_per_row": total_input_tokens // len(df),
            "total_input_cost_usd": float(total_input_cost),
            "total_output_cost_usd": float(total_output_cost),
            "total_cost_usd": float(total_cost),
            "cost_per_row_usd": float(total_cost / len(df))
        })

    if verbose:
        print("=" * 50 + "\n")
    return results


##############################################################################
# <> FUNC Create Cost Matrix from `estimate_costs_for_models()` results
# >> List[Dict] >> pd.DataFrame Styled
##############################################################################
def create_cost_matrix(results: List[Dict], sort_by: str = "total_cost_usd") -> pd.DataFrame:
    """
    Convert cost estimation results into a sorted matrix with gradient formatting.
    
    Args:
        results: Output from estimate_costs_for_models()
        sort_by: Column to sort by (default: "total_cost_usd")
    
    Returns:
        Styled pandas DataFrame with gradient formatting on total costs
    """
    if not results:
        raise ValueError("Results list is empty")
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Sort by total cost (low to high)
    df = df.sort_values(sort_by, ascending=True).reset_index(drop=True)
    
    # Select and rename columns for display
    display_df = df[[
        'model', 
        'total_cost_usd', 
        'cost_per_row_usd',
        'total_input_tokens',
        'total_input_cost_usd',
        'total_output_cost_usd'
    ]].copy()
    
    # Rename columns for better display
    display_df.columns = [
        'Model',
        'Total Cost ($)',
        'Cost Per Row ($)', 
        'Total Tokens',
        'Input Cost ($)',
        'Output Cost ($)'
    ]
    
    # Apply gradient formatting to Total Cost column
    styled_df = display_df.style.background_gradient(
        subset=['Total Cost ($)'],
        cmap='RdYlGn_r',  # Red (high) to Green (low) - reversed
        low=0.3,
        high=0.9
    ).format({
        'Total Cost ($)': '${:.4f}',
        'Cost Per Row ($)': '${:.4f}',
        'Input Cost ($)': '${:.4f}',
        'Output Cost ($)': '${:.4f}',
        'Total Tokens': '{:,}'
    })
    
    return styled_df # type: ignore


##############################################################################
# <> FUNC Display GPT Models Costs
# >> def() >> pd.DataFrame 
##############################################################################
def display_gpt_models_df(prefix: str = "gpt", *kwrds: str):
    """
    Display GPT models with core token limits and pricing.
    Optional keyword fields are shown as ✅ (present/truthy) or ❌ (missing/false).

    Args:
        prefix (str): Filter models by prefix (e.g., "gpt", "claude")
        *kwrds (str): Optional feature keys to check presence of
    """
    prefixes = sorted(set(m.split("-", 1)[0] for m in TOKEN_COSTS))
    if prefix not in prefixes:
        raise ValueError(f"Prefix '{prefix}' not found. Available prefixes are: {prefixes}")

    rows = []
    for model_name, info in TOKEN_COSTS.items():
        if model_name.startswith(prefix):
            # Format costs as floats for now
            input_cost = info.get("input_cost_per_token", 0) * 1_000_000
            output_cost = info.get("output_cost_per_token", 0) * 1_000_000
            row = {
                "Model": model_name,
                "Max Input Tokens": info.get("max_input_tokens"),
                "Max Output Tokens": info.get("max_output_tokens"),
                "Input Cost ($/1M)": f"${input_cost:,.3f}",
                "Output Cost ($/1M)": f"${output_cost:,.3f}",
            }
            for key in kwrds:
                val = info.get(key)
                row[key] = "✅" if val else "❌"
            rows.append(row)

    df = pd.DataFrame(rows).sort_values("Model")
    display(df)
