# Update Buku PA - Versi Sinkron Implementasi

Tanggal sinkronisasi: 14 April 2026  
Nama Proyek: Sistem Rekomendasi Restoran LombokEats berbasis histori percakapan chatbot (Content-Based Filtering + NLP)

## 1. Scope Penelitian yang Disepakati
Penelitian fokus pada sistem rekomendasi restoran yang:
1. Menerima kueri bahasa alami dari pengguna melalui chatbot.
2. Mengekstrak entitas domain kuliner (lokasi, cuisine/jenis makanan, mood/preferensi, price).
3. Melakukan ranking restoran dengan Content-Based Filtering (TF-IDF + cosine similarity).
4. Mengakumulasi histori percakapan berbasis `device_token` untuk personalisasi lintas sesi.
5. Menjaga konsistensi urutan rekomendasi antara output chatbot dan kartu rekomendasi web.

Catatan: scope tidak mengandalkan Collaborative Filtering. Seluruh inti rekomendasi tetap CBF + boosting berbasis entitas dan histori.

## 2. Kesesuaian Implementasi dengan Scope
1. Backend menggunakan Flask dengan pola application factory dan dependency container.
2. Frontend menggunakan React + Vite (bukan web statis HTML/JS murni).
3. Pipeline rekomendasi terdiri dari:
   - ekstraksi intent dan entity,
   - baseline TF-IDF + cosine similarity,
   - hybrid scoring (entity bonus, preference boost, quality signal),
   - fallback untuk kueri ambigu.
4. Personalisasi memakai histori `ChatHistory` berbasis `device_token` (cross-session) dengan pembobotan frekuensi + recency.
5. Endpoint ranking web (`top5` dan `all-ranked`) sudah disejajarkan dengan pipeline ranking chatbot untuk menghindari mismatch urutan.

## 3. Fakta Teknis Proyek (Sumber Kode)
1. Inisialisasi aplikasi: `backend/app/__init__.py`
2. Endpoint chat: `backend/app/routes/chat_routes.py`
3. Endpoint rekomendasi: `backend/app/routes/recommendation_routes.py`
4. Controller chat: `backend/app/controllers/chat_controller.py`
5. Controller rekomendasi: `backend/app/controllers/recommendation_controller.py`
6. Mesin chatbot: `backend/app/services/chatbot_engine.py`
7. Mesin CBF: `backend/app/services/recommendation_engine.py`
8. Frontend app: `frontend/src/App.jsx`
9. Widget chatbot: `frontend/src/components/FloatingChatbot.jsx`

## 4. Dataset dan Komponen Data
1. Dataset utama yang dipakai engine saat ini: `data/restaurants_entitas.csv`.
2. Jumlah data aktual per sinkronisasi ini: 1163 baris, 24 kolom.
3. Kolom entitas tersedia: `entitas_lokasi`, `entitas_jenis_makanan`, `entitas_menu`, `entitas_preferensi`, `entitas_features`.

Implikasi untuk naskah: jika dokumen masih menulis total data 236, perlu disesuaikan dengan dataset aktual yang dipakai eksperimen final.

## 5. Endpoint API yang Aktif
1. `POST /api/chat`
2. `GET /api/chat/history/<session_id>`
3. `GET /api/chat/history/device/<device_token>`
4. `DELETE /api/chat/reset`
5. `DELETE /api/chat/reset-all`
6. `GET /api/recommendations`
7. `GET /api/recommendations/top5`
8. `GET /api/recommendations/all-ranked`
9. `GET /api/recommendations/profile-debug`
10. `GET /api/health`

## 6. Sinkronisasi Narasi Laporan yang Perlu Dijaga
1. Arsitektur web pada laporan harus menyebut React SPA, bukan implementasi tanpa framework frontend.
2. Personalisasi harus dijelaskan berbasis histori `device_token`, bukan sesi tunggal saja.
3. Bab hasil wajib memakai satu sumber angka evaluasi yang konsisten (hindari campur angka lama vs angka benchmark berbeda skenario).
4. Bagian ranking harus menegaskan bahwa urutan chatbot dan web sudah diselaraskan oleh pipeline yang sama.

## 7. Validasi Terbaru yang Relevan dengan Scope
1. Uji regresi API/chat flow lulus: `tests/test_api.py` dan `tests/test_chat_flow.py` (5 passed pada validasi terakhir).
2. Verifikasi skenario personalisasi historis menunjukkan top-5 chatbot dan web sudah identik pada kueri generik setelah riwayat terbentuk.

## 8. Rekomendasi Final untuk Dokumen PA
1. Tetapkan satu baseline metrik eksperimen final, lalu gunakan konsisten di Bab 4 dan Bab 5.
2. Pastikan seluruh klaim teknis merujuk implementasi di folder `backend/app/*` dan `frontend/src/*`.
3. Jika ada naskah lama yang menyebut data 236 entri, ubah sesuai dataset final yang benar-benar dipakai saat pengujian.
