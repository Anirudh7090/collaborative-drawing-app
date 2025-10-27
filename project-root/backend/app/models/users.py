from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    owned_rooms = relationship("Room", back_populates="owner")              # Rooms this user owns
    room_memberships = relationship("UserRoom", back_populates="user")      # Every room/user membership
    snapshots = relationship("CanvasSnapshot", back_populates="creator")    # List of snapshots created by this user
    chat_messages = relationship("ChatMessage", back_populates="user")      # NEW: Chat messages sent by this user
