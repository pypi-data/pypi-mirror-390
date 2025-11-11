# gptquery/tools/tool_text_extraction/extract_affiliations/log.py
import time
import functools
from typing import Any
from ....core.execution_logger import ExecutionLogger


class ExtractAffiliationsLogger(ExecutionLogger):
    """Extract affiliations specific logging implementation."""
        
    def __init__(self):
        super().__init__("extract_affiliations")
        
    def log_execution(self, func):
        """Tool-specific decorator for extract_affiliations."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                execution_stats = {
                    "model": kwargs.get("model"),
                    "parameters": {
                        "temperature": kwargs.get("temperature", 0.0),
                        "max_tokens": kwargs.get("max_tokens", 10000)
                    },
                    "execution_stats": {
                        "total_rows":  len(kwargs["df"]),
                        "execution_time_seconds": round(execution_time, 2),
                        "successful_operations": self._count_successful_operations(result),
                        "error_count": self._count_errors(result)
                    },
                    "system_message": kwargs.get("system_message")
                }
                
                self.save_execution_log(execution_stats)
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                error_stats = {
                    "model": kwargs.get("model", "gpt-4.1-mini"),
                    "execution_stats": {
                        "execution_time_seconds": round(execution_time, 2),
                        "error": str(e),
                        "status": "failed"
                    }
                }
                self.save_execution_log(error_stats)
                raise
        
        return wrapper
    
    def _count_successful_operations(self, result: Any) -> int:
        """Count successful affiliation extraction operations."""
        if not hasattr(result, 'affiliations'):
            return 0
        return sum(1 for affs in result['affiliations'] if affs != ["ERROR"])
    
    def _count_errors(self, result: Any) -> int:
        """Count error operations."""
        if not hasattr(result, 'affiliations'):
            return 0
        return sum(1 for affs in result['affiliations'] if affs == ["ERROR"])
