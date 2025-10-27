# app/init_db.py
from app.models.db import engine, Base, CanvasSnapshot, Room, UserRoom, ChatMessage  # Added ChatMessage
from app.models.users import User

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    init_db()
