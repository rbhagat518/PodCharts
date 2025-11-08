"""Minimal test handler to verify Vercel Python runtime works."""
import sys
import traceback

print("Loading test.py...", file=sys.stderr)

try:
    print("Importing FastAPI...", file=sys.stderr)
    from fastapi import FastAPI
    print("FastAPI imported successfully", file=sys.stderr)
    
    print("Creating FastAPI app...", file=sys.stderr)
    app = FastAPI()
    print("FastAPI app created", file=sys.stderr)
    
    @app.get("/")
    async def root():
        return {"status": "ok", "message": "Test handler works"}
    
    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    print("Routes defined", file=sys.stderr)
    
    # Vercel expects this
    print("Setting handler = app", file=sys.stderr)
    handler = app
    print("Handler set successfully!", file=sys.stderr)
    
except Exception as e:
    print(f"ERROR in test.py: {type(e).__name__}: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise

