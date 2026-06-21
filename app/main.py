from contextlib import asynccontextmanager
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.limiter import limiter

from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.notes import router as notes_router

# 1. Setup structured logging configuration for stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app.main")

# 2. Modern Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup lifecycle events
    logger.info("Initializing system startup events...")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info(f"Target upload directory verified at: '{settings.UPLOAD_DIR}'")
    yield
    # Shutdown lifecycle events
    logger.info("Initializing system shutdown events...")
    logger.info("Cleanup completed successfully.")


# 4. Initialize FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A secure, async-first Notes API with JWT authentication, rate limiting, and protected file uploads.",
    version="1.0.0",
    lifespan=lifespan
)

# Bind rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 5. Configure CORS middleware (Cross-Origin Resource Sharing)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 6. Bind global domain exception handlers
setup_exception_handlers(app)

# 7. Register API Routers under standard prefix
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(notes_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["General"])
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "status": "healthy"
    }
