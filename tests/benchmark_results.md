# Hasil Eksperimen Benchmark

## 1) Waktu Respons (Min/Max/Avg, ms)

| Metrik | Min (ms) | Max (ms) | Avg (ms) |
|---|---:|---:|---:|
| API Gateway overhead | 6.740 | 18.493 | 14.146 |
| Ekstraksi Intent & Entity | 33.092 | 122.916 | 38.551 |
| Lookup Preference / Device Token | 6.247 | 31.762 | 19.188 |
| TF-IDF + Hybrid Scoring | 3.594 | 173.592 | 53.084 |
| Total Response Time End-to-End | 64.041 | 249.446 | 124.969 |

## 2) Akurasi Rekomendasi Top-5

| Kelompok Query | Jumlah Query | Precision@5 | Recall@5 | F1-Score |
|---|---:|---:|---:|---:|
| Kueri Entitas Tunggal | 10 | 0.1200 | 0.0667 | 0.0848 |
| Kueri Multi Entitas | 10 | 0.0400 | 0.0200 | 0.0267 |
| Kueri Tanpa Entitas / Ambigu | 10 | 0.0000 | 0.0000 | 0.0000 |

## 3) Pengujian Fungsional (test_e2e_api.py)

Hasil bagian ini diisi otomatis oleh runner terpisah setelah `tests/test_e2e_api.py` dieksekusi.
