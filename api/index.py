from flask import Flask, Response
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app from app.py
from app import app as flask_app

# Define a handler function for Vercel
def handler(request):
    """Handle a request to the Flask app."""
    return Response(
        flask_app(request.environ, lambda s, h, e: [s, h, []]),
        status=200
    )
