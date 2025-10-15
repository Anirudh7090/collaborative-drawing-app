from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

from app.routers.home import router as home_router
from app.routers.auth import router as auth_router
from app.routers.websockets import router as websocket_router
from app.routers.drawings import router as drawings_router
from app.routers.rooms import router as rooms_router

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow ALL for now to test
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Manual CORS for OPTIONS requests (preflight)
@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true"
        }
    )

app.include_router(home_router)
app.include_router(auth_router)
app.include_router(websocket_router)
app.include_router(drawings_router)
app.include_router(rooms_router)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}
