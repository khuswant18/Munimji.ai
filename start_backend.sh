#!/bin/bash
cd /Users/rajat/VScode/GitHub/Munimji.ai

# Load environment variables
export $(cat backend/.env | grep -v '^#' | xargs)

# Start uvicorn from project root using Python module
cd backend && uv run python -m uvicorn dashboard.app:app --host 0.0.0.0 --port 8001 --reload
