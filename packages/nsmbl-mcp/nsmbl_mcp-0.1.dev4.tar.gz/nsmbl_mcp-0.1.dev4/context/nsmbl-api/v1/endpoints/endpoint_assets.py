"""
Assets endpoint for asset metadata and backtesting.

Provides access to tradeable assets (stocks, ETFs, crypto, futures) with 
deterministic UUID generation and asset_type discrimination.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.core.middleware import get_current_user
from app.services.external.service_alpaca_markets import get_async_alpaca_markets_client
from app.core.utils import transform_alpaca_uuid
from app.api.v1.schemas.assets.schema_asset import AssetResponse, PaginatedAssetResponse
from app.errors import handle_external_service_error, handle_not_found_error
from app.core.logging import get_domain_logger
from app.services.internal.auth.user_service import charge_assets_endpoint_call

logger = get_domain_logger('api', __name__)

router = APIRouter()


@router.get(
    "",
    operation_id="listAssets",
    summary="List Assets",
    response_model=PaginatedAssetResponse,
    responses={
        200: {
            "description": "Assets retrieved successfully with pagination metadata",
            "content": {
                "application/json": {
                    "example": {
                        "assets": [
                            {
                                "asset_id": "as-12345678-1234-5678-9abc-123456789012",
                                "asset_symbol": "VTI",
                                "asset_name": "Vanguard Total Stock Market ETF",
                                "asset_type": "etf"
                            },
                            {
                                "asset_id": "as-87654321-4321-8765-cba9-210987654321",
                                "asset_symbol": "AAPL",
                                "asset_name": "Apple Inc",
                                "asset_type": "stock"
                            }
                        ],
                        "total": 12842,
                        "limit": 50,
                        "offset": 0,
                        "returned": 50
                    }
                }
            }
        },
        422: {
            "description": "Invalid query parameters",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "invalid_parameter",
                            "message": "Invalid asset_type value"
                        }
                    }
                }
            }
        }
    }
)
async def list_assets(
    asset_type: str = Query(
        default=None,
        description="Filter by asset type (returns all if not specified)",
        enum=["stock", "etf"]
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of assets to return per page"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Starting position in result set (for pagination)"
    ),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all tradeable assets with pagination and optional type filtering.
    
    Returns paginated, alphabetically sorted array of assets with metadata for use in 
    strategy construction and backtesting. Pagination helps manage large result sets 
    for LLM and API clients.
    """
    
    user_id, _ = current_user
    logger.info(f"Fetching assets for user {user_id}, asset_type filter: {asset_type}, limit: {limit}, offset: {offset}")
    
    # BILLING CHARGE: Assets endpoint is charged (1¢ per call)
    # We charge for asset lookups because they query external market data providers.
    # This is a "lookup/creation" operation, not reading user's own data.
    try:
        await charge_assets_endpoint_call(user_id)
        logger.info(f"Charged user {user_id} API call cost for GET assets")
    except Exception as e:
        logger.error(f"Failed to charge API call cost for user {user_id}: {str(e)}")
        # Continue with request - billing failure shouldn't block the operation
    
    try:
        # Get assets from market data service
        client = await get_async_alpaca_markets_client()
        async with client as alpaca_client:
            # Get assets directly (returns {"assets": [...]})
            result = await alpaca_client.get_assets()
            assets = result.get('assets', [])
        
        # Transform to our format with deterministic UUIDs
        formatted_assets = []
        for asset in assets:
            # Generate deterministic asset_id from Alpaca UUID
            asset_id = transform_alpaca_uuid(asset.get("id", ""))
            asset_symbol = asset.get("symbol", "")
            asset_name = asset.get("name", "")
            
            # Determine asset_type based on asset name
            # Check if "ETF" appears in the asset name
            if "ETF" in asset_name.upper():
                asset_type_value = "etf"
            else:
                asset_type_value = "stock"
            
            # Apply asset_type filter if specified
            if asset_type and asset_type_value != asset_type:
                continue
            
            formatted_asset = {
                "asset_id": asset_id,
                "asset_symbol": asset_symbol,
                "asset_name": asset_name,
                "asset_type": asset_type_value
            }
            formatted_assets.append(formatted_asset)
        
        # Sort alphabetically by asset_symbol
        formatted_assets.sort(key=lambda x: x.get("asset_symbol", ""))
        
        # Apply pagination
        total_count = len(formatted_assets)
        paginated_assets = formatted_assets[offset:offset + limit]
        
        logger.info(f"Returning {len(paginated_assets)} assets (page {offset // limit + 1}, total: {total_count})")
        
        return {
            "assets": paginated_assets,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "returned": len(paginated_assets)
        }
        
    except Exception as e:
        logger.error(f"Error fetching assets: {str(e)}")
        raise handle_external_service_error("market data service", "asset fetch", e)


@router.get(
    "/{asset_id_or_symbol}",
    operation_id="getAsset",
    summary="Get Asset",
    response_model=AssetResponse,
    responses={
        200: {
            "description": "Asset retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "asset_id": "as-12345678-1234-5678-9abc-123456789012",
                        "asset_symbol": "VTI",
                        "asset_name": "Vanguard Total Stock Market ETF",
                        "asset_type": "etf"
                    }
                }
            }
        },
        404: {
            "description": "Asset not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "not_found",
                            "message": "Asset not found: INVALID"
                        }
                    }
                }
            }
        }
    }
)
async def get_asset(
    asset_id_or_symbol: str = Path(
        ...,
        description="Asset symbol (e.g. 'VTI') or asset UUID (e.g. 'as-12345678-1234-5678-9abc-123456789012')",
        examples=["VTI", "AAPL", "as-12345678-1234-5678-9abc-123456789012"]
    ),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve asset metadata by symbol or UUID.
    
    Returns asset information for use in strategy universe configurations and backtesting.
    """
    
    user_id, _ = current_user
    logger.info(f"Fetching asset {asset_id_or_symbol} for user {user_id}")
    
    # BILLING CHARGE: Assets endpoint is charged (1¢ per call)
    # We charge for asset lookups because they query external market data providers.
    # This is a "lookup/creation" operation, not reading user's own data.
    try:
        await charge_assets_endpoint_call(user_id)
        logger.info(f"Charged user {user_id} API call cost for GET asset")
    except Exception as e:
        logger.error(f"Failed to charge API call cost for user {user_id}: {str(e)}")
        # Continue with request - billing failure shouldn't block the operation
    
    try:
        # Get asset from market data service by symbol or ID
        client = await get_async_alpaca_markets_client()
        async with client as alpaca_client:
            # Try by symbol first (most common case)
            if not asset_id_or_symbol.startswith("as-"):
                asset = await alpaca_client.get_asset_by_symbol(asset_id_or_symbol)
            else:
                # Handle asset_id lookup - search all assets for matching transformed ID
                result = await alpaca_client.get_assets()
                assets = result.get('assets', [])
                asset = None
                for a in assets:
                    if transform_alpaca_uuid(a.get("id", "")) == asset_id_or_symbol:
                        asset = a
                        break
                
                if not asset:
                    raise handle_not_found_error("Asset", asset_id_or_symbol)
        
        if not asset:
            raise handle_not_found_error("Asset", asset_id_or_symbol)
        
        # Transform raw data to our format
        asset_id = transform_alpaca_uuid(asset.get("id", ""))
        asset_symbol = asset.get("symbol", "")
        asset_name = asset.get("name", "")
        
        # Determine asset_type based on asset name
        # Check if "ETF" appears in the asset name
        if "ETF" in asset_name.upper():
            asset_type_value = "etf"
        else:
            asset_type_value = "stock"
        
        formatted_asset = {
            "asset_id": asset_id,
            "asset_symbol": asset_symbol,
            "asset_name": asset_name,
            "asset_type": asset_type_value
        }
        
        logger.info(f"Returning asset: {formatted_asset['asset_symbol']}")
        return formatted_asset
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching asset {asset_id_or_symbol}: {str(e)}")
        raise handle_external_service_error("market data service", "asset fetch", e)
