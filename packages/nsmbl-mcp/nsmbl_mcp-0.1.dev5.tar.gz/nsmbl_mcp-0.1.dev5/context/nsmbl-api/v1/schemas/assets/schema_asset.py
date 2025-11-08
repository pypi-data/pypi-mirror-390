"""
Asset schemas for tradeable assets with deterministic UUID generation.

Supports stocks, ETFs, crypto, futures with asset_type discrimination.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class AssetType(str, Enum):
    """Asset type enumeration for classification"""
    STOCK = "stock"
    ETF = "etf"


class AssetResponse(BaseModel):
    """Asset response model with deterministic UUID and classification"""
    
    asset_id: str = Field(
        ...,
        description="Deterministic UUID with 'as-' prefix for asset identification",
        example="as-12345678-1234-5678-9abc-123456789012"
    )
    
    asset_symbol: str = Field(
        ...,
        description="Trading symbol for the asset",
        example="VTI"
    )
    
    asset_name: str = Field(
        ...,
        description="Human-readable name of the asset",
        example="Vanguard Total Stock Market ETF"
    )
    
    asset_type: AssetType = Field(
        ...,
        description="Asset classification type",
        example="stock"
    )


class AssetListResponse(BaseModel):
    """Response model for asset list endpoint"""
    
    assets: List[AssetResponse] = Field(
        default_factory=list,
        description="List of available assets"
    )


class PaginatedAssetResponse(BaseModel):
    """Paginated response for asset list endpoint"""
    
    assets: List[AssetResponse] = Field(
        ...,
        description="Array of assets for current page"
    )
    
    total: int = Field(
        ...,
        description="Total number of assets matching filters"
    )
    
    limit: int = Field(
        ...,
        description="Maximum items per page"
    )
    
    offset: int = Field(
        ...,
        description="Starting position in result set"
    )
    
    returned: int = Field(
        ...,
        description="Number of items in current response"
    )


class AssetConfig(BaseModel):
    """Asset configuration for additional metadata (future use)"""
    
    exchange: Optional[str] = Field(None, description="Exchange where asset is traded")
    sector: Optional[str] = Field(None, description="Sector classification")
    currency: Optional[str] = Field("USD", description="Base currency")
    
    class Config:
        extra = "allow"  # Allow additional fields for future expansion
