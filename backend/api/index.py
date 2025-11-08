"""Vercel serverless function entry point."""
import sys
import traceback

# Log any import errors to stderr so they appear in Vercel logs
try:
    from app.main import app
except Exception as e:
    # Print error to stderr (Vercel logs capture stderr)
    print(f"ERROR: Failed to import app: {type(e).__name__}: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    # Re-raise so Vercel shows the error
    raise

# This is the handler for Vercel serverless functions
# Vercel's Python runtime expects the FastAPI app directly
handler = app

