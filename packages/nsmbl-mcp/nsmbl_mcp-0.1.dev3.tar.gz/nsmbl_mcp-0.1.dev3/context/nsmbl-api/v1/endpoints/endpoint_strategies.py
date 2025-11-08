"""
Strategies endpoint for unified strategy management with type discrimination.

Supports all strategy types (basket, tactical, ensemble, portfolio) with 
inline model configuration and hierarchical target structure.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.core.middleware import get_current_user
from app.db.strategies.crud_strategies import (
    get_strategies, 
    get_strategy_by_id_or_symbol,
    create_strategy_record,
    update_strategy as update_strategy_record,
    delete_strategy as delete_strategy_record,
    strategy_symbol_exists,
    strategy_name_exists
)
from app.api.v1.schemas.strategies.schema_strategy import StrategyRequest, StrategyResponse
from app.errors import (
    handle_validation_error,
    handle_not_found_error,
    handle_database_error,
    validate_strategy_universe_or_raise
)
from app.core.logging import get_domain_logger
from app.services.internal.auth.user_service import charge_strategies_endpoint_call

logger = get_domain_logger('api', __name__)

router = APIRouter()


@router.post(
    "",
    operation_id="createStrategy",
    summary="Create Strategy",
    status_code=201,
    responses={
        201: {
            "description": "Strategy created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "strategy_id": "sb-12345678-1234-5678-9abc-123456789012",
                        "strategy_name": "Tech Risk Parity Basket",
                        "strategy_symbol": "tech-risk-parity",
                        "strategy_type": "basket",
                        "strategy_config": {
                            "universe": [
                                {"asset_symbol": "VTI"},
                                {"asset_symbol": "VEA"}
                            ],
                            "allocation_model": {
                                "model_name": "risk_parity",
                                "model_params": {"lookback_days": 252}
                            },
                            "rebalancing_model": {
                                "model_name": "calendar_based",
                                "model_params": {"frequency": "monthly"}
                            }
                        },
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "duplicate_symbol",
                            "message": "Strategy symbol 'tech-risk-parity' already exists"
                        }
                    }
                }
            }
        }
    }
)
async def create_strategy(
    strategy_data: StrategyRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a systematic investment strategy with inline model configuration.
    
    Accepts basket, tactical, ensemble, or portfolio strategy types with complete universe and model specifications.
    """
    
    user_id, _ = current_user
    logger.info(f"Creating strategy for user {user_id}")
    
    try:
        # Extract fields from Pydantic model
        strategy_type = strategy_data.strategy_type
        strategy_name = strategy_data.strategy_name
        strategy_symbol = strategy_data.strategy_symbol
        strategy_config = strategy_data.strategy_config.model_dump(exclude_none=True)  # Convert to dict for database
        
        # Check for duplicate strategy_symbol if provided
        if strategy_symbol and strategy_symbol_exists(db, user_id, strategy_symbol):
            raise handle_validation_error(
                "duplicate_symbol",
                f"Strategy symbol '{strategy_symbol}' already exists"
            )
        
        # Check for duplicate strategy_name
        if strategy_name_exists(db, user_id, strategy_name):
            raise handle_validation_error(
                "duplicate_name",
                f"Strategy name '{strategy_name}' already exists"
            )
        
        # Validate universe
        await validate_strategy_universe_or_raise(
            strategy_config, strategy_type, strategy_name, db, user_id
        )
        
        # Create strategy
        db_strategy = create_strategy_record(
            db=db,
            user_id=user_id,
            strategy_name=strategy_name,
            strategy_type=strategy_type,
            strategy_config=strategy_config,
            strategy_symbol=strategy_symbol
        )
        
        # Format response
        response = {
            "strategy_id": db_strategy.id,
            "strategy_name": db_strategy.strategy_name,
            "strategy_symbol": db_strategy.strategy_symbol,
            "strategy_type": db_strategy.strategy_type,
            "strategy_config": db_strategy.strategy_config,
            "created_at": db_strategy.created_at.isoformat(),
            "updated_at": db_strategy.updated_at.isoformat()
        }
        
        # BILLING CHARGE: Strategy creation is charged (1¢ per call)
        # Creating a strategy represents the core value we provide.
        # Users can then retrieve this strategy for free via GET endpoints.
        await charge_strategies_endpoint_call(user_id)
        
        logger.info(f"Created strategy: {db_strategy.id} ({db_strategy.strategy_type})")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating strategy: {str(e)}")
        raise handle_database_error(e, "create", "strategy")


@router.get(
    "",
    operation_id="listStrategies",
    summary="List Strategies",
    response_model=List[dict],
    responses={
        200: {
            "description": "Strategies retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "strategy_id": "sb-12345678-1234-5678-9abc-123456789012",
                            "strategy_name": "Tech Risk Parity Basket",
                            "strategy_symbol": "tech-risk-parity",
                            "strategy_type": "basket",
                            "strategy_config": {
                                "universe": [{"asset_symbol": "VTI"}],
                                "allocation_model": {"model_name": "risk_parity"},
                                "rebalancing_model": {"model_name": "calendar_based"}
                            },
                            "created_at": "2024-01-15T10:30:00Z",
                            "updated_at": "2024-01-15T10:30:00Z"
                        }
                    ]
                }
            }
        },
        422: {
            "description": "Invalid query parameters",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "invalid_strategy_type",
                            "message": "Strategy type must be one of: basket, tactical, ensemble, portfolio"
                        }
                    }
                }
            }
        }
    }
)
async def list_strategies(
    strategy_type: str = Query(
        default=None,
        description="Filter by strategy type (returns all if not specified)",
        enum=["basket", "tactical", "ensemble", "portfolio"]
    ),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all strategies with optional type filtering.
    
    Returns array of user's strategies with IDs, names, symbols, types, and complete configurations.
    """
    
    user_id, _ = current_user
    logger.info(f"Fetching strategies for user {user_id}, strategy_type filter: {strategy_type}")
    
    # NO BILLING CHARGE: Listing strategies is free
    # Users pay to create/modify strategies, then retrieve them for free.
    # This encourages users to explore their strategies without cost concerns.
    
    try:
        # Validate strategy_type if provided
        valid_types = ["basket", "tactical", "ensemble", "portfolio"]
        if strategy_type and strategy_type not in valid_types:
            raise handle_validation_error(
                "invalid_strategy_type",
                f"Strategy type must be one of: {', '.join(valid_types)}"
            )
        
        # Get strategies from database
        strategies = get_strategies(db, user_id, strategy_type=strategy_type)
        
        # Format response
        formatted_strategies = []
        for strategy in strategies:
            formatted_strategy = {
                "strategy_id": strategy.id,
                "strategy_name": strategy.strategy_name,
                "strategy_symbol": strategy.strategy_symbol,
                "strategy_type": strategy.strategy_type,
                "strategy_config": strategy.strategy_config,
                "created_at": strategy.created_at.isoformat(),
                "updated_at": strategy.updated_at.isoformat()
            }
            formatted_strategies.append(formatted_strategy)
        
        logger.info(f"Returning {len(formatted_strategies)} strategies")
        return formatted_strategies
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching strategies: {str(e)}")
        raise handle_database_error(e, "fetch", "strategies")


@router.get(
    "/{strategy_identifier}",
    operation_id="getStrategy",
    summary="Get Strategy",
    responses={
        200: {
            "description": "Strategy retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "strategy_id": "sb-12345678-1234-5678-9abc-123456789012",
                        "strategy_name": "Tech Risk Parity Basket",
                        "strategy_symbol": "tech-risk-parity",
                        "strategy_type": "basket",
                        "strategy_config": {
                            "universe": [{"asset_symbol": "VTI"}],
                            "allocation_model": {"model_name": "risk_parity"},
                            "rebalancing_model": {"model_name": "calendar_based"}
                        },
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Strategy not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "not_found",
                            "message": "Strategy not found: sb-invalid-id"
                        }
                    }
                }
            }
        }
    }
)
async def get_strategy(
    strategy_identifier: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a strategy by UUID or symbol.
    
    Returns complete strategy configuration including all model specifications.
    """
    
    user_id, _ = current_user
    logger.info(f"Fetching strategy {strategy_identifier} for user {user_id}")
    
    # NO BILLING CHARGE: Getting strategy details is free
    # Users pay to create/modify strategies, then retrieve them for free.
    # This encourages users to explore their strategies without cost concerns.
    
    try:
        # Get strategy from database
        strategy = get_strategy_by_id_or_symbol(db, user_id, strategy_identifier)
        
        if not strategy:
            raise handle_not_found_error("Strategy", strategy_identifier)
        
        # Format response
        response = {
            "strategy_id": strategy.id,
            "strategy_name": strategy.strategy_name,
            "strategy_symbol": strategy.strategy_symbol,
            "strategy_type": strategy.strategy_type,
            "strategy_config": strategy.strategy_config,
            "created_at": strategy.created_at.isoformat(),
            "updated_at": strategy.updated_at.isoformat()
        }
        
        logger.info(f"Returning strategy: {strategy.strategy_symbol} ({strategy.strategy_type})")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching strategy {strategy_identifier}: {str(e)}")
        raise handle_database_error(e, "fetch", "strategy", strategy_identifier)


@router.put(
    "/{strategy_id}",
    operation_id="updateStrategy",
    summary="Update Strategy",
    responses={
        200: {
            "description": "Strategy updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "strategy_id": "sb-12345678-1234-5678-9abc-123456789012",
                        "strategy_name": "Tech Risk Parity Basket - Updated",
                        "strategy_symbol": "tech-risk-parity",
                        "strategy_type": "basket",
                        "strategy_config": {
                            "universe": [{"asset_symbol": "VTI"}],
                            "allocation_model": {"model_name": "risk_parity"},
                            "rebalancing_model": {"model_name": "calendar_based"}
                        },
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T11:45:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Strategy not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "not_found",
                            "message": "Strategy not found: sb-invalid-id"
                        }
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "invalid_universe",
                            "message": "Invalid asset in universe: INVALID"
                        }
                    }
                }
            }
        }
    }
)
async def update_strategy(
    strategy_id: str,
    strategy_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing strategy's name or configuration.
    
    Validates universe references and model configurations before applying updates.
    """
    
    user_id, _ = current_user
    logger.info(f"Updating strategy {strategy_id} for user {user_id}")
    
    try:
        # Extract fields to update
        strategy_name = strategy_data.get("strategy_name")
        strategy_config = strategy_data.get("strategy_config")
        
        # Validate universe if being updated
        if strategy_config and strategy_config.get("universe"):
            await validate_strategy_universe_or_raise(
                strategy_config, "strategy", strategy_id, db, user_id
            )
        
        # Update strategy
        updated_strategy = update_strategy_record(
            db=db,
            strategy_id=strategy_id,
            user_id=user_id,
            strategy_name=strategy_name,
            strategy_config=strategy_config
        )
        
        if not updated_strategy:
            raise handle_not_found_error("Strategy", strategy_id)
        
        # Format response
        response = {
            "strategy_id": updated_strategy.id,
            "strategy_name": updated_strategy.strategy_name,
            "strategy_symbol": updated_strategy.strategy_symbol,
            "strategy_type": updated_strategy.strategy_type,
            "strategy_config": updated_strategy.strategy_config,
            "created_at": updated_strategy.created_at.isoformat(),
            "updated_at": updated_strategy.updated_at.isoformat()
        }
        
        # BILLING CHARGE: Strategy modification is charged (1¢ per call)
        # Modifying a strategy provides value similar to creation.
        # Users can then retrieve the updated strategy for free via GET endpoints.
        await charge_strategies_endpoint_call(user_id)
        
        logger.info(f"Updated strategy: {updated_strategy.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating strategy {strategy_id}: {str(e)}")
        raise handle_database_error(e, "update", "strategy", strategy_id)


@router.delete(
    "/{strategy_id}",
    operation_id="deleteStrategy",
    summary="Delete Strategy",
    responses={
        200: {
            "description": "Strategy deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Strategy deleted successfully"
                    }
                }
            }
        },
        404: {
            "description": "Strategy not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "not_found",
                            "message": "Strategy not found: sb-invalid-id"
                        }
                    }
                }
            }
        }
    }
)
async def delete_strategy(
    strategy_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a strategy permanently.
    
    Removes strategy and all associated configurations from the database.
    """
    
    user_id, _ = current_user
    logger.info(f"Deleting strategy {strategy_id} for user {user_id}")
    
    # NO BILLING CHARGE: Deleting strategies is free
    # We don't charge for resource cleanup - only for creation/modification.
    
    try:
        success = delete_strategy_record(db, user_id, strategy_id)
        
        if not success:
            raise handle_not_found_error("Strategy", strategy_id)
        
        logger.info(f"Deleted strategy: {strategy_id}")
        return {"message": "Strategy deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting strategy {strategy_id}: {str(e)}")
        raise handle_database_error(e, "delete", "strategy", strategy_id)
