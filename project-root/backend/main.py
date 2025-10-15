from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routers.home import router as home_router
from app.routers.auth import router as auth_router
from app.routers.websockets import router as websocket_router
from app.routers.drawings import router as drawings_router
from app.routers.rooms import router as rooms_router

app = FastAPI()

# Get frontend URL from environment
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Configure CORS - allow both local and production
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    FRONTEND_URL,
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(home_router)
app.include_router(auth_router)
app.include_router(websocket_router)
app.include_router(drawings_router)
app.include_router(rooms_router)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}
