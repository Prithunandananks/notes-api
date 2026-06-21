from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.notes import router as notes_router

__all__ = ["auth_router", "users_router", "notes_router"]
