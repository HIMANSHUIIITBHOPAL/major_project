import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "running", "message": "Major Project API is live!"}
if __name__ == "__main__":
    uvicorn.run(
        "app.playground_app:app",
        host="0.0.0.0",   # required for cloud deployment
        port=7777,
        reload= False     # False in production
    )