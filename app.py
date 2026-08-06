from fastapi import FastAPI

app = FastAPI(
    title="DocChat API",
    version="1.0.0",
    description="REST API for Multi-Agent RAG Document Intelligence"
)


@app.get("/")
async def root():
    return {
        "message": "DocChat API is running!"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }