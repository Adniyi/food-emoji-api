from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.routers import emoji, batch, search, category, random

app = FastAPI(
    title="Food Emoji API",
    description="Comprehensive food emoji lookup with fuzzy matching and regional variants",
    version="1.0.0",
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_timing(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start)
    return response

app.include_router(emoji.router)
app.include_router(batch.router)
app.include_router(search.router)
app.include_router(category.router)
app.include_router(random.router)

@app.get("/")
async def root():
    return {
        "message": "🍜 Food Emoji API",
        "endpoints": ["/emoji/{food}", "/batch", "/search", "/category/{type}", "/random"]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}