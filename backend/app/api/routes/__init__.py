from app.api.routes.auth import router as auth_router
from app.api.routes.footprints import router as footprints_router
from app.api.routes.trips import router as trips_router
from app.api.routes.uploads import router as uploads_router

__all__ = ["auth_router", "trips_router", "footprints_router", "uploads_router"]
