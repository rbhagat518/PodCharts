"""Vercel serverless function entry point."""
from app.main import app

# This is the handler for Vercel serverless functions
handler = app

