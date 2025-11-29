#!/bin/bash

# Munimji.ai - Quick Start Script
# This script helps you start both backend and frontend servers

echo "🚀 Starting Munimji.ai Development Servers..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env files exist
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  backend/.env not found. Creating from example...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✅ Created backend/.env - Please edit with your credentials${NC}"
fi

if [ ! -f "Frontend/.env" ]; then
    echo -e "${YELLOW}⚠️  Frontend/.env not found. Creating from example...${NC}"
    cp Frontend/.env.example Frontend/.env
    echo -e "${GREEN}✅ Created Frontend/.env${NC}"
fi

echo ""
echo -e "${BLUE}📋 Setup Checklist:${NC}"
echo "1. Database running? (PostgreSQL)"
echo "2. Backend .env configured?"
echo "3. Frontend .env configured?"
echo ""

read -p "Press Enter to continue or Ctrl+C to cancel..."

echo ""
echo -e "${GREEN}🔧 Starting Backend (port 8001)...${NC}"
echo ""

# Start backend in background
cd backend
uvicorn backend.dashboard.app:app --reload --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!
cd ..

echo -e "${GREEN}Backend PID: $BACKEND_PID${NC}"
echo ""

# Wait a bit for backend to start
sleep 3

echo -e "${GREEN}🎨 Starting Frontend (port 5173)...${NC}"
echo ""

# Start frontend
cd Frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}✅ Both servers started!${NC}"
echo ""
echo -e "${BLUE}📍 Access URLs:${NC}"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8001"
echo "   API Docs:  http://localhost:8001/docs"
echo ""
echo -e "${YELLOW}📝 Dev Mode OTP:${NC}"
echo "   OTP will be printed in the backend console above"
echo "   Look for: [DEV MODE] OTP for +91... : xxxxxx"
echo ""
echo -e "${BLUE}🛑 To stop servers:${NC}"
echo "   Press Ctrl+C or run: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo '👋 Servers stopped'; exit" INT

# Keep script running
wait
