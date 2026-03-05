"""
AWS Lambda Handler for Content DNA OS.
Uses Mangum to wrap the FastAPI app for Lambda + API Gateway.
All routes defined in FastAPI are automatically supported.
"""

from mangum import Mangum
from app.main import app

handler = Mangum(app, lifespan="off")
