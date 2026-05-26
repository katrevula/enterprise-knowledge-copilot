#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

command -v python3 >/dev/null 2>&1 || {
  echo "python3 is required. Install Python 3.11+ before running this script."
  exit 1
}

command -v npm >/dev/null 2>&1 || {
  echo "npm is required. Install Node.js 20+ before running this script."
  exit 1
}

echo "Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r backend/requirements.txt -r mcp-server/requirements.txt

echo "Installing frontend dependencies..."
cd frontend
npm install --cache /private/tmp/npm-cache --proxy=false --https-proxy=false --noproxy='*'
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Add your Groq key to OPENAI_API_KEY before running chat."
else
  echo ".env already exists; leaving it unchanged."
fi

echo "Building the local HR knowledge index..."
PYTHONPATH=mcp-server python mcp-server/scripts/ingest_documents.py

echo
echo "Setup complete."
echo "Next: edit .env with OPENAI_API_KEY, then run services using RUNBOOK.md."

