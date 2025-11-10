from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import trajetos, devices
from app.dependencies import get_mqtt_manager
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import engine
    import app.models as models

    models.Base.metadata.create_all(bind=engine)

    mqtt_manager = get_mqtt_manager()
    await mqtt_manager.connect()

    try:
        yield
    finally:
        await mqtt_manager.disconnect()

app = FastAPI(title="ESP32 Car Control API", version="1.0.0", lifespan=lifespan, docs_url="/docs")
app.include_router(trajetos.router)
app.include_router(devices.router)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0"
    }
