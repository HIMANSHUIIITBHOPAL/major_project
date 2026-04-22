import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from phi.playground import Playground

# Import agents
from agents.stock_agent import stock_agent
from agents.web_agent import web_agent

# -------------------------------
# Create Playground App
# -------------------------------
playground = Playground(
    agents=[stock_agent, web_agent]
)

playground_app = playground.get_app()

# -------------------------------
# Main App (IMPORTANT for /v1)
# -------------------------------
app = FastAPI()

# Mount Playground at /v1
app.mount("/v1", playground_app)

# -------------------------------
# CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Health Check
# -------------------------------
@app.get("/health")
async def health():
    return {"status": "healthy"}

# -------------------------------
# Serve Frontend
# -------------------------------
@app.get("/")
async def serve_frontend():
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "Frontend not found", "docs": "/docs"}

# -------------------------------
# Run Server
# -------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 7777))
    uvicorn.run("main:app", host="0.0.0.0", port=port)