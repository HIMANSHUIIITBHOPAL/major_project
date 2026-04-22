import os
import uvicorn
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from phi.playground import Playground

# Import agents
from agents.stock_agent import stock_agent
from agents.web_agent import web_agent

# ✅ Create Playground app (THIS IS THE KEY FIX)
playground = Playground(
    agents=[stock_agent, web_agent]
)

app = playground.get_app()

# ✅ Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}

# ✅ Serve frontend
@app.get("/")
async def serve_frontend():
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "Frontend not found", "docs": "/docs"}


# ✅ Run (Render uses this automatically)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 7777))
    uvicorn.run("main:app", host="0.0.0.0", port=port)