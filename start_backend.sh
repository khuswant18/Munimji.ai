#!/bin/bash
cd /Users/rajat/VScode/GitHub/Munimji.ai
source backend/.venv/bin/activate

# Load environment variables
export $(cat backend/.env | grep -v '^#' | xargs)

# Start uvicorn
uvicorn backend.dashbaord.app:app --host 0.0.0.0 --port 8002 --reload
