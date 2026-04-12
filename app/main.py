from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models
from typing import List
import json
import os
from .routers import auth, artifacts, pages, ai_guide, ai_enrichment, museum

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Virtual Museum")

# --- CORS ---
# Set ALLOWED_ORIGIN in Railway environment variables for your production frontend URL.
# Defaults to "*" (open) which is fine while there is no separate frontend domain.
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
if _raw_origins == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [o.strip() for o in _raw_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/media", StaticFiles(directory="app/media"), name="media")

# Include routers
app.include_router(auth.router)
app.include_router(artifacts.router)
app.include_router(museum.router)
app.include_router(pages.router)
app.include_router(ai_guide.router)
app.include_router(ai_enrichment.router)

# --- WEBSOCKET MANAGER ---
class ConnectionManager:
    def __init__(self):
        # Store active connections: {room_id: [WebSocket]}
        self.rooms: dict = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = []
        self.rooms[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.rooms:
            if websocket in self.rooms[room_id]:
                self.rooms[room_id].remove(websocket)
            if not self.rooms[room_id]:
                del self.rooms[room_id]

    async def broadcast(self, message: dict, sender: WebSocket, room_id: str):
        if room_id in self.rooms:
            for connection in self.rooms[room_id]:
                if connection != sender:
                    await connection.send_text(json.dumps(message))

manager = ConnectionManager()

@app.websocket("/ws/museum/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    print(f"Attempting connection to room {room_id}")
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            await manager.broadcast(data_json, websocket, room_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
