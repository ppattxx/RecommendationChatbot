"""
Script untuk generate test cases dengan data real dari recommendation engine
"""

import sys
import uuid
from pathlib import Path
import pandas as pd
import csv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web_pipeline_client import WebPipelineClient


def generate_test_cases():
    """Generate test cases dengan hasil actual dari engine"""
    pipeline_client = WebPipelineClient()
    
    # Query test cases
    queries = [
        "pizza di kuta",
        "restoran italia di senggigi",
        "sushi di gili trawangan",
        "burger di mataram",
        "mexican food di kuta",
        "nasi goreng di senggigi",
        "seafood di gili air",
        "pasta di pemenang",
        "chicken di kuta",
        "steak di senggigi",
        "coffee shop di mataram",
        "bakery di kuta",
        "vegetarian di gili trawangan",
        "ice cream di senggigi",
        "breakfast di kuta",
        "lunch di mataram",
        "dinner di senggigi",
        "brunch di kuta",
        "bbq di pemenang",
        "grill di senggigi",
        "asian food di kuta",
        "chinese di mataram",
        "thai di senggigi",
        "vietnamese di kuta",
        "indian di gili trawangan",
        "mediterranean di senggigi",
        "french di kuta",
        "spanish di mataram",
        "greek di senggigi",
        "turkish di kuta",
        "ramen di gili trawangan",
        "halal food di mataram",
        "vegan di senggigi",
        "bar di kuta",
        "cocktail di senggigi",
        "wine bar di kuta",
        "pub di mataram",
        "healthy food di gili air",
        "organic food di kuta",
        "fine dining di senggigi",
        "beachfront restaurant di gili trawangan",
        "outdoor cafe di mataram",
        "rooftop restaurant di kuta",
        "family restaurant di senggigi",
    ]
    
    results = []
    output_file = Path(__file__).parent / "test_query_cases.csv"
    
    print("\n" + "="*100)
    print("GENERATE TEST CASES DENGAN DATA REAL")
    print("="*100 + "\n")
    
    for idx, query in enumerate(queries, 1):
        try:
            token = f"web_eval_cases_{idx}_{uuid.uuid4().hex[:8]}"
            resp = pipeline_client.get_all_ranked(
                query=query,
                device_token=token,
                page=1,
                limit=20,
            )
            payload = (resp or {}).get('data', {})
            restaurants = payload.get('restaurants', [])

            if restaurants:
                hasil = str(restaurants[0].get('name', 'Unknown'))
                raw_score = restaurants[0].get('raw_similarity_score', restaurants[0].get('similarity_score', 0.0))
                skor = round(float(raw_score or 0.0), 4)
            else:
                hasil = "Tidak ada hasil"
                skor = 0.0
            
            result = {
                'pertanyaan': query,
                'hasil': hasil,
                'skor_relevansi': skor,
                'pipeline': 'web_all_ranked',
            }
            results.append(result)
            
            print(f"[{idx}/{len(queries)}] {query}")
            print(f"           → {hasil} (skor: {skor})")
            
        except Exception as e:
            print(f"[{idx}/{len(queries)}] ERROR - {query}")
            print(f"           → Error: {str(e)}")
            result = {
                'pertanyaan': query,
                'hasil': 'ERROR',
                'skor_relevansi': 0.0
            }
            results.append(result)
    
    # Save to CSV
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL)
    
    print("\n" + "="*100)
    print(f"✓ Test cases berhasil disimpan ke: {output_file}")
    print(f"  Total: {len(results)} queries")
    print("="*100 + "\n")
    
    # Print summary
    successful = sum(1 for r in results if r['hasil'] != 'ERROR' and r['hasil'] != 'Tidak ada hasil')
    print(f"Successful results: {successful}/{len(results)}")
    print(f"Average score: {sum(r['skor_relevansi'] for r in results) / len(results):.2f}\n")
    
    return df


if __name__ == "__main__":
    generate_test_cases()
