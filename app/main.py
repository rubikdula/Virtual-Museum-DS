from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app import models
from typing import List
import json
from .routers import auth, artifacts, pages, ai_guide, ai_enrichment

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Virtual Museum")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/media", StaticFiles(directory="app/media"), name="media")

# Include routers
app.include_router(auth.router)
app.include_router(artifacts.router)
app.include_router(pages.router)
app.include_router(ai_guide.router)
app.include_router(ai_enrichment.router)

# --- WEBSOCKET MANAGER ---
class ConnectionManager:
    def __init__(self):
        # Store active connections: {socket: user_id}
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict, sender: WebSocket):
        # Send message to everyone EXCEPT the sender (to avoid echo lag)
        for connection in self.active_connections:
            if connection != sender:
                await connection.send_text(json.dumps(message))

manager = ConnectionManager()

@app.websocket("/ws/museum")
async def websocket_endpoint(websocket: WebSocket):
    print(f"Attempting connection from {websocket.client}")
    await manager.connect(websocket)
    print(f"Connected: {websocket.client}")
    try:
        while True:
            # Wait for data from the client (their position/rotation)
            data = await websocket.receive_text()
            data_json = json.loads(data)
            
            # Broadcast this player's new position to everyone else
            await manager.broadcast(data_json, websocket)
    except WebSocketDisconnect:
        print(f"Disconnected: {websocket.client}")
        manager.disconnect(websocket)
        # Optional: Broadcast a "user left" message here if you want
