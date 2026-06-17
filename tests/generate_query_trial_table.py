"""
Generate tabel uji coba query:
- pertanyaan
- hasil (top-1 recommendation)
- skor_kemiripan

Output:
- tests/query_trial_table.csv
- tests/query_trial_table.md
"""

import csv
import sys
import uuid
from pathlib import Path
from typing import List

import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web_pipeline_client import WebPipelineClient


DEFAULT_QUERIES: List[str] = [
    "pizza di kuta",
    "sushi di gili trawangan",
    "seafood di senggigi",
    "burger murah di mataram",
    "coffee shop cozy di mataram",
    "italian fine dining di senggigi",
    "vegetarian di gili air",
    "beachfront restaurant di gili trawangan",
    "halal food di mataram",
    "ramen di gili trawangan",
    "best restaurant di gili meno",
    "tempat makan viral di lombok",
]


def build_trial_table(queries: List[str]) -> pd.DataFrame:
    pipeline_client = WebPipelineClient()
    rows = []

    print("\n" + "=" * 100)
    print("GENERATE TABEL UJI COBA QUERY")
    print("=" * 100)

    for idx, query in enumerate(queries, 1):
        try:
            token = f"web_eval_trial_{idx}_{uuid.uuid4().hex[:8]}"
            resp = pipeline_client.get_all_ranked(
                query=query,
                device_token=token,
                page=1,
                limit=20,
            )
            payload = (resp or {}).get('data', {})
            restaurants = payload.get('restaurants', [])

            if restaurants:
                top_rec = restaurants[0]
                result_name = top_rec.get('name', 'Unknown')
                similarity = float(top_rec.get('raw_similarity_score', top_rec.get('similarity_score', 0.0)) or 0.0)
            else:
                result_name = "Tidak ada hasil"
                similarity = 0.0

            rows.append(
                {
                    "pertanyaan": query,
                    "hasil": result_name,
                    "skor_kemiripan": round(similarity, 4),
                    "pipeline": "web_all_ranked",
                }
            )

            print(f"[{idx}/{len(queries)}] {query}")
            print(f"    -> {result_name} | skor: {similarity:.4f}")

        except Exception as exc:
            rows.append(
                {
                    "pertanyaan": query,
                    "hasil": f"ERROR: {exc}",
                    "skor_kemiripan": 0.0,
                    "pipeline": "web_all_ranked",
                }
            )
            print(f"[{idx}/{len(queries)}] {query}")
            print(f"    -> ERROR: {exc}")

    return pd.DataFrame(rows)


def write_outputs(df: pd.DataFrame, base_dir: Path) -> None:
    csv_path = base_dir / "query_trial_table.csv"
    md_path = base_dir / "query_trial_table.md"

    df.to_csv(csv_path, index=False, quoting=csv.QUOTE_ALL)

    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Tabel Uji Coba Query\n\n")
        f.write("| No | Pertanyaan | Hasil | Skor Kemiripan | Pipeline |\n")
        f.write("|---:|---|---|---:|---|\n")
        for i, row in df.iterrows():
            f.write(
                f"| {i+1} | {row['pertanyaan']} | {row['hasil']} | {row['skor_kemiripan']:.4f} | {row['pipeline']} |\n"
            )

    print("\n" + "=" * 100)
    print("Output berhasil dibuat:")
    print(f"- {csv_path}")
    print(f"- {md_path}")
    print("=" * 100 + "\n")


def main() -> None:
    base_dir = Path(__file__).parent
    df = build_trial_table(DEFAULT_QUERIES)
    write_outputs(df, base_dir)


if __name__ == "__main__":
    main()
