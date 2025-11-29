# backend/dashboard/app.py
import os
from fastapi import FastAPI, Query, Request
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
    "http://localhost:3001",  # Added for current frontend port
    "http://localhost:5173",  # Vite default
    "http://localhost:5174",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",  # Added for current frontend port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "https://munimji-ai.vercel.app",  # Production frontend
    "https://*.vercel.app",  # Vercel preview deployments
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


# WhatsApp Webhook Verification (Meta requires this)
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "my_verify_token")

@app.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """WhatsApp webhook verification endpoint"""
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    return {"error": "Verification failed"}, 403


@app.post("/webhook")
async def webhook_handler(request: Request):
    """Handle incoming WhatsApp messages"""
    # For now, just acknowledge receipt
    # Full WhatsApp handling can be added later
    body = await request.json()
    print(f"📩 Webhook received: {body}")
    return {"status": "received"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("DASHBOARD_PORT", 8001))
    uvicorn.run("backend.dashboard.app:app", host="0.0.0.0", port=port, reload=True)