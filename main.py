import os
import uvicorn
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from phi.playground import Playground

# Import your agents
from agents.stock_agent import stock_agent
from agents.web_agent import web_agent


# ✅ Create Playground (THIS HANDLES ALL /v1/playground ROUTES)
playground = Playground(
    agents=[stock_agent, web_agent]
)

# ✅ Get FastAPI app (DO NOT WRAP AGAIN)
app = playground.get_app()


# ✅ Enable CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ Root route (serves your frontend)
@app.get("/")
async def serve_frontend():
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"status": "running", "message": "Frontend not found"}


# ✅ Health check (optional but useful)
@app.get("/health")
async def health():
    return {"status": "healthy"}


# ✅ Run server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Render uses 10000
    uvicorn.run("main:app", host="0.0.0.0", port=port)