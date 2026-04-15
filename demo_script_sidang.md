# Skrip Demo Sidang

Durasi target: 5-7 menit

Tujuan demo:
1. Menunjukkan query normal menghasilkan rekomendasi relevan.
2. Menunjukkan sistem robust untuk typo/slang/noisy input.
3. Menunjukkan personalisasi lintas interaksi berdasarkan histori chat.

## Persiapan Sebelum Demo

1. Pastikan backend dan frontend sudah berjalan.
2. Pastikan dataset restoran sudah ter-load.
3. Reset histori terlebih dahulu agar baseline bersih.
4. Buka dua tampilan:
   - Halaman web (kartu rekomendasi)
   - Chatbot widget

Kalimat pembuka:

"Pada demo ini saya akan menunjukkan 3 skenario: query normal, query noisy/typo, dan personalisasi berdasarkan histori chat."

## Skenario 1 - Query Normal

Langkah:
1. Ketik di chatbot:
   - "Saya cari seafood enak di Senggigi yang romantis"
2. Tunjukkan:
   - Chatbot memberi top rekomendasi.
   - Kartu restoran di web ikut menampilkan hasil.
   - Ada alasan relevansi (lokasi/cuisine/mood).

Narasi saat presentasi:

"Di sini sistem mengekstrak entitas lokasi = Senggigi, cuisine = seafood, mood = romantis, lalu memberi ranking berdasarkan kesesuaian konten dan skor hybrid."

Checklist visual:
1. Hasil tidak kosong.
2. Hasil relevan dengan entitas.
3. Ranking tampil konsisten.

## Skenario 2 - Query Noisy / Typo / Slang

Langkah:
1. Ketik:
   - "rekomen dong seafoood murce di sengigi yg cozy"
2. Lanjutkan (opsional):
   - "yg family friendly tp ga mahal"
3. Tunjukkan:
   - Sistem tetap memahami intent utama.
   - Tetap keluar rekomendasi yang masuk akal.

Narasi saat presentasi:

"Ini simulasi input nyata user yang ada typo, slang, dan campuran istilah. Sistem tetap robust karena pipeline ekstraksi + fallback ranking tetap berjalan."

Checklist visual:
1. Query kacau tetap diproses.
2. Rekomendasi tetap relevan.
3. Tidak crash dan tidak blank.

## Skenario 3 - Personalisasi Lintas Interaksi

Langkah:
1. Lakukan 3-4 query cepat dalam 1 sesi/token:
   - "aku suka italian di kuta"
   - "yang pizza juga boleh"
   - "cari tempat dinner romantis"
2. Lalu kirim query umum:
   - "rekomendasikan yang terbaik buat saya"
3. Buka/refresh bagian rekomendasi web.
4. Tunjukkan panel/chip insight personalisasi aktif (jika tersedia).
5. Tunjukkan hasil mulai condong ke italian/pizza/kuta/romantis.

Narasi saat presentasi:

"Di sini terlihat personalisasi berbasis histori percakapan. Setelah beberapa interaksi, query umum tetap bisa dipandu oleh preferensi user yang tersimpan pada device token."

Checklist visual:
1. Ada perubahan ranking setelah histori terbentuk.
2. Ada indikasi personalisasi di output chatbot/UI.
3. Sinkron chat dan web tetap konsisten.

## Skenario 4 - Fallback Ambigu (Opsional)

Langkah:
1. Ketik:
   - "saya lapar"
2. Tunjukkan:
   - Sistem tidak error.
   - Sistem memberi rekomendasi umum yang berguna atau mengarahkan query agar lebih spesifik.

Narasi saat presentasi:

"Untuk query ambigu, sistem menggunakan fallback agar user tetap mendapat hasil yang usable, bukan respons kosong."

## Penutup Demo

Kalimat penutup:

"Dari demo ini terlihat sistem mampu menangani query normal, input noisy, dan personalisasi berbasis histori secara konsisten. Ini mendukung tujuan proyek akhir saya: rekomendasi restoran yang lebih personal, cepat, dan kontekstual dibanding pencarian manual."

## Backup Plan Jika Demo Terganggu

1. Jika web lambat, fokus dulu ke output chatbot.
2. Jika hasil kurang relevan, gunakan query lebih terstruktur:
   - "seafood senggigi romantis"
   - "italian kuta murah"
3. Jika histori terlalu kotor, reset histori lalu ulang skenario personalisasi.
