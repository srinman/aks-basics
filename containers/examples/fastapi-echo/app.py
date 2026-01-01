"""
FastAPI Echo Application
A modern async REST API that echoes back messages with metadata.
Demonstrates containerizing a FastAPI application with different dependencies.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import socket
import datetime
import uvicorn

# Configuration from environment variables
PORT = int(os.getenv('PORT', 8080))
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')

# Create FastAPI app
app = FastAPI(
    title="FastAPI Echo API",
    description="A simple echo API demonstrating FastAPI containerization",
    version=APP_VERSION
)


# Request/Response models
class EchoRequest(BaseModel):
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello from FastAPI!"
            }
        }


class EchoResponse(BaseModel):
    echo: str
    timestamp: str
    hostname: str
    client_ip: str
    metadata: dict


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    hostname: str


class InfoResponse(BaseModel):
    container: dict
    application: dict
    environment: dict


@app.get("/")
async def home():
    """Home endpoint with API information."""
    return {
        "service": "FastAPI Echo API",
        "version": APP_VERSION,
        "framework": "FastAPI",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "/": "API information",
            "/echo": "POST - Echo message with metadata",
            "/health": "Health check endpoint",
            "/info": "Container information",
            "/docs": "Interactive API documentation (Swagger UI)",
            "/redoc": "Alternative API documentation (ReDoc)"
        }
    }


@app.post("/echo", response_model=EchoResponse)
async def echo(request: EchoRequest):
    """
    Echo endpoint that returns the message with metadata.
    
    This endpoint demonstrates:
    - Pydantic model validation
    - Async request handling
    - Structured responses
    """
    response = {
        "echo": request.message,
        "timestamp": datetime.datetime.now().isoformat(),
        "hostname": socket.gethostname(),
        "client_ip": "container",  # Would need Request object for real IP
        "metadata": {
            "framework": "FastAPI",
            "version": APP_VERSION,
            "python_version": os.sys.version.split()[0],
            "async": True
        }
    }
    
    return response


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "hostname": socket.gethostname()
    }


@app.get("/info", response_model=InfoResponse)
async def info():
    """Container and environment information."""
    return {
        "container": {
            "hostname": socket.gethostname(),
            "python_version": os.sys.version.split()[0]
        },
        "application": {
            "framework": "FastAPI",
            "version": APP_VERSION,
            "port": PORT,
            "async": True
        },
        "environment": {
            key: value for key, value in os.environ.items()
            if key.startswith('APP_') or key in ['PORT', 'HOSTNAME']
        }
    }


if __name__ == '__main__':
    print(f"Starting FastAPI Echo API v{APP_VERSION} on port {PORT}")
    print(f"Hostname: {socket.gethostname()}")
    print(f"Python version: {os.sys.version.split()[0]}")
    print(f"Documentation available at: http://0.0.0.0:{PORT}/docs")
    
    # Run the application with Uvicorn
    # Uvicorn is an ASGI server for async Python web frameworks
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
