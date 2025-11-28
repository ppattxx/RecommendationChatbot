@echo off
echo ====================================
echo Starting Chatbot Recommendation System
echo ====================================

echo.
echo Killing existing processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo.
echo Starting Backend (Flask)...
cd backend
start "Backend Flask" cmd /k "python app.py"
cd ..

timeout /t 3 /nobreak >nul

echo.
echo Starting Frontend (React)...
cd frontend
start "Frontend React" cmd /k "npm run dev"
cd ..

echo.
echo ====================================
echo Both servers should be starting...
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo ====================================
echo Press any key to exit...
pause