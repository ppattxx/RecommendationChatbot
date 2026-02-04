# 🍽️ Chatbot Rekomendasi Restoran Lombok

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.3+-green.svg" alt="Flask">
  <img src="https://img.shields.io/badge/React-18.2+-61DAFB.svg" alt="React">
  <img src="https://img.shields.io/badge/Vite-5.0+-646CFF.svg" alt="Vite">
  <img src="https://img.shields.io/badge/TailwindCSS-3.4+-38B2AC.svg" alt="TailwindCSS">

Sistem rekomendasi restoran berbasis chatbot yang menggunakan **Natural Language Processing (NLP)** dan **Content-Based Filtering dengan Cosine Similarity** untuk memberikan rekomendasi restoran personal di wilayah Lombok, Indonesia.</p>

## 📋 Daftar Isi

- [Fitur Utama](#-fitur-utama)

- [Teknologi](#-teknologi)

- [Penggunaan](#-penggunaan)- [Instalasi](#-instalasi)- [Arsitektur Sistem](#-arsitektur-sistem)

- [API Documentation](#-api-documentation)

### 💾 Persistence- **Responsive Design**: Optimized untuk desktop dan mobile- **Real-time Personalization**: Update rekomendasi tanpa refresh halaman- **Infinite Scroll/Pagination**: Navigasi efisien untuk 1163+ restoran- **Top 5 Priority**: Menampilkan 5 restoran terbaik dengan label "Pilihan Terbaik"### 📱 Landing Page- **Tie-Breaker Logic**: Rating dan review count sebagai pemecah skor yang sama- **Multi-Tier Boosting**: Boost score berdasarkan lokasi, cuisine, preferences, dan features- **TF-IDF Vectorization**: Transformasi teks menjadi vektor untuk perhitungan similarity- **Cosine Similarity**: Menghitung kemiripan antara query pengguna dengan data restoran### 🎯 Sistem Rekomendasi- **Context Awareness**: Mempertahankan konteks percakapan antar sesi- **Personalized Greeting**: Salam yang dipersonalisasi berdasarkan riwayat percakapan- **Intent Recognition**: Mengenali maksud pengguna untuk pencarian restoran, detail, atau bantuan- **Entity Extraction**: Mengekstrak entitas seperti lokasi, jenis masakan, harga, dan preferensi dari pesan pengguna### 🤖 Chatbot NLP## ✨ Fitur Utama- [Kontributor](#-kontributor)- [Algoritma](#-algoritma)- [Struktur Folder](#-struktur-folder)

- **Session Management**: Manajemen sesi berbasis device token
- **Chat History**: Penyimpanan riwayat chat di localStorage dan backend
- **User Preferences**: Tracking preferensi pengguna untuk personalisasi

## 🛠️ Teknologi

### Backend

| Teknologi | Versi | Deskripsi |

|-----------|-------|-----------|
| Python | 3.9+ | Bahasa pemrograman utama |
| Flask | 2.3+ | Web framework |
| SQLAlchemy | 2.0+ | ORM database |
| scikit-learn | 1.3+ | Machine learning (TF-IDF, Cosine Similarity) |
| pandas | 2.0+ | Data processing |
| SQLite | 3.x | Database |

### Frontend

| Teknologi   | Versi | Deskripsi     |
| ----------- | ----- | ------------- |
| React       | 18.2+ | UI library    |
| Vite        | 5.0+  | Build tool    |
| TailwindCSS | 3.4+  | CSS framework |
| Axios       | 1.6+  | HTTP client   |
| React Icons | 5.0+  | Icon library  |

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────────┐  │
│  │ LandingPage │  │ FloatingChatbot  │  │  RestaurantCard   │  │
│  └──────┬──────┘  └────────┬─────────┘  └─────────┬─────────┘  │
│         │                  │                      │             │
│         └──────────────────┼──────────────────────┘             │
│                            │                                    │
│              ┌─────────────┴─────────────┐                     │
│              │  PersonalizationContext   │                     │
│              └─────────────┬─────────────┘                     │
│                            │                                    │
│              ┌─────────────┴─────────────┐                     │
│              │      API Service          │                     │
│              └─────────────┬─────────────┘                     │
└────────────────────────────┼────────────────────────────────────┘
                             │
                     ┌───────┴───────┐
                     │  Vite Proxy   │
                     └───────┬───────┘
                             │
┌────────────────────────────┼────────────────────────────────────┐
│                    BACKEND (Flask)                              │
├────────────────────────────┼────────────────────────────────────┤
│              ┌─────────────┴─────────────┐                     │
│              │      Flask Routes         │                     │
│              └─────────────┬─────────────┘                     │
│                            │                                    │
│  ┌─────────────────────────┼─────────────────────────────────┐ │
│  │                         │                                  │ │
│  │  ┌──────────────┐  ┌────┴─────┐  ┌─────────────────────┐  │ │
│  │  │ chat_routes  │  │recommend │  │  preferences_routes │  │ │
│  │  └──────┬───────┘  └────┬─────┘  └──────────┬──────────┘  │ │
│  │         │               │                   │              │ │
│  └─────────┼───────────────┼───────────────────┼──────────────┘ │
│            │               │                   │                │
│  ┌─────────┴───────────────┴───────────────────┴──────────────┐ │
│  │                      SERVICES                              │ │
│  │  ┌───────────────────┐  ┌────────────────────────────────┐ │ │
│  │  │  ChatbotService   │  │ ContentBasedRecommendationEngine│ │ │
│  │  └─────────┬─────────┘  └────────────────┬───────────────┘ │ │
│  │            │                             │                 │ │
│  │            └─────────────┬───────────────┘                 │ │
│  └──────────────────────────┼─────────────────────────────────┘ │
│                             │                                   │
│              ┌──────────────┴──────────────┐                   │
│              │  SQLite Database (chatbot.db)│                   │
│              └─────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Instalasi

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm atau yarn

### Backend Setup

```bash
# Clone repository
git clone <repository-url>
cd "Chatbot Rekomendasi"

# Buat virtual environment
python -m venv venv

# Aktivasi virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Jalankan backend
cd backend
python app.py
```

Backend akan berjalan di `http://localhost:5500`

### Frontend Setup

```bash
# Buka terminal baru
cd frontend

# Install dependencies
npm install

# Jalankan development server
npm run dev
```

Frontend akan berjalan di `http://localhost:3001`

## 📖 Penggunaan

### Chatbot Commands

| Command               | Deskripsi                      |
| --------------------- | ------------------------------ |
| `help` atau `bantuan` | Menampilkan panduan penggunaan |
| `bye` atau `keluar`   | Mengakhiri percakapan          |

### Contoh Query

```
"Pizza di Kuta"
"Seafood murah di Gili Trawangan"
"Restoran romantis untuk dinner"
"Tempat makan keluarga yang santai di Senggigi"
"Japanese food dengan view pantai"
```

## 📚 API Documentation

### Chat Endpoints

| Method   | Endpoint                       | Deskripsi              |
| -------- | ------------------------------ | ---------------------- |
| `POST`   | `/api/chat`                    | Kirim pesan ke chatbot |
| `GET`    | `/api/chat/history/:sessionId` | Ambil riwayat chat     |
| `DELETE` | `/api/chat/reset`              | Reset riwayat chat     |

### Recommendations Endpoints

| Method | Endpoint                          | Deskripsi                     |
| ------ | --------------------------------- | ----------------------------- |
| `GET`  | `/api/recommendations`            | Rekomendasi dengan pagination |
| `GET`  | `/api/recommendations/top5`       | Top 5 rekomendasi             |
| `GET`  | `/api/recommendations/all-ranked` | Semua restoran dengan ranking |
| `GET`  | `/api/recommendations/categories` | Daftar kategori               |

### Preferences Endpoints

| Method | Endpoint                        | Deskripsi                |
| ------ | ------------------------------- | ------------------------ |
| `GET`  | `/api/user-preferences`         | Analisis preferensi user |
| `GET`  | `/api/user-preferences/summary` | Ringkasan preferensi     |

### Health Check

| Method | Endpoint      | Deskripsi               |
| ------ | ------------- | ----------------------- |
| `GET`  | `/api/health` | Status kesehatan sistem |

## 📁 Struktur Folder

```
Chatbot Rekomendasi/
├── 📁 backend/                 # Flask Backend
│   ├── app.py                  # Entry point Flask
│   ├── requirements.txt        # Backend dependencies
│   ├── 📁 routes/              # API route handlers
│   │   ├── chat_routes.py      # Chat endpoints
│   │   ├── recommendations_routes.py
│   │   └── preferences_routes.py
│   ├── 📁 models/              # Database models
│   │   └── database.py         # SQLAlchemy models
│   └── 📁 user_histories/      # User session storage
│
├── 📁 frontend/                # React Frontend
│   ├── package.json            # Frontend dependencies
│   ├── vite.config.js          # Vite configuration
│   ├── tailwind.config.js      # TailwindCSS config
│   └── 📁 src/
│       ├── App.jsx             # Main React component
│       ├── main.jsx            # React entry point
│       ├── 📁 components/      # Reusable components
│       │   ├── FloatingChatbot.jsx
│       │   ├── RestaurantCard.jsx
│       │   └── RestaurantRecommendations.jsx
│       ├── 📁 pages/           # Page components
│       │   └── LandingPage.jsx
│       ├── 📁 contexts/        # React contexts
│       │   └── PersonalizationContext.jsx
│       └── 📁 services/        # API services
│           └── api.js
│
├── 📁 services/                # Core business logic
│   ├── chatbot_service.py      # Chatbot logic & NLP
│   ├── recommendation_engine.py # Recommendation algorithm
│   └── device_token_service.py # Device management
│
├── 📁 utils/                   # Utility functions
│   ├── logger.py               # Logging utilities
│   ├── helpers.py              # Helper functions
│   ├── text_processing.py      # Text preprocessing
│   ├── data_loader.py          # Data loading utilities
│   ├── session_manager.py      # Session management
│   └── entity_builder.py       # Entity extraction
│
├── 📁 models/                  # Data models
│   └── data_models.py          # Pydantic/dataclass models
│
├── 📁 config/                  # Configuration
│   └── settings.py             # App settings & constants
│
├── 📁 data/                    # Dataset
│   ├── restaurants.csv         # Raw restaurant data
│   └── restaurants_entitas.csv # Processed data with entities
│
├── 📁 tests/                   # Test suite
│   ├── test_api.py
│   ├── test_chatbot_service.py
│   └── test_recommendation_engine.py
│
├── 📁 logs/                    # Application logs
├── 📁 visualizations/          # Generated charts
├── requirements.txt            # Root dependencies
├── .env                        # Environment variables
└── README.md                   # Documentation
```

## 🧮 Algoritma

### Content-Based Filtering dengan Cosine Similarity

```python
# 1. TF-IDF Vectorization
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(restaurant_texts)

# 2. Query Vectorization
query_vector = tfidf_vectorizer.transform([user_query])

# 3. Cosine Similarity
similarities = cosine_similarity(query_vector, tfidf_matrix)

# 4. Multi-Tier Boosting
boosted_score = base_score * location_boost * cuisine_boost * rating_boost

# 5. Tie-Breaker (jika score sama)
final_sort = sorted(results, key=lambda x: (
    x.similarity_score,  # Primary
    x.rating,            # Secondary
    x.review_count       # Tertiary
), reverse=True)
```

### Entity Extraction Flow

```
User Query → Tokenization → Pattern Matching → Entity Classification
     ↓
"Pizza murah di Kuta"
     ↓
{
  cuisine: ["pizza"],
  location: ["kuta"],
  price: ["murah"]
}
```

## 📊 Dataset

Dataset berisi **1163 restoran** di wilayah Lombok dengan atribut:

- `name`: Nama restoran
- `rating`: Rating (1-5)
- `review_count`: Jumlah review
- `cuisines`: Jenis masakan
- `location`: Lokasi
- `price_range`: Range harga ($, $$, $$$, $$$$)
- `features`: Fitur (WiFi, parking, dll)
- `preferences`: Kata kunci populer

## 🧪 Testing

```bash
# Jalankan semua tests
cd tests
python run_tests.py

# Test spesifik
python test_chatbot_service.py
python test_recommendation_engine.py
```

## 📝 Environment Variables

Buat file `.env` di root folder:

```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key

# Database
DATABASE_URI=sqlite:///chatbot.db

# Frontend
VITE_API_URL=/api
```

## 🤝 Kontributor

- **Developer**: [Nama Anda]
- **Institusi**: [Universitas/Institusi]
- **Pembimbing**: [Nama Pembimbing]

## 📄 Lisensi

Project ini dibuat untuk keperluan Tugas Akhir/Skripsi.

---

<p align="center">
  Made with ❤️ for Lombok Tourism
</p>
