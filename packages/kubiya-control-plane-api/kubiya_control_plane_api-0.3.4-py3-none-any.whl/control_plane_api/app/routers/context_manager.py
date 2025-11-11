"""
Unified Context Management System for Agent Control Plane.

Manages contextual settings (knowledge, resources, policies) across all entity types:
- Environments
- Teams
- Projects
- Agents

Provides layered context resolution: Environment → Team → Project → Agent
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field
import structlog
import uuid

from control_plane_api.app.middleware.auth import get_current_organization
from control_plane_api.app.lib.supabase import get_supabase

logger = structlog.get_logger()

router = APIRouter()

# Entity types that support context
EntityType = Literal["environment", "team", "project", "agent"]

# Pydantic schemas
class ContextData(BaseModel):
    """Generic context data structure"""
    knowledge_uuids: List[str] = Field(default_factory=list, description="Knowledge base UUIDs")
    resource_ids: List[str] = Field(default_factory=list, description="Resource IDs from Meilisearch")
    policy_ids: List[str] = Field(default_factory=list, description="OPA policy IDs")


class UpdateContextRequest(BaseModel):
    """Request to update context for any entity"""
    knowledge_uuids: List[str] = Field(default_factory=list)
    resource_ids: List[str] = Field(default_factory=list)
    policy_ids: List[str] = Field(default_factory=list)


class ContextResponse(BaseModel):
    """Generic context response"""
    id: str
    entity_type: str
    entity_id: str
    organization_id: str
    knowledge_uuids: List[str]
    resource_ids: List[str]
    policy_ids: List[str]
    created_at: str
    updated_at: str


class ResolvedContextResponse(BaseModel):
    """Resolved context with inheritance from all layers"""
    entity_id: str
    entity_type: str
    environment_id: Optional[str] = None
    team_id: Optional[str] = None
    project_id: Optional[str] = None

    # Aggregated context from all layers
    knowledge_uuids: List[str] = Field(description="Merged knowledge from all layers")
    resource_ids: List[str] = Field(description="Merged resources from all layers")
    policy_ids: List[str] = Field(description="Merged policies from all layers")

    # Layer breakdown for debugging
    layers: Dict[str, ContextData] = Field(description="Context breakdown by layer")


# Table name mapping
CONTEXT_TABLE_MAP = {
    "environment": "environment_contexts",
    "team": "team_contexts",
    "project": "project_contexts",
    "agent": "agent_contexts",
}

# Entity table mapping (for validation)
ENTITY_TABLE_MAP = {
    "environment": "environments",
    "team": "teams",
    "project": "projects",
    "agent": "agents",
}


async def _verify_entity_exists(
    client, entity_type: EntityType, entity_id: str, org_id: str
) -> bool:
    """Verify that an entity exists for the organization"""
    table_name = ENTITY_TABLE_MAP.get(entity_type)
    if not table_name:
        return False

    result = (
        client.table(table_name)
        .select("id")
        .eq("id", entity_id)
        .eq("organization_id", org_id)
        .single()
        .execute()
    )

    return bool(result.data)


async def _get_or_create_context(
    client, entity_type: EntityType, entity_id: str, org_id: str
) -> Dict[str, Any]:
    """Get existing context or create a default one"""
    table_name = CONTEXT_TABLE_MAP.get(entity_type)
    if not table_name:
        raise ValueError(f"Invalid entity type: {entity_type}")

    # Try to get existing context
    result = (
        client.table(table_name)
        .select("*")
        .eq(f"{entity_type}_id", entity_id)
        .eq("organization_id", org_id)
        .single()
        .execute()
    )

    if result.data:
        return result.data

    # Create default context
    context_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    default_context = {
        "id": context_id,
        f"{entity_type}_id": entity_id,
        "entity_type": entity_type,
        "organization_id": org_id,
        "knowledge_uuids": [],
        "resource_ids": [],
        "policy_ids": [],
        "created_at": now,
        "updated_at": now,
    }

    insert_result = client.table(table_name).insert(default_context).execute()

    if not insert_result.data:
        raise Exception(f"Failed to create {entity_type} context")

    logger.info(
        "context_created",
        entity_type=entity_type,
        entity_id=entity_id,
        org_id=org_id,
    )

    return insert_result.data[0]


@router.get("/context/{entity_type}/{entity_id}", response_model=ContextResponse)
async def get_context(
    entity_type: EntityType,
    entity_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Get context configuration for any entity type"""
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Verify entity exists
        if not await _verify_entity_exists(client, entity_type, entity_id, org_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{entity_type.capitalize()} not found"
            )

        # Get or create context
        context_data = await _get_or_create_context(client, entity_type, entity_id, org_id)

        return ContextResponse(**context_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_context_failed", error=str(e), entity_type=entity_type, entity_id=entity_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get {entity_type} context: {str(e)}"
        )


@router.put("/context/{entity_type}/{entity_id}", response_model=ContextResponse)
async def update_context(
    entity_type: EntityType,
    entity_id: str,
    context_data: UpdateContextRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Update context configuration for any entity type"""
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Verify entity exists
        if not await _verify_entity_exists(client, entity_type, entity_id, org_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{entity_type.capitalize()} not found"
            )

        table_name = CONTEXT_TABLE_MAP[entity_type]
        now = datetime.utcnow().isoformat()

        # Check if context exists
        existing = (
            client.table(table_name)
            .select("id")
            .eq(f"{entity_type}_id", entity_id)
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        update_data = {
            "knowledge_uuids": context_data.knowledge_uuids,
            "resource_ids": context_data.resource_ids,
            "policy_ids": context_data.policy_ids,
            "updated_at": now,
        }

        if existing.data:
            # Update existing
            result = (
                client.table(table_name)
                .update(update_data)
                .eq("id", existing.data["id"])
                .execute()
            )
        else:
            # Create new
            context_id = str(uuid.uuid4())
            new_context = {
                "id": context_id,
                f"{entity_type}_id": entity_id,
                "entity_type": entity_type,
                "organization_id": org_id,
                **update_data,
                "created_at": now,
            }
            result = client.table(table_name).insert(new_context).execute()

        if not result.data:
            raise Exception(f"Failed to update {entity_type} context")

        logger.info(
            "context_updated",
            entity_type=entity_type,
            entity_id=entity_id,
            knowledge_count=len(context_data.knowledge_uuids),
            resource_count=len(context_data.resource_ids),
            policy_count=len(context_data.policy_ids),
            org_id=org_id,
        )

        return ContextResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_context_failed", error=str(e), entity_type=entity_type, entity_id=entity_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update {entity_type} context: {str(e)}"
        )


@router.delete("/context/{entity_type}/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_context(
    entity_type: EntityType,
    entity_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Clear all context for an entity"""
    try:
        client = get_supabase()
        org_id = organization["id"]

        table_name = CONTEXT_TABLE_MAP[entity_type]
        now = datetime.utcnow().isoformat()

        update_data = {
            "knowledge_uuids": [],
            "resource_ids": [],
            "policy_ids": [],
            "updated_at": now,
        }

        client.table(table_name).update(update_data).eq(f"{entity_type}_id", entity_id).eq("organization_id", org_id).execute()

        logger.info("context_cleared", entity_type=entity_type, entity_id=entity_id, org_id=org_id)
        return None

    except Exception as e:
        logger.error("clear_context_failed", error=str(e), entity_type=entity_type, entity_id=entity_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear {entity_type} context: {str(e)}"
        )


@router.get("/context/resolve/{entity_type}/{entity_id}", response_model=ResolvedContextResponse)
async def resolve_context(
    entity_type: EntityType,
    entity_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Resolve context with inheritance from all layers.

    Resolution order (each layer adds to the previous):
    1. ALL Environments (many-to-many for agents/teams)
    2. Team (if member of a team)
    3. ALL Team Environments (if agent is part of team)
    4. Project (if assigned to a project)
    5. Agent/Entity itself

    Returns merged context with full layer breakdown.
    """
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Verify entity exists
        if not await _verify_entity_exists(client, entity_type, entity_id, org_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{entity_type.capitalize()} not found"
            )

        layers: Dict[str, ContextData] = {}
        team_id: Optional[str] = None
        project_id: Optional[str] = None
        environment_ids: List[str] = []

        # Collect context from all layers
        all_knowledge: List[str] = []
        all_resources: List[str] = []
        all_policies: List[str] = []

        # 1. Get entity relationships (team, project)
        entity_table = ENTITY_TABLE_MAP[entity_type]
        entity_result = (
            client.table(entity_table)
            .select("team_id, project_id")
            .eq("id", entity_id)
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        entity_data = entity_result.data if entity_result.data else {}

        # Extract relationships
        team_id = entity_data.get("team_id")
        project_id = entity_data.get("project_id")

        # 2. Layer 1: Get ALL agent/team environments (many-to-many)
        if entity_type == "agent":
            # Get all agent environments
            agent_env_result = (
                client.table("agent_environments")
                .select("environment_id")
                .eq("agent_id", entity_id)
                .execute()
            )
            environment_ids = [env["environment_id"] for env in (agent_env_result.data or [])]

        elif entity_type == "team":
            # Get all team environments
            team_env_result = (
                client.table("team_environments")
                .select("environment_id")
                .eq("team_id", entity_id)
                .execute()
            )
            environment_ids = [env["environment_id"] for env in (team_env_result.data or [])]

        # Merge context from ALL environments
        for idx, env_id in enumerate(environment_ids):
            try:
                env_context = await _get_or_create_context(client, "environment", env_id, org_id)
                layer_key = f"environment_{idx+1}" if len(environment_ids) > 1 else "environment"
                layers[layer_key] = ContextData(
                    knowledge_uuids=env_context.get("knowledge_uuids", []),
                    resource_ids=env_context.get("resource_ids", []),
                    policy_ids=env_context.get("policy_ids", []),
                )
                all_knowledge.extend(layers[layer_key].knowledge_uuids)
                all_resources.extend(layers[layer_key].resource_ids)
                all_policies.extend(layers[layer_key].policy_ids)
            except Exception as e:
                logger.warning("failed_to_get_environment_context", error=str(e), environment_id=env_id)

        # 3. Layer 2: Team context
        if team_id:
            try:
                team_context = await _get_or_create_context(client, "team", team_id, org_id)
                layers["team"] = ContextData(
                    knowledge_uuids=team_context.get("knowledge_uuids", []),
                    resource_ids=team_context.get("resource_ids", []),
                    policy_ids=team_context.get("policy_ids", []),
                )
                all_knowledge.extend(layers["team"].knowledge_uuids)
                all_resources.extend(layers["team"].resource_ids)
                all_policies.extend(layers["team"].policy_ids)
            except Exception as e:
                logger.warning("failed_to_get_team_context", error=str(e), team_id=team_id)

            # 3b. Get ALL team environments (if agent has team)
            if entity_type == "agent":
                team_env_result = (
                    client.table("team_environments")
                    .select("environment_id")
                    .eq("team_id", team_id)
                    .execute()
                )
                team_environment_ids = [env["environment_id"] for env in (team_env_result.data or [])]

                for idx, env_id in enumerate(team_environment_ids):
                    # Skip if already processed in agent environments
                    if env_id in environment_ids:
                        continue
                    try:
                        env_context = await _get_or_create_context(client, "environment", env_id, org_id)
                        layer_key = f"team_environment_{idx+1}"
                        layers[layer_key] = ContextData(
                            knowledge_uuids=env_context.get("knowledge_uuids", []),
                            resource_ids=env_context.get("resource_ids", []),
                            policy_ids=env_context.get("policy_ids", []),
                        )
                        all_knowledge.extend(layers[layer_key].knowledge_uuids)
                        all_resources.extend(layers[layer_key].resource_ids)
                        all_policies.extend(layers[layer_key].policy_ids)
                    except Exception as e:
                        logger.warning("failed_to_get_team_environment_context", error=str(e), environment_id=env_id)

        # 4. Layer 3: Project context
        if project_id:
            try:
                project_context = await _get_or_create_context(client, "project", project_id, org_id)
                layers["project"] = ContextData(
                    knowledge_uuids=project_context.get("knowledge_uuids", []),
                    resource_ids=project_context.get("resource_ids", []),
                    policy_ids=project_context.get("policy_ids", []),
                )
                all_knowledge.extend(layers["project"].knowledge_uuids)
                all_resources.extend(layers["project"].resource_ids)
                all_policies.extend(layers["project"].policy_ids)
            except Exception as e:
                logger.warning("failed_to_get_project_context", error=str(e), project_id=project_id)

        # 5. Layer 4: Entity's own context
        try:
            entity_context = await _get_or_create_context(client, entity_type, entity_id, org_id)
            layers[entity_type] = ContextData(
                knowledge_uuids=entity_context.get("knowledge_uuids", []),
                resource_ids=entity_context.get("resource_ids", []),
                policy_ids=entity_context.get("policy_ids", []),
            )
            all_knowledge.extend(layers[entity_type].knowledge_uuids)
            all_resources.extend(layers[entity_type].resource_ids)
            all_policies.extend(layers[entity_type].policy_ids)
        except Exception as e:
            logger.warning("failed_to_get_entity_context", error=str(e), entity_type=entity_type, entity_id=entity_id)

        # Deduplicate while preserving order
        unique_knowledge = list(dict.fromkeys(all_knowledge))
        unique_resources = list(dict.fromkeys(all_resources))
        unique_policies = list(dict.fromkeys(all_policies))

        logger.info(
            "context_resolved",
            entity_type=entity_type,
            entity_id=entity_id,
            layers_count=len(layers),
            environment_count=len(environment_ids),
            total_knowledge=len(unique_knowledge),
            total_resources=len(unique_resources),
            total_policies=len(unique_policies),
            org_id=org_id,
        )

        return ResolvedContextResponse(
            entity_id=entity_id,
            entity_type=entity_type,
            environment_id=environment_ids[0] if environment_ids else None,
            team_id=team_id,
            project_id=project_id,
            knowledge_uuids=unique_knowledge,
            resource_ids=unique_resources,
            policy_ids=unique_policies,
            layers=layers,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("resolve_context_failed", error=str(e), entity_type=entity_type, entity_id=entity_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve {entity_type} context: {str(e)}"
        )


# Convenience endpoints for workers
@router.get("/agents/{agent_id}/context/resolved", response_model=ResolvedContextResponse)
async def resolve_agent_context(
    agent_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Convenience endpoint to resolve full context for an agent.

    Fetches and merges context from:
    1. ALL agent environments (many-to-many)
    2. Team (if agent belongs to a team)
    3. ALL team environments
    4. Project (if assigned)
    5. Agent's own context

    Workers should call this endpoint to get all knowledge, resources, and policies.
    """
    return await resolve_context("agent", agent_id, request, organization)


@router.get("/teams/{team_id}/context/resolved", response_model=ResolvedContextResponse)
async def resolve_team_context(
    team_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Convenience endpoint to resolve full context for a team.

    Fetches and merges context from:
    1. ALL team environments (many-to-many)
    2. Project (if assigned)
    3. Team's own context

    Workers should call this endpoint to get all knowledge, resources, and policies.
    """
    return await resolve_context("team", team_id, request, organization)
