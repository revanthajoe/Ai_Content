"""
Content DNA OS – FastAPI Application
Main entry point for the backend API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router

app = FastAPI(
    title="Content DNA OS",
    description="Evolutionary AI Operating System for Digital Content",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": "Content DNA OS",
        "version": "1.0.0",
        "status": "alive",
        "description": "Evolutionary AI Operating System for Digital Content",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
