"""
Job execution logic for routing and parameter substitution.

This module handles:
- Dynamic executor routing (auto/specific queue/environment)
- Prompt template parameter substitution
- Worker queue selection based on availability
"""

import re
import structlog
from typing import Dict, Any, Optional, Tuple

logger = structlog.get_logger()


def substitute_prompt_parameters(prompt_template: str, parameters: Dict[str, Any]) -> str:
    """
    Substitute parameters in prompt template.

    Template variables use {{variable_name}} syntax.

    Example:
        prompt_template = "Run a backup of {{database}} at {{time}}"
        parameters = {"database": "production", "time": "5pm"}
        result = "Run a backup of production at 5pm"

    Args:
        prompt_template: Prompt template with {{variables}}
        parameters: Dictionary of parameter values

    Returns:
        Prompt with substituted values

    Raises:
        ValueError: If required parameters are missing
    """
    # Find all variables in template
    variables = re.findall(r"\{\{(\w+)\}\}", prompt_template)

    # Check for missing parameters
    missing = [var for var in variables if var not in parameters]
    if missing:
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")

    # Substitute variables
    result = prompt_template
    for var_name, var_value in parameters.items():
        result = result.replace(f"{{{{{var_name}}}}}", str(var_value))

    return result


async def get_available_worker_queues(
    organization_id: str,
    environment_name: Optional[str] = None
) -> list[Dict[str, Any]]:
    """
    Get list of worker queues with active workers.

    Queries the worker_queues table and counts active workers from Redis heartbeats.

    Args:
        organization_id: Organization ID for multi-tenant filtering
        environment_name: Optional environment name filter

    Returns:
        List of worker queue dictionaries with metadata
    """
    from control_plane_api.app.lib.supabase import get_supabase
    from control_plane_api.app.routers.worker_queues import get_active_workers_from_redis

    client = get_supabase()

    try:
        # Query worker_queues table for active queues
        query = (
            client.table("worker_queues")
            .select("id, name, environment_id, status, environments(name)")
            .eq("organization_id", organization_id)
            .eq("status", "active")
        )

        # Filter by environment if specified
        if environment_name:
            # First get the environment ID
            env_result = (
                client.table("environments")
                .select("id")
                .eq("organization_id", organization_id)
                .eq("name", environment_name)
                .maybe_single()
                .execute()
            )
            if env_result.data:
                query = query.eq("environment_id", env_result.data["id"])
            else:
                logger.warning(
                    "environment_not_found",
                    organization_id=organization_id,
                    environment_name=environment_name
                )
                return []

        result = query.execute()

        if not result.data:
            logger.info("no_active_worker_queues_found", organization_id=organization_id)
            return []

        # Get active workers from Redis heartbeats
        active_workers_data = await get_active_workers_from_redis(organization_id)

        logger.info(
            "checking_active_workers",
            organization_id=organization_id,
            total_queues_in_db=len(result.data),
            active_workers_count=len(active_workers_data)
        )

        # Count workers per queue
        worker_counts = {}
        for worker_id, worker_data in active_workers_data.items():
            queue_id = worker_data.get("worker_queue_id")
            if queue_id:
                worker_counts[queue_id] = worker_counts.get(queue_id, 0) + 1

        # Transform to expected format
        worker_queues = []
        for queue in result.data:
            active_worker_count = worker_counts.get(queue["id"], 0)

            logger.debug(
                "checking_queue_for_active_workers",
                queue_id=queue["id"],
                queue_name=queue.get("name"),
                active_worker_count=active_worker_count
            )

            # Only include queues with active workers
            if active_worker_count > 0:
                env_data = queue.get("environments", {})
                worker_queues.append({
                    "queue_name": queue["id"],  # Use queue ID as the task queue name
                    "environment_name": env_data.get("name") if env_data else None,
                    "active_workers": active_worker_count,
                    "idle_workers": 0,  # Not tracked separately
                    "total_workers": active_worker_count,
                })

        logger.info(
            "found_available_worker_queues",
            organization_id=organization_id,
            count=len(worker_queues),
            worker_counts=worker_counts
        )

        return worker_queues

    except Exception as e:
        logger.error("failed_to_get_available_worker_queues", error=str(e), organization_id=organization_id)
        return []


async def select_worker_queue(
    organization_id: str,
    executor_type: str,
    worker_queue_name: Optional[str] = None,
    environment_name: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Select appropriate worker queue for job execution.

    Routing logic:
    - AUTO: Select first available queue with idle workers (prefer idle over active)
    - SPECIFIC_QUEUE: Use provided worker_queue_name
    - ENVIRONMENT: Select first available queue in specified environment

    Args:
        organization_id: Organization ID
        executor_type: Routing type ("auto", "specific_queue", "environment")
        worker_queue_name: Explicit queue name (for SPECIFIC_QUEUE)
        environment_name: Environment name (for ENVIRONMENT routing)

    Returns:
        Tuple of (worker_queue_name, environment_name) or (None, None) if no workers available
    """
    if executor_type == "specific_queue":
        if not worker_queue_name:
            raise ValueError("worker_queue_name is required for 'specific_queue' executor type")
        return worker_queue_name, environment_name

    # AUTO or ENVIRONMENT routing - need to find available workers
    available_queues = await get_available_worker_queues(organization_id, environment_name)

    if not available_queues:
        logger.warning(
            "no_available_worker_queues",
            organization_id=organization_id,
            executor_type=executor_type,
            environment_name=environment_name,
        )
        return None, None

    # Sort by idle workers first, then by total workers
    # This ensures we prefer queues with capacity
    available_queues.sort(
        key=lambda q: (q["idle_workers"], q["total_workers"]),
        reverse=True
    )

    selected = available_queues[0]
    logger.info(
        "selected_worker_queue",
        organization_id=organization_id,
        queue_name=selected["queue_name"],
        environment_name=selected["environment_name"],
        idle_workers=selected["idle_workers"],
        total_workers=selected["total_workers"],
    )

    return selected["queue_name"], selected["environment_name"]


async def resolve_job_entity(
    supabase_client,
    organization_id: str,
    planning_mode: str,
    entity_type: Optional[str],
    entity_id: Optional[str],
) -> Tuple[str, str, str]:
    """
    Resolve job entity (agent/team/workflow) and return execution details.

    For predefined modes, validates that the entity exists and returns its details.
    For on_the_fly mode, returns None values (planner will determine execution).

    Args:
        supabase_client: Supabase client instance
        organization_id: Organization ID
        planning_mode: Planning mode (on_the_fly, predefined_agent, etc.)
        entity_type: Entity type (agent/team/workflow)
        entity_id: Entity ID

    Returns:
        Tuple of (execution_type, entity_id, entity_name)

    Raises:
        ValueError: If entity doesn't exist or validation fails
    """
    if planning_mode == "on_the_fly":
        # Planner will determine execution
        return "agent", None, None

    # Validate entity exists
    if not entity_type or not entity_id:
        raise ValueError(f"entity_type and entity_id are required for planning_mode '{planning_mode}'")

    table_name = f"{entity_type}s"  # agents, teams, workflows

    try:
        result = (
            supabase_client.table(table_name)
            .select("id, name")
            .eq("id", entity_id)
            .eq("organization_id", organization_id)
            .execute()
        )

        if not result.data:
            raise ValueError(f"{entity_type} with ID {entity_id} not found")

        entity = result.data[0]
        return entity_type, entity["id"], entity["name"]

    except Exception as e:
        logger.error(
            "failed_to_resolve_job_entity",
            error=str(e),
            planning_mode=planning_mode,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        raise ValueError(f"Failed to resolve {entity_type}: {str(e)}")


def merge_execution_config(
    base_config: Dict[str, Any],
    override_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Merge base job config with execution-specific overrides.

    Args:
        base_config: Base configuration from job definition
        override_config: Optional overrides for this execution

    Returns:
        Merged configuration dictionary
    """
    if not override_config:
        return base_config.copy()

    # Deep merge
    merged = base_config.copy()
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value

    return merged
