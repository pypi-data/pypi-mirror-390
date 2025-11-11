# Single file: entry_extraction_model_test.py
import json
import pandas as pd
from typing import Dict, List

def compare_citations(gt_list: List[str], pred_list: List[str]) -> Dict:
    """Basic citation comparison - case insensitive exact match"""
    gt_set = set(c.lower().strip() for c in gt_list)
    pred_set = set(c.lower().strip() for c in pred_list)
    
    if len(gt_set) == 0:
        precision = 1.0 if len(pred_set) == 0 else 0.0
        recall = 1.0
    else:
        correct = len(gt_set.intersection(pred_set))
        precision = correct / len(pred_set) if len(pred_set) > 0 else 0.0
        recall = correct / len(gt_set)
    
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    hallucinations = list(pred_set - gt_set)
    
    return {'precision': precision, 'recall': recall, 'f1': f1, 'hallucinations': hallucinations}

def test_entry_extraction_models(df: pd.DataFrame, 
                                ground_truth_col: str, 
                                model_cols: List[str]) -> pd.DataFrame:
    """Test multiple models on entry extraction task"""
    results = []
    
    for _, row in df.iterrows():
        doc_id = row['uoa_referral_id']
        gt_json = json.loads(row[ground_truth_col])
        
        for model_col in model_cols:
            pred_json = json.loads(row[model_col])
            
            # Compare each question
            for question_id, gt_citations in gt_json.items():
                pred_citations = pred_json.get(question_id, [])
                metrics = compare_citations(gt_citations, pred_citations)
                
                results.append({
                    'doc_id': doc_id,
                    'question_id': question_id,
                    'model': model_col,
                    'precision': metrics['precision'],
                    'recall': metrics['recall'],
                    'f1': metrics['f1'],
                    'hallucination_count': len(metrics['hallucinations'])
                })
    
    return pd.DataFrame(results)

# # Usage:
# results_df = test_entry_extraction_models(
#     df=your_test_data,
#     ground_truth_col='ground_truth_json',
#     model_cols=['gpt4_mini_json', 'gpt35_json', 'gpt4_nano_json', 'gpt4o_mini_json']
# )

# # Get model summary
# summary = results_df.groupby('model').agg({
#     'precision': 'mean',
#     'recall': 'mean', 
#     'f1': 'mean',
#     'hallucination_count': 'mean'
# }).round(3)

# print("=== MODEL COMPARISON ===")
# print(summary)
# best_model = summary['f1'].idxmax()
# print(f"\n🏆 Best model: {best_model}")
