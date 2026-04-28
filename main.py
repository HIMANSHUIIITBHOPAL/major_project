import os
import uvicorn
import traceback
import groq as groq_lib

from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from phi.playground import Playground

# Import your agents
from agents.stock_agent import stock_agent
from agents.web_agent import web_agent


# ✅ Create Playground (THIS HANDLES ALL /v1/playground ROUTES)
playground = Playground(
    agents=[stock_agent, web_agent]
)

# ✅ Get FastAPI app
app = playground.get_app()


# ✅ Enable CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ Global exception handler — converts unhandled 500s to readable JSON
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Groq API key host restriction (403 PermissionDenied)
    if isinstance(exc, groq_lib.PermissionDeniedError):
        return JSONResponse(
            status_code=403,
            content={
                "error": "groq_permission_denied",
                "detail": (
                    "Your Groq API key has host restrictions. "
                    "Go to console.groq.com → API Keys → remove host allowlist, "
                    "or add your Render deployment URL to the allowlist."
                ),
            },
        )

    # Groq auth error
    if isinstance(exc, groq_lib.AuthenticationError):
        return JSONResponse(
            status_code=401,
            content={
                "error": "groq_auth_error",
                "detail": "Invalid GROQ_API_KEY. Check your environment variable on Render.",
            },
        )

    # Groq rate limit
    if isinstance(exc, groq_lib.RateLimitError):
        return JSONResponse(
            status_code=429,
            content={
                "error": "groq_rate_limit",
                "detail": "Groq API rate limit reached. Please wait a moment and try again.",
            },
        )

    # Pydantic validation errors (e.g. bad tool call response shape)
    try:
        from pydantic import ValidationError
        if isinstance(exc, ValidationError):
            return JSONResponse(
                status_code=422,
                content={
                    "error": "pydantic_validation_error",
                    "detail": str(exc),
                },
            )
    except ImportError:
        pass

    # Generic fallback
    tb = traceback.format_exc()
    print(f"[ERROR] Unhandled exception on {request.url}:\n{tb}")
    return JSONResponse(
        status_code=500,
        content={
            "error": type(exc).__name__,
            "detail": str(exc),
        },
    )


# ✅ Root route (serves your frontend)
@app.get("/")
async def serve_frontend():
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"status": "running", "message": "Frontend not found"}


# ✅ Health check
@app.get("/health")
async def health():
    groq_key_set = bool(os.getenv("GROQ_API_KEY"))
    return {
        "status": "healthy",
        "groq_api_key_set": groq_key_set,
        "agents": ["stock_agent", "web_agent"],
    }


# ✅ Run server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Render uses 10000
    uvicorn.run("main:app", host="0.0.0.0", port=port)