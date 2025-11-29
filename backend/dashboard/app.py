# backend/dashboard/app.py
import os
import logging
from fastapi import FastAPI, Query, Request, BackgroundTasks, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse
from .routes import router

LOG = logging.getLogger("munimji.dashboard")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Munimji Dashboard API",
    description="API for shopkeeper dashboard and WhatsApp webhook",
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


# ==================== WhatsApp Webhook ====================
# Import WhatsApp handlers
try:
    from backend.whatsapp.handlers import webhook_verify, webhook_receiver, get_db
    from backend.whatsapp.utils import send_text_message_async
    WHATSAPP_ENABLED = True
    LOG.info("✅ WhatsApp handlers loaded successfully")
except ImportError as e:
    WHATSAPP_ENABLED = False
    LOG.warning(f"⚠️ WhatsApp handlers not available: {e}")


@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """WhatsApp webhook verification endpoint"""
    if WHATSAPP_ENABLED:
        return await webhook_verify(hub_mode, hub_verify_token, hub_challenge)
    
    # Fallback verification
    VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "my_verify_token")
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge or "", status_code=200)
    return JSONResponse({"error": "Verification failed"}, status_code=403)


@app.post("/webhook")
async def receive_webhook(
    request: Request, 
    background_tasks: BackgroundTasks, 
    x_hub_signature_256: str = Header(None)
):
    """Handle incoming WhatsApp messages"""
    if WHATSAPP_ENABLED:
        # Get DB session
        from backend.chatbot_backend.db.session import SessionLocal
        db = SessionLocal()
        try:
            return await webhook_receiver(request, background_tasks, x_hub_signature_256, db)
        finally:
            db.close()
    
    # Fallback: just log and acknowledge
    body = await request.json()
    LOG.info(f"📩 Webhook received (handlers not loaded): {body}")
    return JSONResponse({"status": "received"}, status_code=200)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("DASHBOARD_PORT", 8001))
    uvicorn.run("backend.dashboard.app:app", host="0.0.0.0", port=port, reload=True)