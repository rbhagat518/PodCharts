"""Minimal test handler to verify Vercel Python runtime works."""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok", "message": "Test handler works"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# Vercel expects this
handler = app

