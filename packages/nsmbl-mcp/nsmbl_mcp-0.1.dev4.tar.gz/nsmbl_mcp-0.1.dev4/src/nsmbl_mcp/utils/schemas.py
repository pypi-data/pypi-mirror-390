"""
JSON Schema definitions for NSMBL API models.

This module provides complete, validated JSON schemas that match the exact
Pydantic models from the backend API. These schemas are used in MCP tool
definitions to help LLMs understand the precise structure required for API calls.

All schemas follow JSON Schema Draft 7 specification.
"""

from typing import Any, Dict


# ============================================================================
# Universe Reference Schema
# ============================================================================

UNIVERSE_REFERENCE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": (
        "Reference to an asset or strategy in a universe. "
        "Provide exactly ONE of: asset_symbol (most common), asset_id, strategy_symbol, or strategy_id."
    ),
    "properties": {
        "asset_symbol": {
            "type": "string",
            "description": "Asset ticker symbol (e.g., 'AAPL', 'VTI', 'GOOGL')",
            "examples": ["VTI", "AAPL", "MSFT", "GOOGL", "NVDA", "META", "TSLA", "SPXU"]
        },
        "asset_id": {
            "type": "string",
            "description": "Asset UUID with 'as-' prefix",
            "pattern": "^as-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            "examples": ["as-12345678-1234-5678-9abc-123456789012"]
        },
        "strategy_symbol": {
            "type": "string",
            "description": "Strategy identifier (user-defined or auto-generated, lowercase with hyphens)",
            "pattern": "^[a-z0-9-]+$",
            "examples": ["my-risk-parity-basket", "tech-momentum"]
        },
        "strategy_id": {
            "type": "string",
            "description": "Strategy UUID with proper prefix (sb-/st-/se-/sp- for basket/tactical/ensemble/portfolio)",
            "pattern": "^s[btep]-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            "examples": ["sb-12345678-1234-5678-9abc-123456789012"]
        }
    },
    "oneOf": [
        {"required": ["asset_symbol"]},
        {"required": ["asset_id"]},
        {"required": ["strategy_symbol"]},
        {"required": ["strategy_id"]}
    ],
    "additionalProperties": False
}


# ============================================================================
# Allocation Model Schemas
# ============================================================================

RISK_PARITY_MODEL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Risk parity allocation - weights assets by inverse volatility for equal risk contribution",
    "properties": {
        "model_name": {
            "type": "string",
            "const": "risk_parity",
            "description": "Must be 'risk_parity' (not 'type'!)"
        },
        "model_params": {
            "type": "object",
            "description": "Parameters for risk parity calculation",
            "properties": {
                "lookback_days": {
                    "type": "integer",
                    "description": "Number of days for risk calculation (5-1000 days)",
                    "default": 252,
                    "minimum": 5,
                    "maximum": 1000,
                    "examples": [21, 63, 126, 252, 504]
                }
            },
            "additionalProperties": False
        }
    },
    "required": ["model_name"],
    "additionalProperties": False
}

EQUAL_WEIGHT_MODEL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Equal weight allocation - distributes capital equally across all assets",
    "properties": {
        "model_name": {
            "type": "string",
            "const": "equal_weight",
            "description": "Must be 'equal_weight' (not 'type'!)"
        },
        "model_params": {
            "type": "object",
            "description": "No parameters required for equal weight",
            "properties": {},
            "additionalProperties": False
        }
    },
    "required": ["model_name"],
    "additionalProperties": False
}

FIXED_WEIGHT_MODEL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Fixed weight allocation - uses custom specified weights",
    "properties": {
        "model_name": {
            "type": "string",
            "const": "fixed_weight",
            "description": "Must be 'fixed_weight' (not 'type'!)"
        },
        "model_params": {
            "type": "object",
            "description": "Custom weight parameters",
            "properties": {
                "weights": {
                    "type": "array",
                    "description": "Array of weights for each universe component (must sum to 1.0)",
                    "items": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1
                    },
                    "minItems": 1,
                    "examples": [[0.5, 0.3, 0.2], [0.25, 0.25, 0.25, 0.25]]
                }
            },
            "required": ["weights"],
            "additionalProperties": False
        }
    },
    "required": ["model_name", "model_params"],
    "additionalProperties": False
}

INVERSE_VOLATILITY_MODEL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Inverse volatility allocation - weights inversely to volatility (lower vol = higher weight)",
    "properties": {
        "model_name": {
            "type": "string",
            "const": "inverse_volatility",
            "description": "Must be 'inverse_volatility' (not 'type'!)"
        },
        "model_params": {
            "type": "object",
            "description": "Parameters for volatility calculation",
            "properties": {
                "lookback_days": {
                    "type": "integer",
                    "description": "Number of days for volatility calculation (5-1000 days)",
                    "default": 252,
                    "minimum": 5,
                    "maximum": 1000,
                    "examples": [21, 63, 126, 252, 504]
                }
            },
            "additionalProperties": False
        }
    },
    "required": ["model_name"],
    "additionalProperties": False
}

ALLOCATION_MODEL_SCHEMA: Dict[str, Any] = {
    "oneOf": [
        RISK_PARITY_MODEL_SCHEMA,
        EQUAL_WEIGHT_MODEL_SCHEMA,
        FIXED_WEIGHT_MODEL_SCHEMA,
        INVERSE_VOLATILITY_MODEL_SCHEMA
    ],
    "description": (
        "Portfolio allocation model (discriminated union). "
        "IMPORTANT: Use 'model_name' (not 'type') and 'model_params' fields. "
        "Valid model_name values: 'risk_parity', 'equal_weight', 'fixed_weight', 'inverse_volatility'"
    )
}


# ============================================================================
# Rebalancing Model Schemas
# ============================================================================

CALENDAR_BASED_MODEL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Calendar-based rebalancing - rebalances on a fixed schedule",
    "properties": {
        "model_name": {
            "type": "string",
            "const": "calendar_based",
            "description": "Must be 'calendar_based' (not 'periodic' or 'type'!)"
        },
        "model_params": {
            "type": "object",
            "description": "Calendar schedule parameters",
            "properties": {
                "frequency": {
                    "type": "string",
                    "enum": ["daily", "weekly", "monthly", "quarterly"],
                    "description": "Rebalancing frequency (daily, weekly, monthly, or quarterly)",
                    "default": "monthly",
                    "examples": ["daily", "weekly", "monthly", "quarterly"]
                }
            },
            "additionalProperties": False
        }
    },
    "required": ["model_name"],
    "additionalProperties": False
}

DRIFT_BASED_MODEL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Drift-based rebalancing - rebalances when allocation drifts beyond threshold",
    "properties": {
        "model_name": {
            "type": "string",
            "const": "drift_based",
            "description": "Must be 'drift_based' (not 'type'!)"
        },
        "model_params": {
            "type": "object",
            "description": "Drift threshold parameters",
            "properties": {
                "threshold": {
                    "type": "number",
                    "description": "Drift threshold as decimal (0.01-0.5, e.g., 0.05 = 5% drift)",
                    "default": 0.05,
                    "minimum": 0.01,
                    "maximum": 0.5,
                    "examples": [0.05, 0.10, 0.15]
                }
            },
            "additionalProperties": False
        }
    },
    "required": ["model_name"],
    "additionalProperties": False
}

REBALANCING_MODEL_SCHEMA: Dict[str, Any] = {
    "oneOf": [
        CALENDAR_BASED_MODEL_SCHEMA,
        DRIFT_BASED_MODEL_SCHEMA
    ],
    "description": (
        "Portfolio rebalancing configuration (discriminated union). "
        "IMPORTANT: Use 'model_name' (not 'type') and 'model_params' fields. "
        "Valid model_name values: 'calendar_based', 'drift_based'"
    )
}


# ============================================================================
# Tactical Model Schemas (for tactical strategies only)
# ============================================================================

MOMENTUM_MODEL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Momentum tactical model - selects top-performing assets",
    "properties": {
        "model_name": {
            "type": "string",
            "const": "momentum",
            "description": "Must be 'momentum' (not 'type'!)"
        },
        "model_params": {
            "type": "object",
            "description": "Momentum signal parameters",
            "properties": {
                "lookback_days": {
                    "type": "integer",
                    "description": "Lookback period for performance calculation (5-1000 days)",
                    "default": 21,
                    "minimum": 5,
                    "maximum": 1000,
                    "examples": [21, 63, 126, 252]
                },
                "n_positions": {
                    "type": "integer",
                    "description": "Number of top-performing assets to select (1-100)",
                    "default": 3,
                    "minimum": 1,
                    "maximum": 100,
                    "examples": [3, 5, 10]
                }
            },
            "additionalProperties": False
        }
    },
    "required": ["model_name"],
    "additionalProperties": False
}

CONTRARIAN_MODEL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Contrarian tactical model - selects worst-performing assets (mean reversion)",
    "properties": {
        "model_name": {
            "type": "string",
            "const": "contrarian",
            "description": "Must be 'contrarian' (not 'mean_reversion' or 'type'!)"
        },
        "model_params": {
            "type": "object",
            "description": "Contrarian signal parameters",
            "properties": {
                "lookback_days": {
                    "type": "integer",
                    "description": "Lookback period for performance calculation (5-1000 days)",
                    "default": 21,
                    "minimum": 5,
                    "maximum": 1000,
                    "examples": [21, 63, 126, 252]
                },
                "n_positions": {
                    "type": "integer",
                    "description": "Number of worst-performing assets to select (1-100)",
                    "default": 3,
                    "minimum": 1,
                    "maximum": 100,
                    "examples": [3, 5, 10]
                }
            },
            "additionalProperties": False
        }
    },
    "required": ["model_name"],
    "additionalProperties": False
}

TACTICAL_MODEL_SCHEMA: Dict[str, Any] = {
    "oneOf": [
        MOMENTUM_MODEL_SCHEMA,
        CONTRARIAN_MODEL_SCHEMA
    ],
    "description": (
        "Tactical signal generation model (discriminated union). "
        "IMPORTANT: Use 'model_name' (not 'type') and 'model_params' fields. "
        "Valid model_name values: 'momentum', 'contrarian'. "
        "Only required for tactical strategy types!"
    )
}


# ============================================================================
# Strategy Configuration Schemas
# ============================================================================

BASKET_CONFIG_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Configuration for basket strategies (allocation-based, no tactical signals)",
    "properties": {
        "universe": {
            "type": "array",
            "description": (
                "List of assets to include in basket. "
                "Each item must be an object with ONE of: asset_symbol, asset_id, strategy_symbol, or strategy_id"
            ),
            "items": UNIVERSE_REFERENCE_SCHEMA,
            "minItems": 1,
            "examples": [
                [{"asset_symbol": "VTI"}, {"asset_symbol": "VEA"}, {"asset_symbol": "AGG"}],
                [{"asset_symbol": "AAPL"}, {"asset_symbol": "MSFT"}, {"asset_symbol": "GOOGL"}]
            ]
        },
        "allocation_model": ALLOCATION_MODEL_SCHEMA,
        "rebalancing_model": REBALANCING_MODEL_SCHEMA
    },
    "required": ["universe", "allocation_model", "rebalancing_model"],
    "additionalProperties": False
}

TACTICAL_CONFIG_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Configuration for tactical strategies (signal-driven asset selection)",
    "properties": {
        "universe": {
            "type": "array",
            "description": (
                "List of assets available for tactical selection. "
                "Each item must be an object with ONE of: asset_symbol, asset_id, strategy_symbol, or strategy_id"
            ),
            "items": UNIVERSE_REFERENCE_SCHEMA,
            "minItems": 1,
            "examples": [
                [{"asset_symbol": "SPY"}, {"asset_symbol": "QQQ"}, {"asset_symbol": "IWM"}]
            ]
        },
        "tactical_model": TACTICAL_MODEL_SCHEMA,
        "allocation_model": ALLOCATION_MODEL_SCHEMA,
        "rebalancing_model": REBALANCING_MODEL_SCHEMA
    },
    "required": ["universe", "tactical_model", "allocation_model", "rebalancing_model"],
    "additionalProperties": False
}

ENSEMBLE_CONFIG_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Configuration for ensemble strategies (combines multiple strategies)",
    "properties": {
        "universe": {
            "type": "array",
            "description": (
                "List of strategies and/or assets to combine (minimum 2 items). "
                "Each item must be an object with ONE of: asset_symbol, asset_id, strategy_symbol, or strategy_id"
            ),
            "items": UNIVERSE_REFERENCE_SCHEMA,
            "minItems": 2,
            "examples": [
                [{"strategy_symbol": "tech-basket"}, {"strategy_symbol": "defensive-basket"}]
            ]
        },
        "allocation_model": ALLOCATION_MODEL_SCHEMA,
        "rebalancing_model": REBALANCING_MODEL_SCHEMA
    },
    "required": ["universe", "allocation_model", "rebalancing_model"],
    "additionalProperties": False
}

PORTFOLIO_CONFIG_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Configuration for portfolio strategies (top-level container for assets and all strategy types)",
    "properties": {
        "universe": {
            "type": "array",
            "description": (
                "List of strategies and/or assets in portfolio. "
                "Each item must be an object with ONE of: asset_symbol, asset_id, strategy_symbol, or strategy_id"
            ),
            "items": UNIVERSE_REFERENCE_SCHEMA,
            "minItems": 1,
            "examples": [
                [{"asset_symbol": "VTI"}, {"strategy_symbol": "my-tactical"}]
            ]
        },
        "allocation_model": ALLOCATION_MODEL_SCHEMA,
        "rebalancing_model": REBALANCING_MODEL_SCHEMA
    },
    "required": ["universe", "allocation_model", "rebalancing_model"],
    "additionalProperties": False
}


# ============================================================================
# Complete Strategy Data Schema (for create_strategy tool)
# ============================================================================

def get_strategy_data_schema() -> Dict[str, Any]:
    """
    Get the complete strategy_data schema for create_strategy tool.
    
    Returns a JSON schema with discriminated union based on strategy_type.
    """
    return {
        "type": "object",
        "description": "Complete strategy configuration object",
        "properties": {
            "strategy_type": {
                "type": "string",
                "enum": ["basket", "tactical", "ensemble", "portfolio"],
                "description": (
                    "Strategy type determines which configuration fields are required:\n"
                    "• basket: Static allocation across assets (requires allocation_model, rebalancing_model)\n"
                    "• tactical: Dynamic signal-driven selection (requires tactical_model, allocation_model, rebalancing_model)\n"
                    "• ensemble: Combines multiple strategies (requires allocation_model, rebalancing_model, min 2 items)\n"
                    "• portfolio: Top-level container for everything (requires allocation_model, rebalancing_model)"
                )
            },
            "strategy_name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 100,
                "description": "Human-readable name for the strategy",
                "examples": ["Tech Risk Parity Basket", "MAG7 + SPXU Risk Parity (Daily)"]
            },
            "strategy_symbol": {
                "type": "string",
                "maxLength": 50,
                "pattern": "^[a-z0-9-]+$",
                "description": "Optional URL-friendly identifier (lowercase, hyphens only). Auto-generated from name if not provided.",
                "examples": ["tech-risk-parity", "mag7-rp-daily"]
            },
            "strategy_config": {
                "description": (
                    "Strategy configuration object. Structure depends on strategy_type. "
                    "IMPORTANT: Use 'model_name' (not 'type') for all model configurations!"
                ),
                "oneOf": [
                    {
                        "description": "Basket strategy configuration",
                        "allOf": [
                            {"properties": {"strategy_type": {"const": "basket"}}},
                            {"properties": {"strategy_config": BASKET_CONFIG_SCHEMA}}
                        ]
                    },
                    {
                        "description": "Tactical strategy configuration",
                        "allOf": [
                            {"properties": {"strategy_type": {"const": "tactical"}}},
                            {"properties": {"strategy_config": TACTICAL_CONFIG_SCHEMA}}
                        ]
                    },
                    {
                        "description": "Ensemble strategy configuration",
                        "allOf": [
                            {"properties": {"strategy_type": {"const": "ensemble"}}},
                            {"properties": {"strategy_config": ENSEMBLE_CONFIG_SCHEMA}}
                        ]
                    },
                    {
                        "description": "Portfolio strategy configuration",
                        "allOf": [
                            {"properties": {"strategy_type": {"const": "portfolio"}}},
                            {"properties": {"strategy_config": PORTFOLIO_CONFIG_SCHEMA}}
                        ]
                    }
                ]
            }
        },
        "required": ["strategy_type", "strategy_name", "strategy_config"],
        "additionalProperties": False
    }


# ============================================================================
# Helper function to get strategy config schema by type
# ============================================================================

def get_strategy_config_schema_by_type(strategy_type: str) -> Dict[str, Any]:
    """
    Get the strategy_config schema for a specific strategy type.
    
    Args:
        strategy_type: One of 'basket', 'tactical', 'ensemble', 'portfolio'
        
    Returns:
        JSON schema for that strategy type's configuration
    """
    schemas = {
        "basket": BASKET_CONFIG_SCHEMA,
        "tactical": TACTICAL_CONFIG_SCHEMA,
        "ensemble": ENSEMBLE_CONFIG_SCHEMA,
        "portfolio": PORTFOLIO_CONFIG_SCHEMA
    }
    return schemas.get(strategy_type, {})
