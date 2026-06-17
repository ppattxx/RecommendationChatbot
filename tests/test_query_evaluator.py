"""
Script untuk membaca dan mengevaluasi test cases dari CSV
dengan kolom: pertanyaan, hasil, skor_relevansi
"""

import sys
import uuid
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web_pipeline_client import WebPipelineClient


class QueryTestEvaluator:
    """Evaluator untuk test cases dari CSV"""
    
    def __init__(self, csv_path):
        self.pipeline_client = WebPipelineClient()
        self.csv_path = csv_path
        self.test_cases = pd.read_csv(csv_path)
        
    def run_evaluation(self):
        """Menjalankan evaluasi untuk semua test cases"""
        print("\n" + "="*100)
        print("EVALUASI TEST CASES DARI CSV")
        print("="*100)
        print(f"Total test cases: {len(self.test_cases)}\n")
        
        results = []
        
        for idx, row in self.test_cases.iterrows():
            pertanyaan = row['pertanyaan']
            expected_hasil = row['hasil']
            expected_skor = float(row['skor_relevansi'])
            
            try:
                token = f"web_eval_check_{idx+1}_{uuid.uuid4().hex[:8]}"
                resp = self.pipeline_client.get_all_ranked(
                    query=pertanyaan,
                    device_token=token,
                    page=1,
                    limit=20,
                )
                payload = (resp or {}).get('data', {})
                restaurants = payload.get('restaurants', [])

                if restaurants:
                    actual_hasil = str(restaurants[0].get('name', 'Unknown'))
                    actual_skor = float(
                        restaurants[0].get('raw_similarity_score', restaurants[0].get('similarity_score', 0.0)) or 0.0
                    )
                else:
                    actual_hasil = "TIDAK ADA"
                    actual_skor = 0.0
                
                # Calculate relevance score based on match.
                # Treat common no-result labels as equivalent outputs.
                is_match = self._normalize_result_label(actual_hasil) == self._normalize_result_label(expected_hasil)
                relevance_score = actual_skor if is_match else 0.0
                
                result = {
                    'no': idx + 1,
                    'pertanyaan': pertanyaan,
                    'expected': expected_hasil,
                    'actual': actual_hasil,
                    'expected_skor': expected_skor,
                    'actual_skor': relevance_score,
                    'status': '✓ PASS' if is_match else '✗ FAIL'
                }
                results.append(result)
                
                # Print detail
                print(f"[{idx+1}] {pertanyaan}")
                print(f"    Expected: {expected_hasil} (skor: {expected_skor})")
                print(f"    Actual: {actual_hasil} (skor: {relevance_score:.2f})")
                print(f"    Status: {result['status']}\n")
                
            except Exception as e:
                print(f"[{idx+1}] ERROR - {pertanyaan}")
                print(f"    Error: {str(e)}\n")
                results.append({
                    'no': idx + 1,
                    'pertanyaan': pertanyaan,
                    'expected': expected_hasil,
                    'actual': 'ERROR',
                    'expected_skor': expected_skor,
                    'actual_skor': 0.0,
                    'status': '✗ ERROR'
                })
        
        # Summary
        self._print_summary(results)
        
        return results

    @staticmethod
    def _normalize_result_label(value: str) -> str:
        text = str(value or '').strip().lower()
        no_result_aliases = {
            'tidak ada hasil',
            'tidak ada',
            'tidak ditemukan',
            'no result',
            'no results',
        }
        if text in no_result_aliases:
            return '__NO_RESULT__'
        return text
    
    def _print_summary(self, results):
        """Cetak summary hasil evaluasi"""
        print("\n" + "="*100)
        print("SUMMARY")
        print("="*100)
        
        total = len(results)
        passed = sum(1 for r in results if r['status'] == '✓ PASS')
        failed = sum(1 for r in results if r['status'] == '✗ FAIL')
        errors = sum(1 for r in results if r['status'] == '✗ ERROR')
        
        avg_skor = sum(r['actual_skor'] for r in results) / total if total > 0 else 0
        
        print(f"Total: {total}")
        print(f"Pass: {passed} ({100*passed/total:.1f}%)")
        print(f"Fail: {failed} ({100*failed/total:.1f}%)")
        print(f"Error: {errors} ({100*errors/total:.1f}%)")
        print(f"Average Score: {avg_skor:.2f}")
        print("="*100 + "\n")


if __name__ == "__main__":
    csv_path = Path(__file__).parent / "test_query_cases.csv"

    if not csv_path.exists():
        print(f"INFO: File {csv_path} tidak ditemukan, generate test cases dulu...")
        from generate_test_cases import generate_test_cases

        generate_test_cases()

    if not csv_path.exists():
        print(f"ERROR: Gagal membuat file {csv_path}")
        sys.exit(1)
    
    evaluator = QueryTestEvaluator(str(csv_path))
    evaluator.run_evaluation()
