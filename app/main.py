from fastapi import FastAPI

app = FastAPI(
    title="TEST BACKEND",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=True
)

@app.get("/")
def root():
    return {"message": "ok"}