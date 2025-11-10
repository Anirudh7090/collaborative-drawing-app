from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import List, Dict
import json
from jose import JWTError, jwt
from datetime import datetime
from sqlalchemy.orm import Session

router = APIRouter()

# JWT settings 
SECRET_KEY = "Anirudh123"  
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
        """Broadcast message to all users in room"""
        if room in self.active_connections:
            for conn_data in self.active_connections[room]:
                websocket = conn_data["websocket"]
                if websocket != exclude_websocket:
                    try:
                        await websocket.send_text(message)
                    except:
                        # Connection might be closed, will be cleaned up on disconnect
                        pass

    # ==================== CHAT & CAPTIONS HANDLING ====================
    async def broadcast_chat(self, room: str, chat_data: dict):
        """Broadcast chat messages to all users in room"""
        if room in self.active_connections:
            message = json.dumps({
                "type": "chat",
                "data": chat_data
            })
            for conn_data in self.active_connections[room]:
                try:
                    await conn_data["websocket"].send_text(message)
                except:
                    pass

    async def broadcast_caption(self, room: str, caption_data: dict):
        """Broadcast live captions to all users in room"""
        if room in self.active_connections:
            message = json.dumps({
                "type": "caption",
                "data": caption_data
            })
            for conn_data in self.active_connections[room]:
                try:
                    await conn_data["websocket"].send_text(message)
                except:
                    pass
    # ==================================================================

    async def send_room_members_update(self, room: str):
        """Send updated list of room members"""
        if room not in self.active_connections:
            return
        
        members = []
        for conn_data in self.active_connections[room]:
            user = conn_data["user"]
            members.append({
                "user_id": user.get("user_id"),
                "email": user["email"],
                "full_name": user["full_name"]
            })
        
        update_message = json.dumps({
            "type": "room_members_update",
            "members": members
        })
        await self.broadcast(room, update_message)

manager = ConnectionManager()

# ==================== WEBRTC SIGNALING ====================
# Store WebRTC connections separately
webrtc_rooms: Dict[str, Dict[str, Dict]] = {}

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
            
            # Parse incoming message
            try:
                message_data = json.loads(raw_data)
                message_type = message_data.get("type")
                
                # ==================== HANDLE DIFFERENT MESSAGE TYPES ====================
                if message_type == "chat":
                    # Handle chat messages
                    chat_data = {
                        "user": user_info["full_name"] or user_info["email"],
                        "user_id": user_info["user_id"],
                        "message": message_data.get("message", ""),
                        "timestamp": datetime.now().isoformat()
                    }
                    await manager.broadcast_chat(room_id, chat_data)
                
                elif message_type == "caption":
                    # Handle live captions
                    caption_data = {
                        "user": user_info["full_name"] or user_info["email"],
                        "user_id": user_info["user_id"],
                        "text": message_data.get("text", ""),
                        "timestamp": datetime.now().isoformat()
                    }
                    await manager.broadcast_caption(room_id, caption_data)
                
                else:
                    # Handle drawing and other messages (existing functionality)
                    message_data["sender"] = user_info["email"]
                    message_data["sender_name"] = user_info["full_name"]
                    enhanced_message = json.dumps(message_data)
                    await manager.broadcast(room_id, enhanced_message, exclude_websocket=websocket)
                # ==============================================================================
                
            except json.JSONDecodeError:
                # If not JSON, treat as regular message
                enhanced_message = raw_data
                await manager.broadcast(room_id, enhanced_message, exclude_websocket=websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
        # Send updated member list after someone leaves
        await manager.send_room_members_update(room_id)


# ==================== WEBRTC VIDEO CALL SIGNALING ====================
@router.websocket("/webrtc/{room_id}")
async def webrtc_signaling(websocket: WebSocket, room_id: str, token: str = Query(...)):
    """WebRTC signaling endpoint for video/audio calls"""
    try:
        # Verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user_email = payload.get("sub")
        user_name = payload.get("fullName", user_email)
        
        if not user_id or not user_email:
            await websocket.close(code=1008)
            return
            
    except JWTError:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    
    # Initialize room if needed
    if room_id not in webrtc_rooms:
        webrtc_rooms[room_id] = {}
    
    # Add user to room
    webrtc_rooms[room_id][user_email] = {
        "websocket": websocket,
        "userName": user_name
    }
    
    try:
        # Notify others that user joined
        for uid, client_data in webrtc_rooms[room_id].items():
            if uid != user_email:
                try:
                    await client_data["websocket"].send_json({
                        "type": "user-joined",
                        "userId": user_email,
                        "userName": user_name
                    })
                except:
                    pass
        
        # Handle incoming messages
        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type")
            
            if msg_type == "join":
                # User sent join message with their info
                webrtc_rooms[room_id][user_email]["userName"] = message.get("userName", user_name)
                continue
            
            if msg_type == "leave":
                # User is leaving
                user_leaving_name = message.get("userName", user_name)
                # Notify others
                for uid, client_data in webrtc_rooms[room_id].items():
                    if uid != user_email:
                        try:
                            await client_data["websocket"].send_json({
                                "type": "user-left",
                                "userId": user_email,
                                "userName": user_leaving_name
                            })
                        except:
                            pass
                break
            
            # Forward signaling messages (offer, answer, ice-candidate)
            target_user_id = message.get("targetUserId")
            if target_user_id and target_user_id in webrtc_rooms[room_id]:
                try:
                    forward_msg = {
                        "type": msg_type,
                        "fromUserId": user_email,
                        "userName": webrtc_rooms[room_id][user_email].get("userName", user_name),
                        "sdp": message.get("sdp"),
                        "candidate": message.get("candidate")
                    }
                    await webrtc_rooms[room_id][target_user_id]["websocket"].send_json(forward_msg)
                except:
                    pass
                    
    except WebSocketDisconnect:
        pass
    finally:
        # Clean up
        if room_id in webrtc_rooms and user_email in webrtc_rooms[room_id]:
            leaving_user_name = webrtc_rooms[room_id][user_email].get("userName", user_name)
            del webrtc_rooms[room_id][user_email]
            
            # Notify others
            for uid, client_data in webrtc_rooms[room_id].items():
                try:
                    await client_data["websocket"].send_json({
                        "type": "user-left",
                        "userId": user_email,
                        "userName": leaving_user_name
                    })
                except:
                    pass
            
            # Clean up empty room
            if not webrtc_rooms[room_id]:
                del webrtc_rooms[room_id]
