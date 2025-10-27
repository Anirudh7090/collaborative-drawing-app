from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.home import router as home_router
from app.routers.auth import router as auth_router
from app.routers.websockets import router as websocket_router
from app.routers.drawings import router as drawings_router
from app.routers.rooms import router as rooms_router
from app.routers.webrtc import router as webrtc_router  # NEW: Import WebRTC router

app = FastAPI()

# CORS - Allow all origins temporarily for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow ALL origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(home_router)
app.include_router(auth_router)
app.include_router(websocket_router)
app.include_router(drawings_router)
app.include_router(rooms_router)
app.include_router(webrtc_router)  # NEW: Register WebRTC router

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}
