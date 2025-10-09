from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.db import SessionLocal, CanvasSnapshot, Room
from app.routers.auth import get_current_user  # Import JWT dependency
from pydantic import BaseModel

router = APIRouter(
    prefix="/canvas",
    tags=["Canvas Persistence"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request model for saving a snapshot
class CanvasSnapshotRequest(BaseModel):
    room_id: str
    state_json: str

# Request model for saving canvas state
class CanvasSaveRequest(BaseModel):
    room_id: str
    state_json: str

# ---- OWNER-ONLY CLEAR CANVAS ----
@router.post("/clear/{room_id}", status_code=status.HTTP_200_OK)
def clear_canvas(
    room_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == room_id, Room.is_active == True).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Only the room owner can clear the canvas.")

    # "Clear" means append a new empty snapshot for that room
    blank_state = "[]"
    new_snapshot = CanvasSnapshot(room_id=room_id, state_json=blank_state)
    db.add(new_snapshot)
    db.commit()
    return {"message": "Canvas cleared.", "room_id": room_id, "snapshot_id": new_snapshot.id}

# ---- SAVE SNAPSHOT (CREATE new version) - PROTECTED ----
@router.post("/snapshot", status_code=status.HTTP_201_CREATED)
def save_canvas_snapshot(
    payload: CanvasSnapshotRequest, 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    snapshot = CanvasSnapshot(room_id=payload.room_id, state_json=payload.state_json)
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return {
        "message": "Snapshot saved.",
        "snapshot_id": snapshot.id,
        "created_at": snapshot.created_at,
        "saved_by": current_user["email"]
    }

# ---- LIST SNAPSHOTS FOR ROOM - PROTECTED ----
@router.get("/snapshots/{room_id}", status_code=status.HTTP_200_OK)
def list_snapshots(
    room_id: str, 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    snapshots = db.query(CanvasSnapshot).filter(CanvasSnapshot.room_id == room_id).order_by(CanvasSnapshot.created_at.desc()).all()
    return [
        {
            "snapshot_id": snap.id,
            "created_at": snap.created_at,
            "room_id": snap.room_id
        }
        for snap in snapshots
    ]

# ---- LOAD SPECIFIC SNAPSHOT BY ID - PROTECTED ----
@router.get("/snapshot/{snapshot_id}", status_code=status.HTTP_200_OK)
def load_snapshot(
    snapshot_id: int, 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    snapshot = db.query(CanvasSnapshot).filter(CanvasSnapshot.id == snapshot_id).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found.")
    return {
        "snapshot_id": snapshot.id,
        "room_id": snapshot.room_id,
        "state_json": snapshot.state_json,
        "created_at": snapshot.created_at
    }

# ---- SAVE CURRENT CANVAS STATE - PROTECTED ----
@router.post("/save", status_code=status.HTTP_201_CREATED)
def save_canvas_state(
    payload: CanvasSaveRequest, 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(CanvasSnapshot).filter(CanvasSnapshot.room_id == payload.room_id).order_by(CanvasSnapshot.created_at.desc()).first()
    if existing:
        existing.state_json = payload.state_json
        db.commit()
        return {"message": "Canvas state updated", "room_id": payload.room_id}
    else:
        new_state = CanvasSnapshot(room_id=payload.room_id, state_json=payload.state_json)
        db.add(new_state)
        db.commit()
        return {"message": "Canvas state saved", "room_id": payload.room_id}

# ---- LOAD CURRENT CANVAS STATE - PROTECTED ----
@router.get("/load/{room_id}", status_code=status.HTTP_200_OK)
def load_canvas_state(
    room_id: str, 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    latest = db.query(CanvasSnapshot).filter(CanvasSnapshot.room_id == room_id).order_by(CanvasSnapshot.created_at.desc()).first()
    if not latest:
        return {"state_json": "[]", "room_id": room_id}
    return {
        "state_json": latest.state_json,
        "room_id": latest.room_id,
        "last_updated": latest.created_at
    }
