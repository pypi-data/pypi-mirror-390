"""
Unified strategy schemas with inline model configuration and type discrimination.

Supports all strategy types (basket, tactical, ensemble, portfolio) with 
modern allocation_model, rebalancing_model, and tactical_model terminology.
"""

from typing import Optional, List, Dict, Any, Union, Literal, Annotated
from pydantic import BaseModel, Field, model_validator, ConfigDict
from enum import Enum
from datetime import datetime


class StrategyType(str, Enum):
    """Strategy type enumeration"""
    BASKET = "basket"
    TACTICAL = "tactical"
    ENSEMBLE = "ensemble"
    PORTFOLIO = "portfolio"


class UniverseReference(BaseModel):
    """
    Reference to an asset or strategy in a universe.
    
    Provide exactly ONE of the following identifiers:
    - asset_symbol: Use for stocks/ETFs (e.g., 'AAPL', 'VTI') - most common
    - asset_id: Use for assets by UUID (e.g., 'as-12345678-...')
    - strategy_symbol: Use for existing strategies by symbol (e.g., 'my-basket')
    - strategy_id: Use for existing strategies by UUID (e.g., 'sb-12345678-...')
    
    Examples:
    - {"asset_symbol": "VTI"} - Reference Vanguard Total Stock Market ETF
    - {"strategy_symbol": "tech-basket"} - Reference an existing strategy
    - {"strategy_id": "sb-12345678-1234-5678-9abc-123456789012"} - Reference by UUID
    """
    
    asset_symbol: Optional[str] = Field(
        None,
        description="Asset ticker symbol (stocks, ETFs, etc.)",
        example="VTI"
    )
    
    asset_id: Optional[str] = Field(
        None,
        description="Asset UUID with 'as-' prefix",
        example="as-12345678-1234-5678-9abc-123456789012"
    )
    
    strategy_symbol: Optional[str] = Field(
        None,
        description="Strategy identifier (user-defined or auto-generated)",
        example="my-risk-parity-basket"
    )
    
    strategy_id: Optional[str] = Field(
        None,
        description="Strategy UUID with proper prefix (sb-/st-/se-/sp-)",
        example="sb-12345678-1234-5678-9abc-123456789012"
    )
    
    model_config = ConfigDict(
        exclude_none=True,
        json_schema_extra={
            "examples": [
                {"asset_symbol": "VTI"},
                {"asset_symbol": "AAPL"},
                {"strategy_symbol": "tech-risk-parity"},
                {"strategy_id": "sb-12345678-1234-5678-9abc-123456789012"}
            ]
        }
    )
    
    @model_validator(mode='after')
    def validate_at_least_one_identifier(self):
        """Ensure at least one identifier is provided"""
        identifiers = [
            self.asset_symbol,
            self.asset_id, 
            self.strategy_symbol,
            self.strategy_id
        ]
        if not any(identifiers):
            raise ValueError("At least one identifier (asset_symbol, asset_id, strategy_symbol, or strategy_id) must be provided")
        return self


# Allocation Model Parameter Schemas
class RiskParityParams(BaseModel):
    """Parameters for risk parity allocation model"""
    lookback_days: int = Field(
        252,
        ge=5,
        le=1000,
        description="Number of days for risk calculation (5-1000 days, default 252 = 1 year)"
    )


class EqualWeightParams(BaseModel):
    """Parameters for equal weight allocation (no parameters required)"""
    pass


class FixedWeightParams(BaseModel):
    """Parameters for fixed weight allocation"""
    weights: List[float] = Field(
        ...,
        description="Array of weights for each universe component (must sum to 1.0)",
        min_items=1
    )


class InverseVolatilityParams(BaseModel):
    """Parameters for inverse volatility allocation"""
    lookback_days: int = Field(
        252,
        ge=5,
        le=1000,
        description="Number of days for volatility calculation (5-1000 days, default 252 = 1 year)"
    )


# Allocation Model with Discriminated Union
class RiskParityModel(BaseModel):
    """Risk parity allocation configuration"""
    model_name: Literal["risk_parity"] = Field("risk_parity", description="Risk parity allocation")
    model_params: RiskParityParams = Field(default_factory=lambda: RiskParityParams())


class EqualWeightModel(BaseModel):
    """Equal weight allocation configuration"""
    model_name: Literal["equal_weight"] = Field("equal_weight", description="Equal weight allocation")
    model_params: EqualWeightParams = Field(default_factory=lambda: EqualWeightParams())


class FixedWeightModel(BaseModel):
    """Fixed weight allocation configuration"""
    model_name: Literal["fixed_weight"] = Field("fixed_weight", description="User-specified weights")
    model_params: FixedWeightParams


class InverseVolatilityModel(BaseModel):
    """Inverse volatility allocation configuration"""
    model_name: Literal["inverse_volatility"] = Field("inverse_volatility", description="Inverse volatility weights")
    model_params: InverseVolatilityParams = Field(default_factory=lambda: InverseVolatilityParams())


AllocationModel = Annotated[
    Union[RiskParityModel, EqualWeightModel, FixedWeightModel, InverseVolatilityModel],
    Field(discriminator="model_name", description="Portfolio allocation model configuration")
]


# Rebalancing Model Parameter Schemas
class RebalancingFrequency(str, Enum):
    """Rebalancing frequency options"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class CalendarBasedParams(BaseModel):
    """Parameters for calendar-based rebalancing"""
    frequency: RebalancingFrequency = Field(
        RebalancingFrequency.MONTHLY,
        description="Rebalancing schedule (daily, weekly, monthly, or quarterly)"
    )


class DriftBasedParams(BaseModel):
    """Parameters for drift-based rebalancing"""
    threshold: float = Field(
        0.05,
        ge=0.01,
        le=0.5,
        description="Drift threshold percentage (0.01-0.5, default 0.05 = 5% drift)"
    )


# Rebalancing Model with Discriminated Union
class CalendarBasedModel(BaseModel):
    """Calendar-based rebalancing configuration"""
    model_name: Literal["calendar_based"] = Field("calendar_based", description="Fixed schedule rebalancing")
    model_params: CalendarBasedParams = Field(default_factory=lambda: CalendarBasedParams())


class DriftBasedModel(BaseModel):
    """Drift-based rebalancing configuration"""
    model_name: Literal["drift_based"] = Field("drift_based", description="Threshold-based rebalancing")
    model_params: DriftBasedParams = Field(default_factory=lambda: DriftBasedParams())


RebalancingModel = Annotated[
    Union[CalendarBasedModel, DriftBasedModel],
    Field(discriminator="model_name", description="Portfolio rebalancing configuration")
]


# Tactical Model Parameter Schemas
class TacticalParams(BaseModel):
    """Common parameters for tactical models (momentum and contrarian)"""
    lookback_days: int = Field(
        21,
        ge=5,
        le=1000,
        description="Lookback period for signal calculation (5-1000 days, default 21)"
    )
    n_positions: int = Field(
        3,
        ge=1,
        le=100,
        description="Number of positions to select from universe (1-100, default 3)"
    )


# Tactical Model with Discriminated Union
class MomentumModel(BaseModel):
    """Momentum tactical model configuration"""
    model_name: Literal["momentum"] = Field("momentum", description="Momentum signal generation")
    model_params: TacticalParams = Field(default_factory=lambda: TacticalParams())


class ContrarianModel(BaseModel):
    """Contrarian tactical model configuration"""
    model_name: Literal["contrarian"] = Field("contrarian", description="Contrarian (mean reversion) signal generation")
    model_params: TacticalParams = Field(default_factory=lambda: TacticalParams())


TacticalModel = Annotated[
    Union[MomentumModel, ContrarianModel],
    Field(discriminator="model_name", description="Tactical signal generation model (tactical strategies only)")
]


# Strategy-Type-Specific Configurations
class BasketConfig(BaseModel):
    """Configuration for basket strategies (allocation-based, no signals)"""
    universe: List[UniverseReference] = Field(
        ...,
        description="List of assets to include in basket",
        min_items=1
    )
    allocation_model: AllocationModel = Field(
        ...,
        description="Portfolio allocation method"
    )
    rebalancing_model: RebalancingModel = Field(
        ...,
        description="Rebalancing frequency and triggers"
    )


class TacticalConfig(BaseModel):
    """Configuration for tactical strategies (signal-driven asset selection)"""
    universe: List[UniverseReference] = Field(
        ...,
        description="List of assets available for tactical selection",
        min_items=1
    )
    tactical_model: TacticalModel = Field(
        ...,
        description="Signal generation model for asset selection"
    )
    allocation_model: AllocationModel = Field(
        ...,
        description="Portfolio allocation method for selected assets"
    )
    rebalancing_model: RebalancingModel = Field(
        ...,
        description="Rebalancing frequency and triggers"
    )


class EnsembleConfig(BaseModel):
    """Configuration for ensemble strategies (multi-strategy combinations)"""
    universe: List[UniverseReference] = Field(
        ...,
        description="List of strategies and/or assets to combine",
        min_items=2
    )
    allocation_model: AllocationModel = Field(
        ...,
        description="Portfolio allocation method"
    )
    rebalancing_model: RebalancingModel = Field(
        ...,
        description="Rebalancing frequency and triggers"
    )
    

class PortfolioConfig(BaseModel):
    """Configuration for portfolio strategies (top-level investment portfolios)"""
    universe: List[UniverseReference] = Field(
        ...,
        description="List of strategies and/or assets in portfolio",
        min_items=1
    )
    allocation_model: AllocationModel = Field(
        ...,
        description="Portfolio allocation method"
    )
    rebalancing_model: RebalancingModel = Field(
        ...,
        description="Rebalancing frequency and triggers"
    )
    

# Strategy Request Models (Discriminated by Type)
class BasketRequest(BaseModel):
    """Request to create a basket strategy"""
    strategy_type: Literal["basket"] = Field("basket", description="Basket strategy type")
    strategy_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable strategy name",
        example="Tech Risk Parity Basket"
    )
    strategy_symbol: Optional[str] = Field(
        None,
        max_length=50,
        pattern="^[a-z0-9-]+$",
        description="URL-friendly identifier (auto-generated from name if not provided)",
        example="tech-risk-parity"
    )
    strategy_config: BasketConfig = Field(
        ...,
        description="Basket configuration (allocation-based, no signals)"
    )


class TacticalRequest(BaseModel):
    """Request to create a tactical strategy"""
    strategy_type: Literal["tactical"] = Field("tactical", description="Tactical strategy type")
    strategy_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable strategy name",
        example="ETF Momentum Rotation"
    )
    strategy_symbol: Optional[str] = Field(
        None,
        max_length=50,
        pattern="^[a-z0-9-]+$",
        description="URL-friendly identifier (auto-generated from name if not provided)",
        example="etf-momentum"
    )
    strategy_config: TacticalConfig = Field(
        ...,
        description="Tactical configuration (requires tactical_model)"
    )


class EnsembleRequest(BaseModel):
    """Request to create an ensemble strategy"""
    strategy_type: Literal["ensemble"] = Field("ensemble", description="Ensemble strategy type")
    strategy_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable strategy name",
        example="Multi-Strategy Ensemble"
    )
    strategy_symbol: Optional[str] = Field(
        None,
        max_length=50,
        pattern="^[a-z0-9-]+$",
        description="URL-friendly identifier (auto-generated from name if not provided)",
        example="multi-strategy"
    )
    strategy_config: EnsembleConfig = Field(
        ...,
        description="Ensemble configuration (combines multiple strategies/assets)"
    )


class PortfolioRequest(BaseModel):
    """Request to create a portfolio strategy"""
    strategy_type: Literal["portfolio"] = Field("portfolio", description="Portfolio strategy type")
    strategy_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable strategy name",
        example="Complete Investment Portfolio"
    )
    strategy_symbol: Optional[str] = Field(
        None,
        max_length=50,
        pattern="^[a-z0-9-]+$",
        description="URL-friendly identifier (auto-generated from name if not provided)",
        example="complete-portfolio"
    )
    strategy_config: PortfolioConfig = Field(
        ...,
        description="Portfolio configuration (top-level investment mix)"
    )


# Union for Strategy Requests (error filtering handled by custom handler)
StrategyRequest = Union[BasketRequest, TacticalRequest, EnsembleRequest, PortfolioRequest]


# Union of all config types for responses (no discrimination needed)
StrategyConfig = Union[BasketConfig, TacticalConfig, EnsembleConfig, PortfolioConfig]


class StrategyResponse(BaseModel):
    """Response model for strategy operations"""
    
    strategy_id: str = Field(
        ...,
        description="Strategy UUID with proper prefix (sb-, st-, se-, sp-)",
        example="sb-12345678-1234-5678-9abc-123456789012"
    )
    
    strategy_name: str = Field(
        ...,
        description="Human-readable strategy name"
    )
    
    strategy_symbol: str = Field(
        ...,
        description="URL-friendly strategy symbol"
    )
    
    strategy_type: StrategyType = Field(
        ...,
        description="Strategy type classification"
    )
    
    strategy_config: StrategyConfig = Field(
        ...,
        description="Complete strategy configuration"
    )
    
    created_at: datetime = Field(
        ...,
        description="Strategy creation timestamp"
    )
    
    updated_at: datetime = Field(
        ...,
        description="Strategy last update timestamp"
    )


class StrategyUpdateRequest(BaseModel):
    """Request model for updating strategies"""
    
    strategy_name: Optional[str] = Field(
        None,
        description="Updated strategy name",
        min_length=1,
        max_length=100
    )
    
    strategy_config: Optional[StrategyConfig] = Field(
        None,
        description="Updated strategy configuration"
    )
