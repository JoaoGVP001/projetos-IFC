from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Support running from project root (absolute imports) or from app/ folder (relative)
try:
    from app.routes.root import router as root_router  # type: ignore
    from app.routes.characters import router as characters_router  # type: ignore
    from app.routes.campaigns import router as campaigns_router  # type: ignore
except ModuleNotFoundError:
    from .routes.root import router as root_router  # type: ignore
    from .routes.characters import router as characters_router  # type: ignore
    from .routes.campaigns import router as campaigns_router  # type: ignore

app = FastAPI(title="RPG Helper API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root_router, prefix="/api/v1")
app.include_router(characters_router, prefix="/api/v1/characters", tags=["characters"])
app.include_router(campaigns_router, prefix="/api/v1/campaigns", tags=["campaigns"])

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis

from app.config.database import engine, Base
from app.config.redis_client import get_redis_client
from app.routes import auth, characters, campaigns, items, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting RPG Helper API...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize Redis connection
    app.state.redis = await redis.from_url("redis://localhost:6379", decode_responses=True)
    
    yield
    
    # Shutdown
    print("🛑 Shutting down RPG Helper API...")
    await app.state.redis.close()


app = FastAPI(
    title="RPG Helper API",
    description="API para gerenciamento de campanhas de RPG",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(characters.router, prefix="/api/v1/characters", tags=["Characters"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["Campaigns"])
app.include_router(items.router, prefix="/api/v1/items", tags=["Items"])


@app.get("/")
async def root():
    return {
        "message": "RPG Helper API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "RPG Helper API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
