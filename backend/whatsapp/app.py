# munimji/whatsapp_adapter.py
import os
import logging
from fastapi import FastAPI, Query, Depends, Request, BackgroundTasks, Header
from dotenv import load_dotenv
from .handlers import get_db, webhook_verify, webhook_receiver, send_text_demo

load_dotenv()
LOG = logging.getLogger("munimji.whatsapp_adapter")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Munimji WhatsApp Adapter")


@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    return await webhook_verify(hub_mode, hub_verify_token, hub_challenge)

@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks, x_hub_signature_256: str = Header(None), db=Depends(get_db)):
    return await webhook_receiver(request, background_tasks, x_hub_signature_256, db)

@app.post("/send_text_demo")
async def demo_send_text(body):
    return await send_text_demo(body)

def main():
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    uvicorn.run("backend.whatsapp.app:app", host="0.0.0.0", port=port, reload=(os.getenv("DEV_RELOAD","false").lower()=="true"))

if __name__ == "__main__":
    main()
