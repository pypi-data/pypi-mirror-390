# gptquery/__init__.py
"""GPT Query Architecture"""

# Import core classes
from .core.client import GPTClient, RateLimitError, APIError, AuthenticationError, ModelValidationError

# Import main functions  
from .tools.tool_eulaw_citations.validate_citations.task import run_validate_basic
from .tools.tool_eulaw_citations.extract_citations.task import run_extract_basic
from .tools.tool_eulaw_citations.select_citations.task import run_select_basic

# IMPORT Cost Estimation utils
from .estimation.cost_estimator import (estimate_costs_for_models,create_cost_matrix,display_gpt_models_df)


# Export everything
__all__ = ['GPTClient', 'RateLimitError', 'APIError', 'AuthenticationError', 'ModelValidationError', 
           'estimate_costs_for_models', 'create_cost_matrix', 'display_gpt_models_df',
           'run_validate_basic','run_extract_basic', 'run_select_basic']

__version__ = '0.0.3'



