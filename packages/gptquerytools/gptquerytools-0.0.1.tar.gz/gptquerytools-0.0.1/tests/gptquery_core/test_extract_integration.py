# test_extract_integration.py
import os
import pandas as pd
from pathlib import Path 
from dotenv import load_dotenv
from gptquery import run_extract_basic

# Load environment variables from .env file
SECRETS_FILE = Path(r"C:\LocalSecrets\master.env")
load_dotenv(str(SECRETS_FILE))
api_key = os.getenv('OPENAI_UIO24EMC_KEY')

def test_extract_with_logging(api_key):
    # Create minimal test DataFrame
    test_df = pd.DataFrame({
        'question_text': ['Does Article 49 TFEU apply?', 'What about Regulation 1408/71?'],
        'potential_citations': ['', '32006L0123']
        })
    ## USAGE pattern
    results_df = run_extract_basic(test_df, api_key, model="gpt-4.1")
    
    # VERIFY function still works
    assert 'missing_citations' in results_df.columns
    
    # VERIFY log was created
    log_files = list(Path.cwd().glob("logs/*extract_citations*.json"))
    assert len(log_files) > 0
    
    print(f"✓ Function works, log created: {log_files[-1].name}")

test_extract_with_logging(api_key)
