"""Vercel serverless function entry point."""
import sys
import traceback
import os

# Print to stderr so it appears in Vercel logs
print("Starting handler import...", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Current directory: {os.getcwd()}", file=sys.stderr)
print(f"Python path: {sys.path}", file=sys.stderr)

# Log any import errors to stderr so they appear in Vercel logs
try:
    print("Importing app.main...", file=sys.stderr)
    from app.main import app
    print("Successfully imported app.main", file=sys.stderr)
except ImportError as e:
    # Print detailed import error
    print(f"IMPORT ERROR: {type(e).__name__}: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise
except Exception as e:
    # Print other errors
    print(f"ERROR: Failed to import app: {type(e).__name__}: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise

# This is the handler for Vercel serverless functions
# Vercel's Python runtime expects the FastAPI app directly
print("Setting handler = app", file=sys.stderr)
handler = app
print("Handler ready!", file=sys.stderr)

