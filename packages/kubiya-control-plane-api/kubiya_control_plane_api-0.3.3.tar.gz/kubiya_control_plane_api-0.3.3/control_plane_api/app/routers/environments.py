"""
Environments router - Clean API for environment management.

This router provides /environments endpoints that map to the environments table.
The naming "environments" is internal - externally we call them "environments".
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import structlog
import uuid
import os

from control_plane_api.app.middleware.auth import get_current_organization
from control_plane_api.app.lib.supabase import get_supabase
from control_plane_api.app.lib.temporal_client import get_temporal_client

logger = structlog.get_logger()

router = APIRouter()


# Execution Environment Model (shared with agents/teams)
class ExecutionEnvironment(BaseModel):
    """Execution environment configuration - env vars, secrets, and integration credentials"""
    env_vars: dict[str, str] = Field(default_factory=dict, description="Environment variables (key-value pairs)")
    secrets: list[str] = Field(default_factory=list, description="Secret names from Kubiya vault")
    integration_ids: list[str] = Field(default_factory=list, description="Integration UUIDs for delegated credentials")


# Pydantic schemas
class EnvironmentCreate(BaseModel):
    name: str = Field(..., description="Environment name (e.g., default, production)", min_length=2, max_length=100)
    display_name: str | None = Field(None, description="User-friendly display name")
    description: str | None = Field(None, description="Environment description")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    settings: dict = Field(default_factory=dict, description="Environment settings")
    execution_environment: ExecutionEnvironment | None = Field(None, description="Execution environment configuration")
    # Note: priority and policy_ids not supported by environments table


class EnvironmentUpdate(BaseModel):
    name: str | None = None
    display_name: str | None = None
    description: str | None = None
    tags: List[str] | None = None
    settings: dict | None = None
    status: str | None = None
    execution_environment: ExecutionEnvironment | None = None
    # Note: priority and policy_ids not supported by environments table


class EnvironmentResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    display_name: str | None
    description: str | None
    tags: List[str]
    settings: dict
    status: str
    created_at: str
    updated_at: str
    created_by: str | None

    # Temporal Cloud provisioning fields
    worker_token: str | None = None
    provisioning_workflow_id: str | None = None
    provisioned_at: str | None = None
    error_message: str | None = None
    temporal_namespace_id: str | None = None

    # Worker metrics (deprecated at environment level, use worker_queues)
    active_workers: int = 0
    idle_workers: int = 0
    busy_workers: int = 0

    # Skills (populated from associations)
    skill_ids: List[str] = []
    skills: List[dict] = []

    # Execution environment configuration
    execution_environment: dict = {}


class WorkerCommandResponse(BaseModel):
    """Response with worker registration command"""
    worker_token: str
    environment_name: str
    command: str
    command_parts: dict
    namespace_status: str
    can_register: bool
    provisioning_workflow_id: str | None = None


def ensure_default_environment(organization: dict) -> Optional[dict]:
    """
    Ensure the organization has a default environment.
    Creates one if it doesn't exist.
    """
    try:
        client = get_supabase()

        # Check if default environment exists
        existing = (
            client.table("environments")
            .select("*")
            .eq("organization_id", organization["id"])
            .eq("name", "default")
            .execute()
        )

        if existing.data:
            return existing.data[0]

        # Create default environment
        env_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        default_env = {
            "id": env_id,
            "organization_id": organization["id"],
            "name": "default",
            "display_name": "Default Environment",
            "description": "Default environment for all workers",
            "tags": [],
            "settings": {},
            "status": "active",
            "created_at": now,
            "updated_at": now,
            "created_by": organization.get("user_id"),
        }

        result = client.table("environments").insert(default_env).execute()

        if result.data:
            logger.info(
                "default_environment_created",
                environment_id=env_id,
                org_id=organization["id"],
            )
            return result.data[0]

        return None

    except Exception as e:
        logger.error("ensure_default_environment_failed", error=str(e), org_id=organization.get("id"))
        return None


def get_environment_skills(client, organization_id: str, environment_id: str) -> tuple[List[str], List[dict]]:
    """Get skills associated with an environment"""
    try:
        # Get associations with full skill data
        result = (
            client.table("skill_associations")
            .select("skill_id, configuration_override, skills(*)")
            .eq("organization_id", organization_id)
            .eq("entity_type", "environment")
            .eq("entity_id", environment_id)
            .execute()
        )

        skill_ids = []
        skills = []

        for item in result.data:
            skill_data = item.get("skills")
            if skill_data:
                skill_ids.append(skill_data["id"])

                # Merge configuration with override
                config = skill_data.get("configuration", {})
                override = item.get("configuration_override")
                if override:
                    config = {**config, **override}

                skills.append({
                    "id": skill_data["id"],
                    "name": skill_data["name"],
                    "type": skill_data["skill_type"],
                    "description": skill_data.get("description"),
                    "enabled": skill_data.get("enabled", True),
                    "configuration": config,
                })

        return skill_ids, skills

    except Exception as e:
        logger.error("get_environment_skills_failed", error=str(e), environment_id=environment_id)
        return [], []


@router.post("", response_model=EnvironmentResponse, status_code=status.HTTP_201_CREATED)
async def create_environment(
    env_data: EnvironmentCreate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Create a new environment.

    If this is the first environment for the organization, it will trigger
    Temporal Cloud namespace provisioning workflow.
    """
    try:
        client = get_supabase()

        # Check if environment name already exists
        existing = (
            client.table("environments")
            .select("id")
            .eq("organization_id", organization["id"])
            .eq("name", env_data.name)
            .execute()
        )

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Environment with name '{env_data.name}' already exists"
            )

        # Check if this is the first environment
        all_envs = (
            client.table("environments")
            .select("id")
            .eq("organization_id", organization["id"])
            .execute()
        )
        is_first_env = len(all_envs.data or []) == 0

        # Check if namespace already exists
        namespace_result = (
            client.table("temporal_namespaces")
            .select("*")
            .eq("organization_id", organization["id"])
            .execute()
        )
        has_namespace = bool(namespace_result.data)
        needs_provisioning = is_first_env and not has_namespace

        env_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        # Set initial status
        initial_status = "provisioning" if needs_provisioning else "ready"

        env_record = {
            "id": env_id,
            "organization_id": organization["id"],
            "name": env_data.name,
            "display_name": env_data.display_name or env_data.name,
            "description": env_data.description,
            "tags": env_data.tags,
            "settings": env_data.settings,
            "status": initial_status,
            "created_at": now,
            "updated_at": now,
            "created_by": organization.get("user_id"),
            "worker_token": str(uuid.uuid4()),
            "execution_environment": env_data.execution_environment.model_dump() if env_data.execution_environment else {},
        }

        result = client.table("environments").insert(env_record).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create environment"
            )

        environment = result.data[0]

        # Trigger namespace provisioning if needed
        if needs_provisioning:
            try:
                from control_plane_api.app.workflows.namespace_provisioning import (
                    ProvisionTemporalNamespaceWorkflow,
                    ProvisionNamespaceInput,
                )

                temporal_client = await get_temporal_client()
                account_id = os.environ.get("TEMPORAL_CLOUD_ACCOUNT_ID", "default-account")

                workflow_input = ProvisionNamespaceInput(
                    organization_id=organization["id"],
                    organization_name=organization.get("name", organization["id"]),
                    task_queue_id=env_id,
                    account_id=account_id,
                    region=os.environ.get("TEMPORAL_CLOUD_REGION", "aws-us-east-1"),
                )

                workflow_handle = await temporal_client.start_workflow(
                    ProvisionTemporalNamespaceWorkflow.run,
                    workflow_input,
                    id=f"provision-namespace-{organization['id']}",
                    task_queue="agent-control-plane",
                )

                client.table("environments").update({
                    "provisioning_workflow_id": workflow_handle.id,
                    "updated_at": datetime.utcnow().isoformat(),
                }).eq("id", env_id).execute()

                environment["provisioning_workflow_id"] = workflow_handle.id

                logger.info(
                    "namespace_provisioning_workflow_started",
                    workflow_id=workflow_handle.id,
                    environment_id=env_id,
                    org_id=organization["id"],
                )
            except Exception as e:
                logger.error(
                    "failed_to_start_provisioning_workflow",
                    error=str(e),
                    environment_id=env_id,
                    org_id=organization["id"],
                )
                client.table("environments").update({
                    "status": "error",
                    "error_message": f"Failed to start provisioning: {str(e)}",
                    "updated_at": datetime.utcnow().isoformat(),
                }).eq("id", env_id).execute()
                environment["status"] = "error"
                environment["error_message"] = f"Failed to start provisioning: {str(e)}"

        logger.info(
            "environment_created",
            environment_id=env_id,
            environment_name=environment["name"],
            org_id=organization["id"],
            needs_provisioning=needs_provisioning,
        )

        return EnvironmentResponse(
            **environment,
            active_workers=0,
            idle_workers=0,
            busy_workers=0,
            skill_ids=[],
            skills=[],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("environment_creation_failed", error=str(e), org_id=organization["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create environment: {str(e)}"
        )


@router.get("", response_model=List[EnvironmentResponse])
async def list_environments(
    request: Request,
    status_filter: str | None = None,
    organization: dict = Depends(get_current_organization),
):
    """List all environments in the organization"""
    try:
        client = get_supabase()

        # Ensure default environment exists
        ensure_default_environment(organization)

        # Query environments
        query = client.table("environments").select("*").eq("organization_id", organization["id"])

        if status_filter:
            query = query.eq("status", status_filter)

        query = query.order("created_at", desc=False)
        result = query.execute()

        if not result.data:
            return []

        # BATCH FETCH: Get all skills for all environments in one query
        environment_ids = [env["id"] for env in result.data]
        skills_result = (
            client.table("skill_associations")
            .select("entity_id, skill_id, configuration_override, skills(*)")
            .eq("organization_id", organization["id"])
            .eq("entity_type", "environment")
            .in_("entity_id", environment_ids)
            .execute()
        )

        # Group skills by environment_id
        skills_by_env = {}
        for item in skills_result.data or []:
            env_id = item["entity_id"]
            skill_data = item.get("skills")
            if skill_data:
                if env_id not in skills_by_env:
                    skills_by_env[env_id] = {"ids": [], "data": []}

                # Merge configuration with override
                config = skill_data.get("configuration", {})
                override = item.get("configuration_override")
                if override:
                    config = {**config, **override}

                skills_by_env[env_id]["ids"].append(skill_data["id"])
                skills_by_env[env_id]["data"].append({
                    "id": skill_data["id"],
                    "name": skill_data["name"],
                    "type": skill_data["skill_type"],
                    "description": skill_data.get("description"),
                    "enabled": skill_data.get("enabled", True),
                    "configuration": config,
                })

        # Build environment responses
        environments = []
        for env in result.data:
            env_skills = skills_by_env.get(env["id"], {"ids": [], "data": []})

            environments.append(
                EnvironmentResponse(
                    **env,
                    active_workers=0,
                    idle_workers=0,
                    busy_workers=0,
                    skill_ids=env_skills["ids"],
                    skills=env_skills["data"],
                )
            )

        logger.info(
            "environments_listed",
            count=len(environments),
            org_id=organization["id"],
        )

        return environments

    except Exception as e:
        logger.error("environments_list_failed", error=str(e), org_id=organization["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list environments: {str(e)}"
        )


@router.get("/{environment_id}", response_model=EnvironmentResponse)
async def get_environment(
    environment_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Get a specific environment by ID"""
    try:
        client = get_supabase()

        result = (
            client.table("environments")
            .select("*")
            .eq("id", environment_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Environment not found")

        environment = result.data

        # Get skills
        skill_ids, skills = get_environment_skills(client, organization["id"], environment_id)

        return EnvironmentResponse(
            **environment,
            active_workers=0,
            idle_workers=0,
            busy_workers=0,
            skill_ids=skill_ids,
            skills=skills,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("environment_get_failed", error=str(e), environment_id=environment_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get environment: {str(e)}"
        )


@router.patch("/{environment_id}", response_model=EnvironmentResponse)
async def update_environment(
    environment_id: str,
    env_data: EnvironmentUpdate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Update an environment"""
    try:
        client = get_supabase()

        # Check if environment exists
        existing = (
            client.table("environments")
            .select("id")
            .eq("id", environment_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not existing.data:
            raise HTTPException(status_code=404, detail="Environment not found")

        # Build update dict
        update_data = env_data.model_dump(exclude_unset=True)

        # Convert execution_environment Pydantic model to dict if present
        if "execution_environment" in update_data and update_data["execution_environment"]:
            if hasattr(update_data["execution_environment"], "model_dump"):
                update_data["execution_environment"] = update_data["execution_environment"].model_dump()

        update_data["updated_at"] = datetime.utcnow().isoformat()

        # Update environment
        result = (
            client.table("environments")
            .update(update_data)
            .eq("id", environment_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update environment"
            )

        environment = result.data[0]

        # Get skills
        skill_ids, skills = get_environment_skills(client, organization["id"], environment_id)

        logger.info(
            "environment_updated",
            environment_id=environment_id,
            org_id=organization["id"],
        )

        return EnvironmentResponse(
            **environment,
            active_workers=0,
            idle_workers=0,
            busy_workers=0,
            skill_ids=skill_ids,
            skills=skills,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("environment_update_failed", error=str(e), environment_id=environment_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update environment: {str(e)}"
        )


@router.delete("/{environment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_environment(
    environment_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Delete an environment"""
    try:
        client = get_supabase()

        # Prevent deleting default environment
        env_check = (
            client.table("environments")
            .select("name")
            .eq("id", environment_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if env_check.data and env_check.data.get("name") == "default":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the default environment"
            )

        result = (
            client.table("environments")
            .delete()
            .eq("id", environment_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Environment not found")

        logger.info("environment_deleted", environment_id=environment_id, org_id=organization["id"])

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error("environment_delete_failed", error=str(e), environment_id=environment_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete environment: {str(e)}"
        )


@router.get("/{environment_id}/worker-command", response_model=WorkerCommandResponse)
async def get_worker_registration_command(
    environment_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Get the worker registration command for an environment.

    Returns the kubiya worker start command with the worker token.
    """
    try:
        client = get_supabase()

        # Get environment
        result = (
            client.table("environments")
            .select("*")
            .eq("id", environment_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Environment not found")

        environment = result.data
        worker_token = environment.get("worker_token")

        # Generate worker_token if it doesn't exist
        if not worker_token:
            worker_token = str(uuid.uuid4())
            client.table("environments").update({
                "worker_token": worker_token,
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("id", environment_id).execute()

            logger.info(
                "worker_token_generated",
                environment_id=environment_id,
                org_id=organization["id"],
            )

        environment_name = environment["name"]
        namespace_status = environment.get("status", "unknown")
        provisioning_workflow_id = environment.get("provisioning_workflow_id")

        # Check if namespace is ready
        can_register = namespace_status in ["ready", "active"]

        # Build command
        command = f"kubiya worker start --token {worker_token} --environment {environment_name}"

        command_parts = {
            "binary": "kubiya",
            "subcommand": "worker start",
            "flags": {
                "--token": worker_token,
                "--environment": environment_name,
            },
        }

        logger.info(
            "worker_command_retrieved",
            environment_id=environment_id,
            can_register=can_register,
            status=namespace_status,
            org_id=organization["id"],
        )

        return WorkerCommandResponse(
            worker_token=worker_token,
            environment_name=environment_name,
            command=command,
            command_parts=command_parts,
            namespace_status=namespace_status,
            can_register=can_register,
            provisioning_workflow_id=provisioning_workflow_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("worker_command_get_failed", error=str(e), environment_id=environment_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get worker command: {str(e)}"
        )
