# backend/dashboard/app.py
from fastapi import FastAPI
from .routes import router

app = FastAPI(title="Munimji Dashboard API")

app.include_router(router)