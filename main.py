import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Import your existing playground app
from app.playground_app import app as playground_app

# Wrap with a new FastAPI app that adds root route + frontend
from fastapi import FastAPI
from fastapi.routing import Mount

# Add CORS middleware to playground app
playground_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend at root "/"
@playground_app.get("/")
async def serve_frontend():
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path, media_type="text/html")
    return JSONResponse({"status": "running", "message": "Major Project AI Agents API", "docs": "/docs"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7777))
    uvicorn.run(
        "main:playground_app",
        host="0.0.0.0",
        port=port,
        reload=False
    )