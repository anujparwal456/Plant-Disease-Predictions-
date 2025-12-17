#!/bin/bash
# Quick Start Script for Plant Disease Detection System
# Usage: bash start.sh [frontend|backend|all]

set -e

COMMAND=${1:-all}

case "$COMMAND" in
  frontend)
    echo "Starting frontend..."
    npm install
    npm run dev
    ;;
  backend)
    echo "Starting backend..."
    cd backend
    if [ ! -d ".venv" ]; then
      echo "Creating virtual environment..."
      python -m venv .venv
    fi
    source .venv/bin/activate
    pip install -r requirements.txt
    python app.py
    ;;
  all)
    echo "Starting both frontend and backend..."
    # Start backend in background
    (cd backend && bash -c '
      if [ ! -d ".venv" ]; then
        python -m venv .venv
      fi
      source .venv/bin/activate
      pip install -r requirements.txt
      python app.py
    ') &
    BACKEND_PID=$!
    echo "Backend started (PID: $BACKEND_PID)"
    
    # Start frontend
    sleep 2
    npm install
    npm run dev
    
    # Cleanup on exit
    trap "kill $BACKEND_PID" EXIT
    ;;
  docker)
    echo "Starting with Docker Compose..."
    cd backend
    docker-compose up
    ;;
  test)
    echo "Running tests..."
    cd backend
    source .venv/bin/activate
    pytest -q
    ;;
  *)
    echo "Usage: bash start.sh [frontend|backend|all|docker|test]"
    exit 1
    ;;
esac
