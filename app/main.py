from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="MCP Backend",
    description="税理士事務所向け業務効率化システムのバックエンド",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

@app.get("/", response_model=dict)
async def root():
    return {
        "message": "Welcome to MCP Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=dict)
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "mcp-backend"
    } 