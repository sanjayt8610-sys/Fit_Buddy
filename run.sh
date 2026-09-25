#!/usr/bin/env bash
# =======================================================
#   FITBUDDY - AI Fitness Plan Generator
#   macOS / Linux Startup Script
# =======================================================

set -e

echo "======================================================="
echo "  FITBUDDY - AI Fitness Plan Generator"
echo "======================================================="
echo ""

if [ ! -d ".venv" ]; then
    echo "[1/3] Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "[2/3] Activating virtual environment & checking dependencies..."
source .venv/bin/activate
pip install -r requirements.txt --quiet

if [ ! -f ".env" ]; then
    echo "[2.5/3] Generating .env configuration from .env.example..."
    cp .env.example .env
fi

echo "[3/3] Starting FitBuddy application on http://127.0.0.1:8000 ..."
echo ""
echo "======================================================="
echo "  Application URLs:"
echo "  - Main Web App:       http://127.0.0.1:8000"
echo "  - Admin Portal:       http://127.0.0.1:8000/admin/login"
echo "  - API Docs (Swagger): http://127.0.0.1:8000/docs"
echo "======================================================="
echo ""

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
