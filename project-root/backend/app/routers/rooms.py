from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.db import SessionLocal, Room, UserRoom, UserRole
from app.models.users import User
from app.routers.auth import get_current_user
from pydantic import BaseModel
import uuid

router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic schemas
class RoomCreateRequest(BaseModel):
    name: str
    description: str | None = None
    max_users: int = 10

class JoinRoomRequest(BaseModel):
    room_id: str

class RemoveMemberRequest(BaseModel):
    room_id: str
    user_id: int

# ---- CREATE ROOM ----
@router.post("/create", status_code=201)
def create_room(
    room_data: RoomCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_room_id = f"room-{str(uuid.uuid4())[:8]}"
    room = Room(
        id=new_room_id,
        name=room_data.name,
        description=room_data.description,
        owner_id=current_user["user_id"],
        max_users=room_data.max_users,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    owner_membership = UserRoom(
        user_id=current_user["user_id"],
        room_id=new_room_id,
        role=UserRole.OWNER
    )
    db.add(owner_membership)
    db.commit()
    return {
        "room_id": room.id,
        "name": room.name,
        "description": room.description,
        "owner_id": room.owner_id
    }

# ---- JOIN ROOM ----
@router.post("/join", status_code=200)
def join_room(
    join_data: JoinRoomRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == join_data.room_id, Room.is_active == True).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    membership = db.query(UserRoom).filter(
        UserRoom.room_id == join_data.room_id,
        UserRoom.user_id == current_user["user_id"],
        UserRoom.is_active == True
    ).first()
    if membership:
        return {"message": "Already a member", "room_id": room.id}

    members_count = db.query(UserRoom).filter(UserRoom.room_id == join_data.room_id, UserRoom.is_active == True).count()
    if members_count >= room.max_users:
        raise HTTPException(status_code=403, detail="Room is full")

    new_member = UserRoom(
        user_id=current_user["user_id"],
        room_id=join_data.room_id,
        role=UserRole.MEMBER
    )
    db.add(new_member)
    db.commit()
    return {"message": "Joined", "room_id": room.id}

# ---- LEAVE ROOM ----
@router.post("/leave/{room_id}", status_code=200)
def leave_room(
    room_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    membership = db.query(UserRoom).filter(
        UserRoom.room_id == room_id,
        UserRoom.user_id == current_user["user_id"],
        UserRoom.is_active == True,
    ).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    membership.is_active = False
    db.commit()
    return {"message": "Left room", "room_id": room_id}

# ---- DELETE ROOM (OWNER ONLY) ----
@router.delete("/{room_id}", status_code=200)
def delete_room(
    room_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == room_id, Room.is_active == True).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Only the room owner can delete this room.")
    room.is_active = False
    memberships = db.query(UserRoom).filter(UserRoom.room_id == room_id).all()
    for m in memberships:
        m.is_active = False
    db.commit()
    return {"message": "Room deleted successfully."}

# ---- REMOVE MEMBER (OWNER ONLY) ----
@router.post("/remove_member", status_code=200)
def remove_member(
    req: RemoveMemberRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == req.room_id, Room.is_active == True).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Only the owner can remove a member.")
    if current_user["user_id"] == req.user_id:
        raise HTTPException(status_code=403, detail="Owner cannot remove themselves.")
    membership = db.query(UserRoom).filter(
        UserRoom.room_id == req.room_id,
        UserRoom.user_id == req.user_id,
        UserRoom.is_active == True
    ).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    membership.is_active = False
    db.commit()
    return {"message": "Member removed successfully."}

# ---- CLEAR CANVAS (OWNER ONLY, calls drawings router logic) ----
@router.post("/clear_canvas/{room_id}", status_code=200)
def clear_canvas(
    room_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == room_id, Room.is_active == True).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Only owner can clear the canvas.")
    # The actual canvas clearing will be done in drawings.py (next step)
    # Here, you can call/emit logic or set flag for canvas reset
    return {"message": "Canvas clear requested. (Implement in drawings.py)."}

# ---- LIST ROOMS FOR CURRENT USER ----
@router.get("/my", status_code=200)
def list_my_rooms(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    memberships = db.query(UserRoom).filter(
        UserRoom.user_id == current_user["user_id"], UserRoom.is_active == True
    ).all()
    result = []
    for m in memberships:
        room = db.query(Room).filter(Room.id == m.room_id).first()
        result.append({
            "room_id": room.id,
            "name": room.name,
            "role": m.role.value,
            "owner_id": room.owner_id
        })
    return result

# ---- GET ROOM DETAILS ----
@router.get("/{room_id}", status_code=200)
def get_room_details(
    room_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    members = db.query(UserRoom).filter(UserRoom.room_id == room_id, UserRoom.is_active == True).all()
    return {
        "room_id": room.id,
        "name": room.name,
        "owner_id": room.owner_id,
        "description": room.description,
        "max_users": room.max_users,
        "members": [
            {
                "user_id": m.user_id,
                "role": m.role.value
            }
            for m in members
        ],
        "is_active": room.is_active,
        "created_at": room.created_at
    }
