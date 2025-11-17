from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, List
import json
from jose import JWTError, jwt

router = APIRouter()

# JWT settings (must match auth.py)
SECRET_KEY = "Anirudh123"
ALGORITHM = "HS256"


class WebRTCSignalingManager:
    """Manages WebRTC signaling connections for video/audio calls"""
    
    def __init__(self):
        self.connections: Dict[str, Dict[int, WebSocket]] = {}  # room_id: {user_id: websocket}
    
    async def connect(self, room_id: str, user_id: int, websocket: WebSocket):
        """Add a new peer connection to the room"""
        await websocket.accept()
        
        if room_id not in self.connections:
            self.connections[room_id] = {}
        
        self.connections[room_id][user_id] = websocket
        
        # Notify other peers that a new user joined
        await self.broadcast_to_room(
            room_id, 
            {
                "type": "user-joined",
                "userId": user_id
            },
            exclude_user=user_id
        )
    
    def disconnect(self, room_id: str, user_id: int):
        """Remove peer from room"""
        if room_id in self.connections and user_id in self.connections[room_id]:
            del self.connections[room_id][user_id]
            
            # Clean up empty rooms
            if not self.connections[room_id]:
                del self.connections[room_id]
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_user: int = None):
        """Send message to all peers in room except excluded user"""
        if room_id not in self.connections:
            return
        
        for user_id, ws in self.connections[room_id].items():
            if user_id != exclude_user:
                try:
                    await ws.send_json(message)
                except Exception as e:
                    print(f"Error sending to user {user_id}: {e}")
    
    async def send_to_user(self, room_id: str, target_user_id: int, message: dict):
        """Send message to specific user in room"""
        if room_id in self.connections and target_user_id in self.connections[room_id]:
            try:
                await self.connections[room_id][target_user_id].send_json(message)
            except Exception as e:
                print(f"Error sending to user {target_user_id}: {e}")


# Global signaling manager instance
signaling_manager = WebRTCSignalingManager()


def verify_webrtc_token(token: str):
    """Verify JWT token for WebRTC connection"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        email: str = payload.get("sub")
        
        if user_id is None or email is None:
            return None
        
        return {"user_id": user_id, "email": email}
    except JWTError:
        return None


@router.websocket("/webrtc/{room_id}")
async def webrtc_signaling_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: str = Query(...)
):
    """
    WebRTC signaling endpoint for peer-to-peer video/audio calls.
    
    Handles:
    - SDP offers/answers (session descriptions)
    - ICE candidates (network path discovery)
    - Peer connection/disconnection notifications
    """
    
    # Verify authentication
    user_info = verify_webrtc_token(token)
    if not user_info:
        await websocket.close(code=4001, reason="Authentication failed")
        return
    
    user_id = user_info["user_id"]
    
    # Connect user to signaling room
    await signaling_manager.connect(room_id, user_id, websocket)
    
    try:
        while True:
            # Receive signaling message from peer
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            # Handle different signaling message types
            if message_type == "offer":
                # Peer A sends SDP offer to Peer B
                target_user_id = data.get("targetUserId")
                if target_user_id:
                    await signaling_manager.send_to_user(
                        room_id,
                        target_user_id,
                        {
                            "type": "offer",
                            "fromUserId": user_id,
                            "sdp": data.get("sdp")
                        }
                    )
            
            elif message_type == "answer":
                # Peer B sends SDP answer back to Peer A
                target_user_id = data.get("targetUserId")
                if target_user_id:
                    await signaling_manager.send_to_user(
                        room_id,
                        target_user_id,
                        {
                            "type": "answer",
                            "fromUserId": user_id,
                            "sdp": data.get("sdp")
                        }
                    )
            
            elif message_type == "ice-candidate":
                # Exchange ICE candidates for NAT traversal
                target_user_id = data.get("targetUserId")
                if target_user_id:
                    await signaling_manager.send_to_user(
                        room_id,
                        target_user_id,
                        {
                            "type": "ice-candidate",
                            "fromUserId": user_id,
                            "candidate": data.get("candidate")
                        }
                    )
            
            elif message_type == "leave":
                # Peer is leaving the call
                await signaling_manager.broadcast_to_room(
                    room_id,
                    {
                        "type": "user-left",
                        "userId": user_id
                    },
                    exclude_user=user_id
                )
                break
    
    except WebSocketDisconnect:
        pass
    
    finally:
        # Clean up on disconnect
        signaling_manager.disconnect(room_id, user_id)
        
        # Notify other peers
        await signaling_manager.broadcast_to_room(
            room_id,
            {
                "type": "user-left",
                "userId": user_id
            }
        )
