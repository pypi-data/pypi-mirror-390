"""
Execution Environment Router - Resolve execution environment for agents/teams

This router provides workers with resolved execution environment configuration:
- Fetches agent/team execution_environment from database
- Resolves secret names to actual values from Kubiya API
- Resolves integration IDs to actual tokens from Kubiya API
- Maps integration tokens to specific env var names (GH_TOKEN, JIRA_TOKEN, etc.)
- Returns complete env var dict ready for worker to inject into execution
"""

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any
import structlog

from control_plane_api.app.middleware.auth import get_current_organization
from control_plane_api.app.lib.supabase import get_supabase
from control_plane_api.app.lib.kubiya_client import KUBIYA_API_BASE

logger = structlog.get_logger()

router = APIRouter(prefix="/execution-environment", tags=["execution-environment"])


# Integration type to environment variable name mapping
INTEGRATION_ENV_VAR_MAP = {
    "github": "GH_TOKEN",
    "github_app": "GITHUB_TOKEN",
    "jira": "JIRA_TOKEN",
    "slack": "SLACK_TOKEN",
    "aws": "AWS_ACCESS_KEY_ID",  # Note: AWS might need multiple vars
    "aws-serviceaccount": "AWS_ROLE_ARN",
    "kubernetes": "KUBECONFIG",
}


async def resolve_secret_value(
    secret_name: str,
    token: str,
    org_id: str,
) -> str:
    """
    Resolve a secret name to its actual value from Kubiya API.

    Args:
        secret_name: Name of the secret to resolve
        token: Kubiya API token
        org_id: Organization ID

    Returns:
        Secret value as string
    """
    headers = {
        "Authorization": f"UserKey {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Kubiya-Client": "agent-control-plane",
        "X-Organization-ID": org_id,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{KUBIYA_API_BASE}/api/v2/secrets/get_value/{secret_name}",
            headers=headers,
        )

        if response.status_code == 200:
            return response.text
        else:
            logger.warning(
                "secret_resolution_failed",
                secret_name=secret_name[:20],
                status=response.status_code,
            )
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to resolve secret '{secret_name}': {response.text[:200]}",
            )


async def resolve_integration_token(
    integration_id: str,
    integration_type: str,
    token: str,
    org_id: str,
) -> Dict[str, str]:
    """
    Resolve an integration ID to its actual token from Kubiya API.

    Args:
        integration_id: Integration UUID
        integration_type: Type of integration (github, jira, etc.)
        token: Kubiya API token
        org_id: Organization ID

    Returns:
        Dict with env_var_name and token value
    """
    headers = {
        "Authorization": f"UserKey {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Kubiya-Client": "agent-control-plane",
        "X-Organization-ID": org_id,
    }

    # Build token URL based on integration type
    integration_type_lower = integration_type.lower()

    if integration_type_lower == "github":
        token_url = f"{KUBIYA_API_BASE}/api/v1/integration/github/token/{integration_id}"
    elif integration_type_lower == "github_app":
        token_url = f"{KUBIYA_API_BASE}/api/v1/integration/github_app/token/{integration_id}"
    elif integration_type_lower == "jira":
        token_url = f"{KUBIYA_API_BASE}/api/v1/integration/jira/token/{integration_id}"
    else:
        logger.warning(
            "unsupported_integration_type",
            integration_type=integration_type,
            integration_id=integration_id[:8],
        )
        # For unsupported types, skip
        return {}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(token_url, headers=headers)

        if response.status_code == 200:
            # Try to parse as JSON first
            try:
                token_data = response.json()
                token_value = token_data.get("token", response.text)
            except:
                # If not JSON, use plain text
                token_value = response.text

            # Map to env var name
            env_var_name = INTEGRATION_ENV_VAR_MAP.get(integration_type_lower, f"{integration_type.upper()}_TOKEN")

            return {env_var_name: token_value}
        else:
            logger.warning(
                "integration_token_resolution_failed",
                integration_id=integration_id[:8],
                integration_type=integration_type,
                status=response.status_code,
            )
            # Don't fail the entire request for one integration
            return {}


async def resolve_environment_configs(
    environment_ids: list[str],
    org_id: str,
) -> Dict[str, Any]:
    """
    Resolve execution environment configs from a list of environment IDs.
    Merges configs from all environments.

    Args:
        environment_ids: List of environment IDs
        org_id: Organization ID

    Returns:
        Merged execution environment dict with env_vars, secrets, integration_ids
    """
    if not environment_ids:
        return {"env_vars": {}, "secrets": [], "integration_ids": []}

    supabase = get_supabase()

    # Fetch all environments
    result = (
        supabase.table("environments")
        .select("execution_environment")
        .in_("id", environment_ids)
        .eq("organization_id", org_id)
        .execute()
    )

    # Merge all environment configs
    merged_env_vars = {}
    merged_secrets = set()
    merged_integration_ids = set()

    for env in result.data:
        env_config = env.get("execution_environment", {})

        # Merge env vars (later environments override earlier ones)
        merged_env_vars.update(env_config.get("env_vars", {}))

        # Collect secrets (union)
        merged_secrets.update(env_config.get("secrets", []))

        # Collect integration IDs (union)
        merged_integration_ids.update(env_config.get("integration_ids", []))

    return {
        "env_vars": merged_env_vars,
        "secrets": list(merged_secrets),
        "integration_ids": list(merged_integration_ids),
    }


@router.get("/agents/{agent_id}/resolved")
async def get_agent_execution_environment(
    agent_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
) -> Dict[str, str]:
    """
    Get resolved execution environment for an agent.

    This endpoint:
    1. Fetches agent's execution_environment and environment_ids from database
    2. Fetches and merges execution configs from all associated environments
    3. Merges agent's own execution_environment (agent config overrides environment)
    4. Resolves all secret names to actual values
    5. Resolves all integration IDs to actual tokens
    6. Maps integration tokens to specific env var names
    7. Returns merged env var dict

    Inheritance order (later overrides earlier):
    - Environment 1 execution_environment
    - Environment 2 execution_environment
    - ...
    - Agent execution_environment

    Returns:
        Dict of environment variables ready to inject into agent execution
    """
    try:
        token = request.state.kubiya_token
        org_id = organization["id"]
        supabase = get_supabase()

        # Fetch agent with environment associations
        result = supabase.table("agents").select("execution_environment, environment_ids").eq("id", agent_id).eq("organization_id", org_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        agent = result.data[0]

        # Get environment-level configs first
        environment_ids = agent.get("environment_ids", [])
        env_config = await resolve_environment_configs(environment_ids, org_id)

        # Get agent-level config
        agent_config = agent.get("execution_environment", {})

        # Merge: environment config + agent config (agent overrides environment)
        execution_environment = {
            "env_vars": {**env_config.get("env_vars", {}), **agent_config.get("env_vars", {})},
            "secrets": list(set(env_config.get("secrets", []) + agent_config.get("secrets", []))),
            "integration_ids": list(set(env_config.get("integration_ids", []) + agent_config.get("integration_ids", []))),
        }

        # Start with custom env vars
        resolved_env_vars = dict(execution_environment.get("env_vars", {}))

        # Resolve secrets
        secrets = execution_environment.get("secrets", [])
        for secret_name in secrets:
            try:
                secret_value = await resolve_secret_value(secret_name, token, org_id)
                resolved_env_vars[secret_name] = secret_value
                logger.info(
                    "secret_resolved",
                    agent_id=agent_id[:8],
                    secret_name=secret_name[:20],
                )
            except Exception as e:
                logger.error(
                    "secret_resolution_error",
                    agent_id=agent_id[:8],
                    secret_name=secret_name[:20],
                    error=str(e),
                )
                # Continue with other secrets even if one fails

        # Resolve integrations
        integration_ids = execution_environment.get("integration_ids", [])
        if integration_ids:
            # First, fetch integration details to get types
            headers = {
                "Authorization": f"UserKey {token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Kubiya-Client": "agent-control-plane",
                "X-Organization-ID": org_id,
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{KUBIYA_API_BASE}/api/v2/integrations?full=true",
                    headers=headers,
                )

                if response.status_code == 200:
                    all_integrations = response.json()

                    for integration_id in integration_ids:
                        # Find integration by UUID
                        integration = next(
                            (i for i in all_integrations if i.get("uuid") == integration_id),
                            None
                        )

                        if integration:
                            integration_type = integration.get("integration_type", "")
                            try:
                                token_env_vars = await resolve_integration_token(
                                    integration_id,
                                    integration_type,
                                    token,
                                    org_id,
                                )
                                resolved_env_vars.update(token_env_vars)
                                logger.info(
                                    "integration_resolved",
                                    agent_id=agent_id[:8],
                                    integration_id=integration_id[:8],
                                    integration_type=integration_type,
                                    env_vars=list(token_env_vars.keys()),
                                )
                            except Exception as e:
                                logger.error(
                                    "integration_resolution_error",
                                    agent_id=agent_id[:8],
                                    integration_id=integration_id[:8],
                                    error=str(e),
                                )
                        else:
                            logger.warning(
                                "integration_not_found",
                                agent_id=agent_id[:8],
                                integration_id=integration_id[:8],
                            )

        logger.info(
            "execution_environment_resolved",
            agent_id=agent_id[:8],
            env_var_count=len(resolved_env_vars),
            env_var_keys=list(resolved_env_vars.keys()),
        )

        return resolved_env_vars

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "execution_environment_resolution_error",
            agent_id=agent_id[:8],
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(status_code=500, detail=f"Failed to resolve execution environment: {str(e)}")


@router.get("/teams/{team_id}/resolved")
async def get_team_execution_environment(
    team_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
) -> Dict[str, str]:
    """
    Get resolved execution environment for a team.

    This endpoint:
    1. Fetches team's execution_environment and environment_ids from database
    2. Fetches and merges execution configs from all associated environments
    3. Merges team's own execution_environment (team config overrides environment)
    4. Resolves all secret names to actual values
    5. Resolves all integration IDs to actual tokens
    6. Maps integration tokens to specific env var names
    7. Returns merged env var dict

    Inheritance order (later overrides earlier):
    - Environment 1 execution_environment
    - Environment 2 execution_environment
    - ...
    - Team execution_environment

    Returns:
        Dict of environment variables ready to inject into team execution
    """
    try:
        token = request.state.kubiya_token
        org_id = organization["id"]
        supabase = get_supabase()

        # Fetch team with environment associations
        result = supabase.table("teams").select("execution_environment, environment_ids").eq("id", team_id).eq("organization_id", org_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

        team = result.data[0]

        # Get environment-level configs first
        environment_ids = team.get("environment_ids", [])
        env_config = await resolve_environment_configs(environment_ids, org_id)

        # Get team-level config
        team_config = team.get("execution_environment", {})

        # Merge: environment config + team config (team overrides environment)
        execution_environment = {
            "env_vars": {**env_config.get("env_vars", {}), **team_config.get("env_vars", {})},
            "secrets": list(set(env_config.get("secrets", []) + team_config.get("secrets", []))),
            "integration_ids": list(set(env_config.get("integration_ids", []) + team_config.get("integration_ids", []))),
        }

        # Start with custom env vars
        resolved_env_vars = dict(execution_environment.get("env_vars", {}))

        # Resolve secrets
        secrets = execution_environment.get("secrets", [])
        for secret_name in secrets:
            try:
                secret_value = await resolve_secret_value(secret_name, token, org_id)
                resolved_env_vars[secret_name] = secret_value
                logger.info(
                    "secret_resolved",
                    team_id=team_id[:8],
                    secret_name=secret_name[:20],
                )
            except Exception as e:
                logger.error(
                    "secret_resolution_error",
                    team_id=team_id[:8],
                    secret_name=secret_name[:20],
                    error=str(e),
                )
                # Continue with other secrets even if one fails

        # Resolve integrations
        integration_ids = execution_environment.get("integration_ids", [])
        if integration_ids:
            # First, fetch integration details to get types
            headers = {
                "Authorization": f"UserKey {token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Kubiya-Client": "agent-control-plane",
                "X-Organization-ID": org_id,
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{KUBIYA_API_BASE}/api/v2/integrations?full=true",
                    headers=headers,
                )

                if response.status_code == 200:
                    all_integrations = response.json()

                    for integration_id in integration_ids:
                        # Find integration by UUID
                        integration = next(
                            (i for i in all_integrations if i.get("uuid") == integration_id),
                            None
                        )

                        if integration:
                            integration_type = integration.get("integration_type", "")
                            try:
                                token_env_vars = await resolve_integration_token(
                                    integration_id,
                                    integration_type,
                                    token,
                                    org_id,
                                )
                                resolved_env_vars.update(token_env_vars)
                                logger.info(
                                    "integration_resolved",
                                    team_id=team_id[:8],
                                    integration_id=integration_id[:8],
                                    integration_type=integration_type,
                                    env_vars=list(token_env_vars.keys()),
                                )
                            except Exception as e:
                                logger.error(
                                    "integration_resolution_error",
                                    team_id=team_id[:8],
                                    integration_id=integration_id[:8],
                                    error=str(e),
                                )
                        else:
                            logger.warning(
                                "integration_not_found",
                                team_id=team_id[:8],
                                integration_id=integration_id[:8],
                            )

        logger.info(
            "execution_environment_resolved",
            team_id=team_id[:8],
            env_var_count=len(resolved_env_vars),
            env_var_keys=list(resolved_env_vars.keys()),
        )

        return resolved_env_vars

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "execution_environment_resolution_error",
            team_id=team_id[:8],
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(status_code=500, detail=f"Failed to resolve execution environment: {str(e)}")
