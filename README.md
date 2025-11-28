# Chatbot Rekomendasi Restoran - Monorepo

Aplikasi **Recommendation Chatbot** dengan metode **Content-Based Filtering** yang mengintegrasikan Flask Backend dan React Frontend dalam arsitektur Monorepo.

## 🏗️ Struktur Project

```
/project-root
├── /backend                    # Flask Backend
│   ├── app.py                 # Entry point Flask
│   ├── /models                # Database models (SQLAlchemy)
│   │   └── database.py        # ChatHistory, UserSession
│   ├── /routes                # API endpoints
│   │   ├── chat_routes.py     # POST /api/chat
│   │   └── preferences_routes.py  # GET /api/user-preferences
│   └── requirements.txt       # Python dependencies
│
├── /frontend                   # React Frontend
│   ├── /src
│   │   ├── /components        # ChatWidget, PreferenceChart
│   │   │   ├── FloatingChatbot.jsx
│   │   │   └── PreferenceCharts.jsx
│   │   ├── /pages             # LandingPage
│   │   │   └── LandingPage.jsx
│   │   ├── /services          # API client
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json           # React (Vite)
│   └── tailwind.config.js     # Tailwind CSS config
│
├── /services                   # Existing chatbot logic
│   ├── chatbot_service.py
│   └── recommendation_engine.py
│
├── /config                     # Configuration files
├── /data                       # Restaurant data (CSV)
└── /utils                      # Helper functions
```

## 🚀 Cara Menjalankan

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm atau yarn

### 1. Setup Backend (Flask)

```bash
# Navigate ke folder backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Jalankan Flask server
python app.py
```

Backend akan berjalan di: **http://localhost:5000**

**API Endpoints:**

- `POST /api/chat` - Kirim pesan ke chatbot
- `GET /api/user-preferences` - Analisis preferensi user
- `GET /api/health` - Health check

### 2. Setup Frontend (React + Vite)

```bash
# Navigate ke folder frontend
cd frontend

# Install dependencies
npm install

# Jalankan development server
npm run dev
```

Frontend akan berjalan di: **http://localhost:5173**

### 3. Akses Aplikasi

Buka browser dan akses:

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:5000

## 📋 Core Features

### Backend (Flask + SQLite)

✅ **Database Schema:**

- `ChatHistory` - Menyimpan riwayat percakapan (user_message, bot_response, timestamp, entities)
- `UserSession` - Tracking user sessions

✅ **API Endpoints:**

- `POST /api/chat` - Menerima pesan user dan membalas menggunakan logika chatbot
- `GET /api/user-preferences` - Menganalisis history chat dan mengembalikan statistik preferensi

✅ **CORS Configuration:**

- Mengizinkan frontend (port 5173) berkomunikasi dengan backend (port 5000)

### Frontend (React + Tailwind CSS)

✅ **Landing Page:**

- Hero section yang elegan
- Cards statistik (Total Conversations, Favorite Cuisine, Location, dll)
- **"Analisis Minat Anda"** section dengan data dari `/api/user-preferences`
- Visualisasi data (Bar Chart, Pie Chart) menggunakan Recharts

✅ **Floating Chatbot:**

- Widget chat di pojok kanan bawah
- Bisa dibuka/tutup
- Real-time communication dengan backend via axios
- Local storage untuk device token

## 🔧 Tech Stack

### Backend

- **Flask** - Web framework
- **SQLAlchemy** - ORM database
- **Flask-CORS** - Cross-origin resource sharing
- **SQLite** - Database
- Existing chatbot logic (Content-Based Filtering)

### Frontend

- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **React Icons** - Icon library

## 📊 Database Schema

### ChatHistory Table

```sql
- id (Integer, Primary Key)
- session_id (String, Indexed)
- device_token (String, Indexed)
- user_message (Text)
- bot_response (Text)
- timestamp (DateTime)
- extracted_cuisine (String)
- extracted_location (String)
- extracted_mood (String)
- extracted_price (String)
```

### UserSession Table

```sql
- id (Integer, Primary Key)
- session_id (String, Unique, Indexed)
- device_token (String, Indexed)
- created_at (DateTime)
- last_activity (DateTime)
- is_active (Boolean)
```

## 🎯 API Usage Examples

### POST /api/chat

```javascript
fetch("http://localhost:5000/api/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    message: "pizza enak di Kuta",
    session_id: "session_123",
    device_token: "dev_xyz",
  }),
});
```

### GET /api/user-preferences

```javascript
fetch("http://localhost:5000/api/user-preferences?device_token=dev_xyz");
```

## 🎨 Features Highlights

1. **Personalized Recommendations** - Content-Based Filtering algorithm
2. **User Preference Analysis** - Track dan visualisasi preferensi user
3. **Real-time Chat** - Instant communication via WebSocket-like experience
4. **Beautiful UI** - Modern, responsive design dengan Tailwind CSS
5. **Data Visualization** - Interactive charts dengan Recharts
6. **Session Management** - Persistent sessions dengan device tokens

## 📝 Development Notes

- Backend menggunakan existing chatbot logic dari `services/chatbot_service.py`
- Frontend memiliki fallback untuk handle backend offline
- Database SQLite akan otomatis dibuat saat pertama kali menjalankan backend
- CORS sudah dikonfigurasi untuk development (localhost:5173)

## 🔒 Security Notes

- Untuk production, ganti `SECRET_KEY` di environment variables
- Update CORS origins untuk production domains
- Implementasikan rate limiting untuk API endpoints
- Tambahkan authentication/authorization jika diperlukan

## 👨‍💻 Author

**Tugas Akhir - Recommendation Chatbot**
Content-Based Filtering System

---

**Happy Coding! 🚀**
