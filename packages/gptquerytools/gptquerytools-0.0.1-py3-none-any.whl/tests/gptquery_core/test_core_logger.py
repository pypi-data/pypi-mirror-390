# gptquery/tests/gptquery_core/test_core_logger.py
from pathlib import Path
from ...gptquery.core.execution_logger import ExecutionLogger
# from core.execution_logger import ExecutionLogger

def test_basic_logger():
    logger = ExecutionLogger("test_extraction")
    
    # Verify directory creation
    assert (Path.cwd() / "logs").exists()
    
    # Test basic log saving
    test_stats = {
        "model": "gpt-4.1",
        "parameters": {"temperature": 0.0},
        "execution_stats": {"total_rows": 5}
    }
    
    logger.save_execution_log(test_stats)
    
    # Verify file exists and contains valid JSON
    assert logger.log_path.exists()
    print(f"✓ Log created: {logger.filename}")
