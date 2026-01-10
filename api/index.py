"""
Vercel Serverless Function Entry Point
"""
from app import app

# This is required for Vercel
def handler(request, context):
    return app(request, context)