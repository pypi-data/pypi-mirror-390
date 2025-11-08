from fastapi import APIRouter
from app.api.v1.endpoints import endpoint_assets as assets, endpoint_strategies as strategies, endpoint_backtests as backtests

api_router = APIRouter()

# Include the assets router under /assets prefix
api_router.include_router(
    assets.router, 
    prefix="/assets", 
    tags=["assets"]
)

# Include the strategies router under /strategies prefix
api_router.include_router(
    strategies.router,
    prefix="/strategies",
    tags=["strategies"]
)

# Include the modernized backtests endpoint
api_router.include_router(
    backtests.router, 
    prefix="/backtests", 
    tags=["backtests"]
)
