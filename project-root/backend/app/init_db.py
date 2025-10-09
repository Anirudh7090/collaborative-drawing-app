from models.db import engine, Base, CanvasSnapshot, Room, UserRoom  # Import all new models
from models.users import User

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created!")

if __name__ == "__main__":
    init_db()
