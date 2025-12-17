@echo off
cd /d "a:\Downloads\gouri project\backend"
call .venv\Scripts\activate.bat
set GEMINI_API_KEY=AIzaSyCSPkavnaWhdOBpO4Co_rl7muKDZRZS_p0
python app.py
pause
