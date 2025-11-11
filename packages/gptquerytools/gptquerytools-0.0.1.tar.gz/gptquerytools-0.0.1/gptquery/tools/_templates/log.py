# gptquery/tools/_template/log.py
import time
import functools
from typing import Dict, Any
from ...core.execution_logger import ExecutionLogger

"""
TOOL-SPECIFIC LOGGING TEMPLATE

This template provides the foundation for creating custom logging systems for new tools
in the modular LLM architecture. Each tool creator has complete freedom to define their
own metrics and logging behavior while maintaining consistency with the core infrastructure.

DECORATOR PATTERN EXPLANATION:
Decorators work like envelopes that wrap around your original function. Think of it as
a mathematical superset relationship - the decorated function contains everything your
original function does, PLUS additional logging capabilities:

Original Function = {core_logic}
Decorated Function = {logging, timing, error_handling, **core_logic**, cleanup}

When you apply @logger.log_execution, you create a new function that:
1. Executes BEFORE your function (start timing, setup logging)
2. Calls your ORIGINAL function (preserving all behavior)
3. Executes AFTER your function (save logs, calculate metrics)

The decorator EXTENDS rather than REPLACES your function - it's a superset that
includes the original plus logging enhancements.

CUSTOMIZATION REQUIREMENTS:
1. Update tool_name in __init__ method
2. Implement _calculate_tool_metrics() with your domain-specific statistics
3. Adapt _count_successful_operations() and _count_errors() to your result structure
4. Apply @logger.log_execution decorator to your main task function

INTEGRATION EXAMPLE:
# In your task.py file:
from .log import YourToolLogger

logger = YourToolLogger("your_tool_name")

@logger.log_execution
def run_your_tool(df, prompt_func, api_key, **kwargs):
    # Your tool implementation here
    return results

LOG OUTPUT:
Creates timestamped JSON files in user's current working directory:
logs/2025-06-18T11-41-30_your_tool_name.json

METRICS FREEDOM:
The _calculate_tool_metrics() method can return ANY dictionary structure.
Examples of useful domain-specific metrics:
- Citation extraction: single vs multiple citations, granularity used
- Validation: accuracy scores, completeness percentages
- Selection: filtering criteria, results processed
"""


class ToolLogger(ExecutionLogger):
    """
    Template logger for new tools. Copy this file and customize the metrics
    calculation method to track whatever statistics matter for your specific tool.
    """
    
    def __init__(self, tool_name: str):
        # Initialize base logger with your tool name
        super().__init__(tool_name)
        
    def log_execution(self, func):
        """
        Decorator that wraps your main task function to automatically capture
        execution statistics. Apply this to your run_* function in task.py
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Execute the original task function
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Capture standard execution metrics
                execution_stats = {
                    "model": kwargs.get("model", "gpt-4o"),
                    "parameters": {
                        "temperature": kwargs.get("temperature", 0.0),
                        "top_p": kwargs.get("top_p", 1.0),
                        "max_tokens": kwargs.get("max_tokens", 5000)
                    },
                    "execution_stats": {
                        "total_rows": len(args[0]) if args else 0,
                        "execution_time_seconds": round(execution_time, 2),
                        "successful_operations": self._count_successful_operations(result),
                        "error_count": self._count_errors(result)
                    }
                }
                
                # Calculate your custom tool-specific metrics
                tool_specific_stats = self._calculate_tool_metrics(result, kwargs)
                
                # Save the log file to user's current directory
                self.save_execution_log(execution_stats, tool_specific_stats)
                
                return result
                
            except Exception as e:
                # Log errors without breaking the tool functionality
                execution_time = time.time() - start_time
                error_stats = {
                    "model": kwargs.get("model", "gpt-4o"),
                    "execution_stats": {
                        "execution_time_seconds": round(execution_time, 2),
                        "error": str(e),
                        "status": "failed"
                    }
                }
                self.save_execution_log(error_stats)
                raise
        
        return wrapper
    
    def _calculate_tool_metrics(self, result: Dict[str, Any], 
                              execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        CUSTOMIZE THIS METHOD: Define what metrics matter for your specific tool.
        
        Examples of useful metrics:
        - Citation extraction: count single vs multiple citations found
        - Validation: accuracy scores, completeness percentages  
        - Selection: filtering criteria applied, results filtered
        
        Args:
            result: The return value from your task function
            execution_data: The kwargs passed to your task function
            
        Returns:
            Dictionary with your custom metrics - structure is completely up to you
        """
        # Example metrics - replace with your own logic
        return {
            "custom_metric_1": "example_value",
            "custom_metric_2": 42,
            "tool_parameter_used": execution_data.get("your_parameter", "default"),
            "results_processed": len(result) if hasattr(result, '__len__') else 1
        }
    
    def _count_successful_operations(self, result: Dict[str, Any]) -> int:
        """
        CUSTOMIZE THIS METHOD: Count successful operations for your tool.
        This appears in the standard execution stats section.
        """
        # Example logic - adapt to your result structure
        if hasattr(result, '__len__'):
            return len(result)
        return 1
    
    def _count_errors(self, result: Dict[str, Any]) -> int:
        """
        CUSTOMIZE THIS METHOD: Count errors/failures for your tool.
        This appears in the standard execution stats section.
        """
        # Example logic - adapt to your error handling approach
        if hasattr(result, 'get') and 'errors' in result:
            return len(result['errors'])
        return 0

# Usage example in your task.py file:
# from .log import ToolLogger
# 
# logger = ToolLogger("your_tool_name")
# 
# @logger.log_execution
# def run_your_tool(df, prompt_func, api_key, **kwargs):
#     # Your tool implementation here
#     return results
