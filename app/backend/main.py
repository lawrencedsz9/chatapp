from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import sys
import os
import asyncio
from datetime import datetime

# Add the parent directory to the path so we can import from app.common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.cipher import encrypt, decrypt

app = FastAPI(title="Secure Chat App")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Message(BaseModel):
    sender: str
    content: str
    is_encrypted: bool = True
    rails: Optional[int] = 3
    timestamp: Optional[str] = None

class User(BaseModel):
    username: str

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.message_history: List[Message] = []
    
    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections[username] = websocket
    
    def disconnect(self, username: str):
        if username in self.active_connections:
            del self.active_connections[username]
    
    async def send_personal_message(self, message: Message, username: str):
        if username in self.active_connections:
            await self.active_connections[username].send_json(message.dict())
    
    async def broadcast(self, message: Message):
        self.message_history.append(message)
        for username, connection in self.active_connections.items():
            await connection.send_json(message.dict())

manager = ConnectionManager()

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to the Secure Chat API"}

@app.get("/messages")
async def get_messages():
    return manager.message_history

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket, username)
    try:
        # Send message history to new users
        for message in manager.message_history:
            await manager.send_personal_message(message, username)
        
        # Welcome message
        welcome_msg = Message(
            sender="System",
            content=f"Welcome, {username}! You are now connected.",
            is_encrypted=False,
            timestamp=datetime.now().isoformat()
        )
        await manager.send_personal_message(welcome_msg, username)
        
        # Announce new user
        announcement = Message(
            sender="System",
            content=f"{username} has joined the chat.",
            is_encrypted=False,
            timestamp=datetime.now().isoformat()
        )
        await manager.broadcast(announcement)
        
        # Main message loop
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message = Message(
                sender=username,
                content=message_data["content"],
                is_encrypted=message_data.get("is_encrypted", True),
                rails=message_data.get("rails", 3),
                timestamp=datetime.now().isoformat()
            )
            
            # Encrypt the message if needed
            if message.is_encrypted:
                message.content = encrypt(message.content, message.rails)
            
            await manager.broadcast(message)
            
    except WebSocketDisconnect:
        manager.disconnect(username)
        # Announce user left
        announcement = Message(
            sender="System",
            content=f"{username} has left the chat.",
            is_encrypted=False,
            timestamp=datetime.now().isoformat()
        )
        await manager.broadcast(announcement)

# Run with: uvicorn app.backend.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
