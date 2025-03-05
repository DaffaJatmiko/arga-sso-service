from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.core.config import settings
from src.core.database import init_db
from src.middleware.cors import setup_cors
from src.core.redis import init_redis_pool, close_redis_connection
from src.api.auth import router as auth_router
from src.api.user import router as user_router
from src.api.unit import router as unit_router
from src.api.role import router as role_router
from src.middleware.token_blacklist import TokenBlacklistMiddleware



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events
    """
    # Initialize connections
    await init_db()
    await init_redis_pool()
    
    yield
    
    # Cleanup
    await close_redis_connection()

def setup_middleware(app: FastAPI):
    """
    Add all middleware to the app
    """
    # Security middleware
    app.middleware("http")(TokenBlacklistMiddleware())

    setup_cors(app)

    # Session middleware for OAuth
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.JWT_SECRET_KEY,
        session_cookie="sso_session"
    )

def setup_routers(app: FastAPI):
    """
    Configure all API routes
    """
    app.include_router(
        auth_router,
        prefix="/auth",
        tags=["Authentication"]
    )
    
    # User management routes
    app.include_router(
        user_router,
        prefix="/api/users",
        tags=["Users"]
    )
    
    # Unit management routes
    app.include_router(
        unit_router,
        prefix="/api/units",
        tags=["Units"]
    )
    
    # Role management routes
    app.include_router(
        role_router,
        prefix="/api/roles",
        tags=["Roles"]
    )

def create_app() -> FastAPI:
    """
    Create FastAPI application with all configurations
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="SSO Service API",
        debug=settings.DEBUG,
        lifespan=lifespan
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Setup routers
    setup_routers(app)
    
    return app

app = create_app()

