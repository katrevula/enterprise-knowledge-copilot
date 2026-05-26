param(
    [switch]$SkipIndex
)

$ErrorActionPreference = "Stop"
$RootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RootDir

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "python is required. Install Python 3.11+ before running this script."
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Error "npm is required. Install Node.js 20+ before running this script."
}

Write-Host "Creating Python virtual environment..."
python -m venv .venv

Write-Host "Installing Python dependencies..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\pip.exe install -r backend\requirements.txt -r mcp-server\requirements.txt

Write-Host "Installing frontend dependencies..."
Push-Location frontend
npm install
Pop-Location

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example. Add your Groq key to OPENAI_API_KEY before running chat."
} else {
    Write-Host ".env already exists; leaving it unchanged."
}

if (-not $SkipIndex) {
    Write-Host "Building the local HR knowledge index..."
    $env:PYTHONPATH = "mcp-server"
    & .\.venv\Scripts\python.exe mcp-server\scripts\ingest_documents.py
}

Write-Host ""
Write-Host "Setup complete."
Write-Host "Next: edit .env with OPENAI_API_KEY, then run services using RUNBOOK.md."

