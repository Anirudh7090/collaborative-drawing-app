from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import List, Dict
import json
from jose import JWTError, jwt

router = APIRouter()

# JWT settings (same as in auth.py)
SECRET_KEY = "YOUR_SUPER_SECRET_KEY"  # Must match auth.py
ALGORITHM = "HS256"

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[Dict]] = {}  # Store connection + user info

    async def connect(self, room: str, websocket: WebSocket, user_info: dict):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        
        connection_data = {
            "websocket": websocket,
            "user": user_info
        }
        self.active_connections[room].append(connection_data)
        
        # Send welcome message with current room members
        await self.send_room_members_update(room)

    def disconnect(self, room: str, websocket: WebSocket):
        if room in self.active_connections:
            self.active_connections[room] = [
                conn for conn in self.active_connections[room] 
                if conn["websocket"] != websocket
            ]
            if len(self.active_connections[room]) == 0:
                del self.active_connections[room]

    async def broadcast(self, room: str, message: str, exclude_websocket: WebSocket = None):
        if room in self.active_connections:
            for conn_data in self.active_connections[room]:
                websocket = conn_data["websocket"]
                if websocket != exclude_websocket:
                    try:
                        await websocket.send_text(message)
                    except:
                        # Connection might be closed, will be cleaned up on disconnect
                        pass

    async def send_room_members_update(self, room: str):
        if room not in self.active_connections:
            return
            
        members = []
        for conn_data in self.active_connections[room]:
            user = conn_data["user"]
            members.append({
                "email": user["email"],
                "full_name": user["full_name"]
            })
        
        update_message = json.dumps({
            "type": "room_members_update",
            "members": members
        })
        
        await self.broadcast(room, update_message)

manager = ConnectionManager()

def verify_websocket_token(token: str):
    """Verify JWT token for WebSocket connection"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        email: str = payload.get("sub")
        full_name: str = payload.get("fullName")
        if user_id is None or email is None:
            return None
        return {"user_id": user_id, "email": email, "full_name": full_name}
    except JWTError:
        return None

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, token: str = Query(...)):
    # Verify JWT token
    user_info = verify_websocket_token(token)
    if not user_info:
        await websocket.close(code=4001, reason="Authentication failed")
        return
    
    await manager.connect(room_id, websocket, user_info)
    
    try:
        while True:
            raw_data = await websocket.receive_text()
            
            # Parse and add user info to messages
            try:
                message_data = json.loads(raw_data)
                message_data["sender"] = user_info["email"]
                message_data["sender_name"] = user_info["full_name"]
                enhanced_message = json.dumps(message_data)
            except:
                enhanced_message = raw_data
            
            # Broadcast to all other users in the room (excluding sender)
            await manager.broadcast(room_id, enhanced_message, exclude_websocket=websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
        # Send updated member list after someone leaves
        await manager.send_room_members_update(room_id)
