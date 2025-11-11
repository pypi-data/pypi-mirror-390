"""
LLM Models CRUD API with database persistence

This router provides full CRUD operations for managing LLM models
that can be used by agents and teams.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime
import structlog

from control_plane_api.app.middleware.auth import get_current_organization
from control_plane_api.app.database import get_db
from control_plane_api.app.models.llm_model import LLMModel as LLMModelDB

logger = structlog.get_logger()

router = APIRouter()


# ==================== Pydantic Schemas ====================

class LLMModelCreate(BaseModel):
    """Schema for creating a new LLM model"""
    value: str = Field(..., description="Model identifier (e.g., 'kubiya/claude-sonnet-4')")
    label: str = Field(..., description="Display name (e.g., 'Claude Sonnet 4')")
    provider: str = Field(..., description="Provider name (e.g., 'Anthropic', 'OpenAI')")
    logo: Optional[str] = Field(None, description="Logo path or URL")
    description: Optional[str] = Field(None, description="Model description")
    enabled: bool = Field(True, description="Whether model is enabled")
    recommended: bool = Field(False, description="Whether model is recommended by default")
    compatible_runtimes: List[str] = Field(
        default_factory=list,
        description="List of compatible runtime IDs (e.g., ['default', 'claude_code'])"
    )
    capabilities: dict = Field(
        default_factory=dict,
        description="Model capabilities (e.g., {'vision': true, 'max_tokens': 4096})"
    )
    pricing: Optional[dict] = Field(None, description="Pricing information")
    display_order: int = Field(1000, description="Display order (lower = shown first)")


class LLMModelUpdate(BaseModel):
    """Schema for updating an existing LLM model"""
    value: Optional[str] = None
    label: Optional[str] = None
    provider: Optional[str] = None
    logo: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    recommended: Optional[bool] = None
    compatible_runtimes: Optional[List[str]] = None
    capabilities: Optional[dict] = None
    pricing: Optional[dict] = None
    display_order: Optional[int] = None


class LLMModelResponse(BaseModel):
    """Schema for LLM model responses"""
    id: str
    value: str
    label: str
    provider: str
    logo: Optional[str]
    description: Optional[str]
    enabled: bool
    recommended: bool
    compatible_runtimes: List[str]
    capabilities: dict
    pricing: Optional[dict]
    display_order: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# ==================== Helper Functions ====================

def check_runtime_compatibility(model: LLMModelDB, runtime_id: Optional[str]) -> bool:
    """Check if a model is compatible with a specific runtime"""
    if not runtime_id:
        return True  # No filter specified
    if not model.compatible_runtimes:
        return True  # Model doesn't specify compatibility, allow all
    return runtime_id in model.compatible_runtimes


# ==================== CRUD Endpoints ====================

@router.post("", response_model=LLMModelResponse, status_code=status.HTTP_201_CREATED)
def create_model(
    model_data: LLMModelCreate,
    request: Request,
    db: Session = Depends(get_db),
    organization: dict = Depends(get_current_organization),
):
    """
    Create a new LLM model.

    Only accessible by authenticated users (org admins recommended).
    """
    # Check if model with this value already exists
    existing = db.query(LLMModelDB).filter(LLMModelDB.value == model_data.value).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Model with value '{model_data.value}' already exists"
        )

    # Create new model
    new_model = LLMModelDB(
        value=model_data.value,
        label=model_data.label,
        provider=model_data.provider,
        logo=model_data.logo,
        description=model_data.description,
        enabled=model_data.enabled,
        recommended=model_data.recommended,
        compatible_runtimes=model_data.compatible_runtimes,
        capabilities=model_data.capabilities,
        pricing=model_data.pricing,
        display_order=model_data.display_order,
        created_by=organization.get("user_id"),
    )

    db.add(new_model)
    db.commit()
    db.refresh(new_model)

    logger.info(
        "llm_model_created",
        model_id=new_model.id,
        model_value=new_model.value,
        provider=new_model.provider,
        org_id=organization["id"]
    )

    return model_to_response(new_model)


@router.get("", response_model=List[LLMModelResponse])
def list_models(
    db: Session = Depends(get_db),
    enabled_only: bool = Query(True, description="Only return enabled models"),
    provider: Optional[str] = Query(None, description="Filter by provider (e.g., 'Anthropic', 'OpenAI')"),
    runtime: Optional[str] = Query(None, description="Filter by compatible runtime (e.g., 'claude_code')"),
    recommended: Optional[bool] = Query(None, description="Filter by recommended status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    List all LLM models with optional filtering.

    Query Parameters:
    - enabled_only: Only return enabled models (default: true)
    - provider: Filter by provider name
    - runtime: Filter by compatible runtime
    - recommended: Filter by recommended status
    - skip/limit: Pagination
    """
    query = db.query(LLMModelDB)

    # Apply filters
    if enabled_only:
        query = query.filter(LLMModelDB.enabled == True)

    if provider:
        query = query.filter(LLMModelDB.provider == provider)

    if recommended is not None:
        query = query.filter(LLMModelDB.recommended == recommended)

    # Order by display_order, then by created_at
    query = query.order_by(LLMModelDB.display_order, LLMModelDB.created_at)

    # Apply pagination
    models = query.offset(skip).limit(limit).all()

    # Filter by runtime compatibility (done in Python due to JSON array filtering complexity)
    if runtime:
        models = [m for m in models if check_runtime_compatibility(m, runtime)]

    return [model_to_response(m) for m in models]


@router.get("/default", response_model=LLMModelResponse)
def get_default_model(db: Session = Depends(get_db)):
    """
    Get the default recommended LLM model.

    Returns the first model marked as recommended and enabled.
    If none found, returns the first enabled model.
    """
    # Try to get recommended model first
    model = (
        db.query(LLMModelDB)
        .filter(LLMModelDB.enabled == True, LLMModelDB.recommended == True)
        .order_by(LLMModelDB.display_order)
        .first()
    )

    # Fallback to first enabled model
    if not model:
        model = (
            db.query(LLMModelDB)
            .filter(LLMModelDB.enabled == True)
            .order_by(LLMModelDB.display_order)
            .first()
        )

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No enabled models found"
        )

    return model_to_response(model)


@router.get("/providers", response_model=List[str])
def list_providers(db: Session = Depends(get_db)):
    """
    Get list of unique model providers.

    Returns a list of all unique provider names.
    """
    providers = db.query(LLMModelDB.provider).distinct().all()
    return [p[0] for p in providers]


@router.get("/{model_id}", response_model=LLMModelResponse)
def get_model(model_id: str, db: Session = Depends(get_db)):
    """
    Get a specific LLM model by ID or value.

    Accepts either the UUID or the model value (e.g., 'kubiya/claude-sonnet-4').
    """
    # Try by ID first
    model = db.query(LLMModelDB).filter(LLMModelDB.id == model_id).first()

    # If not found, try by value
    if not model:
        model = db.query(LLMModelDB).filter(LLMModelDB.value == model_id).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_id}' not found"
        )

    return model_to_response(model)


@router.patch("/{model_id}", response_model=LLMModelResponse)
def update_model(
    model_id: str,
    model_data: LLMModelUpdate,
    request: Request,
    db: Session = Depends(get_db),
    organization: dict = Depends(get_current_organization),
):
    """
    Update an existing LLM model.

    Only accessible by authenticated users (org admins recommended).
    """
    # Find model
    model = db.query(LLMModelDB).filter(LLMModelDB.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_id}' not found"
        )

    # Check if value is being updated and conflicts with existing
    if model_data.value and model_data.value != model.value:
        existing = db.query(LLMModelDB).filter(LLMModelDB.value == model_data.value).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Model with value '{model_data.value}' already exists"
            )

    # Update fields
    update_dict = model_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(model, field, value)

    model.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(model)

    logger.info(
        "llm_model_updated",
        model_id=model.id,
        model_value=model.value,
        updated_fields=list(update_dict.keys()),
        org_id=organization["id"]
    )

    return model_to_response(model)


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(
    model_id: str,
    request: Request,
    db: Session = Depends(get_db),
    organization: dict = Depends(get_current_organization),
):
    """
    Delete an LLM model.

    Only accessible by authenticated users (org admins recommended).
    """
    model = db.query(LLMModelDB).filter(LLMModelDB.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_id}' not found"
        )

    db.delete(model)
    db.commit()

    logger.info(
        "llm_model_deleted",
        model_id=model.id,
        model_value=model.value,
        org_id=organization["id"]
    )

    return None


# ==================== Helper Functions ====================

def model_to_response(model: LLMModelDB) -> LLMModelResponse:
    """Convert database model to response schema"""
    return LLMModelResponse(
        id=model.id,
        value=model.value,
        label=model.label,
        provider=model.provider,
        logo=model.logo,
        description=model.description,
        enabled=model.enabled,
        recommended=model.recommended,
        compatible_runtimes=model.compatible_runtimes or [],
        capabilities=model.capabilities or {},
        pricing=model.pricing,
        display_order=model.display_order,
        created_at=model.created_at.isoformat() if model.created_at else "",
        updated_at=model.updated_at.isoformat() if model.updated_at else "",
    )
