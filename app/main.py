from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import engine, Base
from app.core.config import get_settings
from app.api.v1.endpoints import characters, campaigns
# Import all models to ensure they are registered with SQLAlchemy
from app.models import Character, Campaign, Item, CharacterItem

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Sigil RPG API...")

    # Create database tables
    Base.metadata.create_all(bind=engine)

    yield

    # Shutdown
    print("🛑 Shutting down Sigil RPG API...")


app = FastAPI(
    title="Sigil RPG API",
    description="API para gerenciamento de personagens do sistema Sigil RPG",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(characters.router, prefix="/api/v1/characters", tags=["Characters"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["Campaigns"])


@app.get("/")
async def root():
    return {
        "message": "Sigil RPG API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Sigil RPG API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)