from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import auth_router, snippets_router, snippets_public_router, stars_router, users_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.logging import LoggingMiddleware
from app.services.cache_service import close_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis()

app = FastAPI(
    title="SnippetVault API",
    description="Backend API for SnippetVault SaaS",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(snippets_router)
app.include_router(snippets_public_router)
app.include_router(stars_router)
app.include_router(users_router)

@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "healthy"}
