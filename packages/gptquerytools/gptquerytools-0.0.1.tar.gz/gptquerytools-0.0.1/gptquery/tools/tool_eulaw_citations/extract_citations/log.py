# gptquery/tools/tool_eulaw_citations/extract_citations/log.py
"""
gptquery.tools.extract_citations.log

Logging utilities for the extract_citations tool.

Defines the ExtractCitationsLogger class which extends
ExecutionLogger to provide specialized logging functionality
for citation extraction processes, including execution timing,
success/error counting, and extraction-specific metrics.

Provides a decorator to wrap extraction functions for
automatic logging of execution details and error handling.
"""

# import warnings
import time
import functools
from typing import Dict, Any
from ....core.execution_logger import ExecutionLogger

class ExtractCitationsLogger(ExecutionLogger):
    """Extract citations specific logging implementation."""
    
    def __init__(self):
        super().__init__("extract_citations")
    
    def log_execution(self, func):
        """Tool-specific decorator for extract_citations."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Execute original function
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Extract core execution statistics
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
                
                # Calculate tool-specific metrics
                tool_specific_stats = self._calculate_extraction_metrics(result, kwargs)
                
                # Save log
                self.save_execution_log(execution_stats, tool_specific_stats)
                
                return result
                
            except Exception as e:
                # Log error and re-raise
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
    
    def _calculate_extraction_metrics(self, result: Dict[str, Any], 
                                    execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate extraction-specific metrics."""
        if 'missing_citations' not in result:
            return {"error": "missing_citations column not found"}
        
        missing_citations = result['missing_citations'].tolist()
        
        single_citations = sum(1 for r in missing_citations if len(r) == 1 and r != ["ERROR"])
        multiple_citations = sum(1 for r in missing_citations if len(r) > 1 and r != ["ERROR"])
        empty_results = sum(1 for r in missing_citations if r == [])
        error_count = sum(1 for r in missing_citations if r == ["ERROR"])
        
        return {
            "single_citations": single_citations,
            "multiple_citations": multiple_citations,
            "empty_results": empty_results,
            "error_count": error_count,
            "granularity_used": execution_data.get("granularity", "full")
        }
    
    def _count_successful_operations(self, result: Dict[str, Any]) -> int:
        """Count successful extraction operations."""
        if 'missing_citations' not in result:
            return 0
        missing_citations = result['missing_citations'].tolist()
        return sum(1 for r in missing_citations if r != ["ERROR"])
    
    def _count_errors(self, result: Dict[str, Any]) -> int:
        """Count error operations."""
        if 'missing_citations' not in result:
            return 0
        missing_citations = result['missing_citations'].tolist()
        return sum(1 for r in missing_citations if r == ["ERROR"])
