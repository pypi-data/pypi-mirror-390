# gptquery\tools\tool_text_extraction\extract_authornames\log.py
import time
import functools
from typing import Dict, Any
from ....core.execution_logger import ExecutionLogger


class ExtractAuthornamesLogger(ExecutionLogger):
    """Select citations specific logging implementation."""
        
    def __init__(self):
        super().__init__("extract_authornames")
        
    def log_execution(self, func):
        """Tool-specific decorator for extract_authornames."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                execution_stats = {
                    "model": kwargs.get("model"),
                    "parameters": {
                        "temperature": kwargs.get("temperature"),
                        "top_p": kwargs.get("top_p"),
                        "max_tokens": kwargs.get("max_tokens")
                    },
                    "execution_stats": {
                        "total_rows": len(kwargs["df"]),
                        "execution_time_seconds": round(execution_time, 2),
                        "successful_operations": self._count_successful_operations(result),
                        "error_count": self._count_errors(result)
                    },
                    "system_message": kwargs.get("system_message")
                }
                
                tool_specific_stats = self._calculate_selection_metrics(result, kwargs)
                self.save_execution_log(execution_stats, tool_specific_stats)
                
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
    
    def _calculate_selection_metrics(self, result: Dict[str, Any], 
                                   execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate selection-specific metrics - tool creator defines these."""
        # Tool creator implements their own selection metrics
        return {
            "selection_criteria": execution_data.get("criteria", "default"),
            "filtered_count": len(result) if hasattr(result, '__len__') else 0
        }
    
    def _count_successful_operations(self, result: Dict[str, Any]) -> int:
        """Count successful selection operations."""
        return len(result) if hasattr(result, '__len__') else 1
    
    def _count_errors(self, result: Dict[str, Any]) -> int:
        """Count error operations."""
        return 0  # Tool creator can implement error counting logic
