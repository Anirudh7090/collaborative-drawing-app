from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, func, Boolean, Enum
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import os
from dotenv import load_dotenv
import enum


# Load environment variables from .env file
load_dotenv()


# Get database URL from environment variable or fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:Anirudh@localhost:5432/canvus"
)


# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)


# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class
Base = declarative_base()


# ---- ENUM FOR USER ROLES ----
class UserRole(enum.Enum):
    OWNER = "owner"      # Room creator, full permissions
    MEMBER = "member"    # Regular room participant


# ---- MODEL FOR CANVAS SNAPSHOTS (VERSIONING) ----
class CanvasSnapshot(Base):
    __tablename__ = "canvas_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String, ForeignKey("rooms.id"), nullable=False, index=True)
    state_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    room = relationship("Room", back_populates="snapshots")
    creator = relationship("User")


# ==================== NEW: CHAT MESSAGE MODEL ====================
class ChatMessage(Base):
    """Store chat messages for each room"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String, ForeignKey("rooms.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    room = relationship("Room", back_populates="chat_messages")
    user = relationship("User", back_populates="chat_messages")
# ==================================================================


# ---- MODEL FOR ROOMS ----
class Room(Base):
    __tablename__ = "rooms"
    id = Column(String, primary_key=True, index=True)  # Custom room ID like "room-123"
    name = Column(String, nullable=False)              # Human-readable room name
    description = Column(Text, nullable=True)          # Optional room description
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)          # Can deactivate rooms
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    max_users = Column(Integer, default=10)            # Max users allowed in room

    # Relationships
    owner = relationship("User", back_populates="owned_rooms")
    members = relationship("UserRoom", back_populates="room")
    snapshots = relationship("CanvasSnapshot", back_populates="room")
    chat_messages = relationship("ChatMessage", back_populates="room")  # NEW: Chat relationship


# ---- MODEL FOR USER-ROOM MEMBERSHIP ----
class UserRoom(Base):
    __tablename__ = "user_rooms"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(String, ForeignKey("rooms.id"), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.MEMBER)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)  # Can temporarily remove users

    # Relationships
    user = relationship("User", back_populates="room_memberships")
    room = relationship("Room", back_populates="members")

    # Ensure unique user-room pairs
    __table_args__ = (
        {'extend_existing': True}
    )


# ------------------------------------------------------
# Example usage in migration/init_db:
# from models.db import engine, Base
# Base.metadata.create_all(bind=engine)
