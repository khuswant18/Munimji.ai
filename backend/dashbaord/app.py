# backend/dashboard/app.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI(
    title="Munimji Dashboard API",
    description="API for shopkeeper dashboard with Twilio OTP authentication",
    version="1.0.0"
)

# CORS Configuration - allows frontend to make requests
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default
    "http://localhost:5174",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

# Add production domain if FRONTEND_URL is set
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "munimji-dashboard"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("DASHBOARD_PORT", 8001))
    uvicorn.run("backend.dashbaord.app:app", host="0.0.0.0", port=port, reload=True)