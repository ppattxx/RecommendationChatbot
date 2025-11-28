# !/bin/bash
# Script untuk menjalankan Backend dan Frontend secara bersamaan

echo "======================================"
echo "Starting Chatbot Recommendation System"
echo "======================================"

# Start Backend
echo ""
echo "🚀 Starting Flask Backend..."
cd backend
start cmd /k "python app.py"
cd ..

# Wait a bit for backend to start
timeout /t 3 /nobreak > nul

# Start Frontend
echo ""
echo "🎨 Starting React Frontend..."
cd frontend
start cmd /k "npm run dev"
cd ..

echo ""
echo "======================================"
echo "✅ Both servers are starting!"
echo "======================================"
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:5173"
echo "======================================"
