@echo off
REM Quick Start Script for Plant Disease Detection System (Windows)
REM Usage: start.bat [frontend|backend|all|docker|test]

setlocal enabledelayedexpansion

if "%1"=="" (
    set COMMAND=all
) else (
    set COMMAND=%1
)

if /i "%COMMAND%"=="frontend" (
    echo Starting frontend...
    call npm install
    call npm run dev
) else if /i "%COMMAND%"=="backend" (
    echo Starting backend...
    cd backend
    if not exist ".venv" (
        echo Creating virtual environment...
        python -m venv .venv
    )
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
    python app.py
) else if /i "%COMMAND%"=="all" (
    echo Starting both frontend and backend...
    echo Starting backend in new window...
    start cmd /k "cd backend && .venv\Scripts\activate.bat && python app.py"
    timeout /t 2 /nobreak
    echo Starting frontend...
    call npm install
    call npm run dev
) else if /i "%COMMAND%"=="docker" (
    echo Starting with Docker Compose...
    cd backend
    docker-compose up
) else if /i "%COMMAND%"=="test" (
    echo Running tests...
    cd backend
    call .venv\Scripts\activate.bat
    pytest -q
) else (
    echo Usage: start.bat [frontend^|backend^|all^|docker^|test]
    exit /b 1
)
