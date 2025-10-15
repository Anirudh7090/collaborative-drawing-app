from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routers.home import router as home_router
from app.routers.auth import router as auth_router
from app.routers.websockets import router as websocket_router
from app.routers.drawings import router as drawings_router
from app.routers.rooms import router as rooms_router

app = FastAPI()

# CORS - MUST BE FIRST MIDDLEWARE!
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://collaborative-drawing-app-1.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # <-- ADD THIS!
)

app.include_router(home_router)
app.include_router(auth_router)
app.include_router(websocket_router)
app.include_router(drawings_router)
app.include_router(rooms_router)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}
