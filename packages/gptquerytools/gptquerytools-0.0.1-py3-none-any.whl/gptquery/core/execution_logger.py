# gptquery/core/execution_logger.py
import json
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

class ExecutionLogger:
    """Base execution logger for all tools - saves to user's CWD."""
    
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.timestamp = datetime.now().isoformat().replace(':', '-')
        self.log_dir = Path.cwd() / "logs"
        self.filename = f"{self.timestamp}_{tool_name}.json"
        self.log_path = self.log_dir / self.filename
        
        # Create logs directory if needed
        try:
            self.log_dir.mkdir(exist_ok=True)
        except Exception as e:
            warnings.warn(f"Logging failed for {tool_name}: {e}")
    
    def save_execution_log(self, execution_stats: Dict[str, Any], 
                          tool_specific_stats: Optional[Dict[str, Any]] = None):
        """Save execution log with warning-based error handling."""
        try:
            log_data = {
                "timestamp": self.timestamp,
                "tool": self.tool_name,
                **execution_stats
            }
            
            if tool_specific_stats:
                log_data["tool_specific_stats"] = tool_specific_stats
            
            with open(self.log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            warnings.warn(f"Logging failed for {self.tool_name}: {e}")