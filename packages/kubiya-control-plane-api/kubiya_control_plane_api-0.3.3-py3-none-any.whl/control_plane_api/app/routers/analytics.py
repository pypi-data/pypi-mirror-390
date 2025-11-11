"""
Analytics router for execution metrics and reporting.

This router provides endpoints for:
1. Persisting analytics data from workers (turns, tool calls, tasks)
2. Querying aggregated analytics for reporting
3. Organization-level metrics and cost tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import structlog
import uuid as uuid_lib

from control_plane_api.app.middleware.auth import get_current_organization
from control_plane_api.app.lib.supabase import get_supabase

logger = structlog.get_logger()

router = APIRouter()


# ============================================================================
# Pydantic Schemas for Analytics Data
# ============================================================================

class TurnMetricsCreate(BaseModel):
    """Schema for creating a turn metrics record"""
    execution_id: str
    turn_number: int
    turn_id: Optional[str] = None
    model: str
    model_provider: Optional[str] = None
    started_at: str  # ISO timestamp
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    total_tokens: int = 0
    input_cost: float = 0.0
    output_cost: float = 0.0
    cache_read_cost: float = 0.0
    cache_creation_cost: float = 0.0
    total_cost: float = 0.0
    finish_reason: Optional[str] = None
    response_preview: Optional[str] = None
    tools_called_count: int = 0
    tools_called_names: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    metrics: dict = Field(default_factory=dict)
    # Agentic Engineering Minutes (AEM) fields
    runtime_minutes: float = 0.0
    model_weight: float = 1.0
    tool_calls_weight: float = 1.0
    aem_value: float = 0.0
    aem_cost: float = 0.0


class ToolCallCreate(BaseModel):
    """Schema for creating a tool call record"""
    execution_id: str
    turn_id: Optional[str] = None  # UUID of the turn (if available)
    tool_name: str
    tool_use_id: Optional[str] = None
    started_at: str  # ISO timestamp
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    tool_input: Optional[dict] = None
    tool_output: Optional[str] = None
    tool_output_size: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class TaskCreate(BaseModel):
    """Schema for creating a task record"""
    execution_id: str
    task_number: Optional[int] = None
    task_id: Optional[str] = None
    task_description: str
    task_type: Optional[str] = None
    status: str = "pending"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class TaskUpdate(BaseModel):
    """Schema for updating a task's status"""
    status: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    result: Optional[str] = None
    error_message: Optional[str] = None


class BatchAnalyticsCreate(BaseModel):
    """Schema for batch creating analytics data (used by workers to send all data at once)"""
    execution_id: str
    turns: List[TurnMetricsCreate] = Field(default_factory=list)
    tool_calls: List[ToolCallCreate] = Field(default_factory=list)
    tasks: List[TaskCreate] = Field(default_factory=list)


# ============================================================================
# Data Persistence Endpoints (Used by Workers)
# ============================================================================

@router.post("/turns", status_code=status.HTTP_201_CREATED)
async def create_turn_metrics(
    turn_data: TurnMetricsCreate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Create a turn metrics record.

    This endpoint is called by workers to persist per-turn LLM metrics
    including tokens, cost, duration, and tool usage.
    """
    try:
        client = get_supabase()

        # Verify execution belongs to organization
        exec_result = client.table("executions").select("id").eq("id", turn_data.execution_id).eq("organization_id", organization["id"]).execute()
        if not exec_result.data:
            raise HTTPException(status_code=404, detail="Execution not found")

        turn_record = {
            "id": str(uuid_lib.uuid4()),
            "organization_id": organization["id"],
            "execution_id": turn_data.execution_id,
            "turn_number": turn_data.turn_number,
            "turn_id": turn_data.turn_id,
            "model": turn_data.model,
            "model_provider": turn_data.model_provider,
            "started_at": turn_data.started_at,
            "completed_at": turn_data.completed_at,
            "duration_ms": turn_data.duration_ms,
            "input_tokens": turn_data.input_tokens,
            "output_tokens": turn_data.output_tokens,
            "cache_read_tokens": turn_data.cache_read_tokens,
            "cache_creation_tokens": turn_data.cache_creation_tokens,
            "total_tokens": turn_data.total_tokens,
            "input_cost": turn_data.input_cost,
            "output_cost": turn_data.output_cost,
            "cache_read_cost": turn_data.cache_read_cost,
            "cache_creation_cost": turn_data.cache_creation_cost,
            "total_cost": turn_data.total_cost,
            "finish_reason": turn_data.finish_reason,
            "response_preview": turn_data.response_preview[:500] if turn_data.response_preview else None,
            "tools_called_count": turn_data.tools_called_count,
            "tools_called_names": turn_data.tools_called_names,
            "error_message": turn_data.error_message,
            "metrics": turn_data.metrics,
            # AEM fields
            "runtime_minutes": turn_data.runtime_minutes,
            "model_weight": turn_data.model_weight,
            "tool_calls_weight": turn_data.tool_calls_weight,
            "aem_value": turn_data.aem_value,
            "aem_cost": turn_data.aem_cost,
        }

        result = client.table("execution_turns").insert(turn_record).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create turn metrics")

        logger.info(
            "turn_metrics_created",
            execution_id=turn_data.execution_id,
            turn_number=turn_data.turn_number,
            model=turn_data.model,
            tokens=turn_data.total_tokens,
            cost=turn_data.total_cost,
            org_id=organization["id"]
        )

        return {"success": True, "turn_id": result.data[0]["id"]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("turn_metrics_create_failed", error=str(e), execution_id=turn_data.execution_id)
        raise HTTPException(status_code=500, detail=f"Failed to create turn metrics: {str(e)}")


@router.post("/tool-calls", status_code=status.HTTP_201_CREATED)
async def create_tool_call(
    tool_call_data: ToolCallCreate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Create a tool call record.

    This endpoint is called by workers to persist tool execution details
    including timing, success/failure, and error information.
    """
    try:
        client = get_supabase()

        # Verify execution belongs to organization
        exec_result = client.table("executions").select("id").eq("id", tool_call_data.execution_id).eq("organization_id", organization["id"]).execute()
        if not exec_result.data:
            raise HTTPException(status_code=404, detail="Execution not found")

        # Truncate tool_output if too large (store first 10KB)
        tool_output = tool_call_data.tool_output
        tool_output_size = len(tool_output) if tool_output else 0
        if tool_output and len(tool_output) > 10000:
            tool_output = tool_output[:10000] + "... [truncated]"

        tool_call_record = {
            "id": str(uuid_lib.uuid4()),
            "organization_id": organization["id"],
            "execution_id": tool_call_data.execution_id,
            "turn_id": tool_call_data.turn_id,
            "tool_name": tool_call_data.tool_name,
            "tool_use_id": tool_call_data.tool_use_id,
            "started_at": tool_call_data.started_at,
            "completed_at": tool_call_data.completed_at,
            "duration_ms": tool_call_data.duration_ms,
            "tool_input": tool_call_data.tool_input,
            "tool_output": tool_output,
            "tool_output_size": tool_output_size,
            "success": tool_call_data.success,
            "error_message": tool_call_data.error_message,
            "error_type": tool_call_data.error_type,
            "custom_metadata": tool_call_data.metadata,
        }

        result = client.table("execution_tool_calls").insert(tool_call_record).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create tool call record")

        logger.info(
            "tool_call_created",
            execution_id=tool_call_data.execution_id,
            tool_name=tool_call_data.tool_name,
            success=tool_call_data.success,
            duration_ms=tool_call_data.duration_ms,
            org_id=organization["id"]
        )

        return {"success": True, "tool_call_id": result.data[0]["id"]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("tool_call_create_failed", error=str(e), execution_id=tool_call_data.execution_id)
        raise HTTPException(status_code=500, detail=f"Failed to create tool call: {str(e)}")


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Create a task record.

    This endpoint is called by workers to persist task tracking information.
    """
    try:
        client = get_supabase()

        # Verify execution belongs to organization
        exec_result = client.table("executions").select("id").eq("id", task_data.execution_id).eq("organization_id", organization["id"]).execute()
        if not exec_result.data:
            raise HTTPException(status_code=404, detail="Execution not found")

        task_record = {
            "id": str(uuid_lib.uuid4()),
            "organization_id": organization["id"],
            "execution_id": task_data.execution_id,
            "task_number": task_data.task_number,
            "task_id": task_data.task_id,
            "task_description": task_data.task_description,
            "task_type": task_data.task_type,
            "status": task_data.status,
            "started_at": task_data.started_at,
            "completed_at": task_data.completed_at,
            "duration_ms": task_data.duration_ms,
            "result": task_data.result,
            "error_message": task_data.error_message,
            "custom_metadata": task_data.metadata,
        }

        result = client.table("execution_tasks").insert(task_record).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create task")

        logger.info(
            "task_created",
            execution_id=task_data.execution_id,
            task_description=task_data.task_description[:100],
            status=task_data.status,
            org_id=organization["id"]
        )

        return {"success": True, "task_id": result.data[0]["id"]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("task_create_failed", error=str(e), execution_id=task_data.execution_id)
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def create_batch_analytics(
    batch_data: BatchAnalyticsCreate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Create analytics data in batch.

    This endpoint allows workers to send all analytics data (turns, tool calls, tasks)
    in a single request, reducing round trips and improving performance.
    """
    try:
        client = get_supabase()

        # Verify execution belongs to organization
        exec_result = client.table("executions").select("id").eq("id", batch_data.execution_id).eq("organization_id", organization["id"]).execute()
        if not exec_result.data:
            raise HTTPException(status_code=404, detail="Execution not found")

        results = {
            "turns_created": 0,
            "tool_calls_created": 0,
            "tasks_created": 0,
            "errors": []
        }

        # Create turns
        if batch_data.turns:
            for turn in batch_data.turns:
                try:
                    turn_record = {
                        "id": str(uuid_lib.uuid4()),
                        "organization_id": organization["id"],
                        "execution_id": batch_data.execution_id,
                        "turn_number": turn.turn_number,
                        "turn_id": turn.turn_id,
                        "model": turn.model,
                        "model_provider": turn.model_provider,
                        "started_at": turn.started_at,
                        "completed_at": turn.completed_at,
                        "duration_ms": turn.duration_ms,
                        "input_tokens": turn.input_tokens,
                        "output_tokens": turn.output_tokens,
                        "cache_read_tokens": turn.cache_read_tokens,
                        "cache_creation_tokens": turn.cache_creation_tokens,
                        "total_tokens": turn.total_tokens,
                        "input_cost": turn.input_cost,
                        "output_cost": turn.output_cost,
                        "cache_read_cost": turn.cache_read_cost,
                        "cache_creation_cost": turn.cache_creation_cost,
                        "total_cost": turn.total_cost,
                        "finish_reason": turn.finish_reason,
                        "response_preview": turn.response_preview[:500] if turn.response_preview else None,
                        "tools_called_count": turn.tools_called_count,
                        "tools_called_names": turn.tools_called_names,
                        "error_message": turn.error_message,
                        "metrics": turn.metrics,
                    }
                    client.table("execution_turns").insert(turn_record).execute()
                    results["turns_created"] += 1
                except Exception as e:
                    results["errors"].append(f"Turn {turn.turn_number}: {str(e)}")

        # Create tool calls
        if batch_data.tool_calls:
            for tool_call in batch_data.tool_calls:
                try:
                    tool_output = tool_call.tool_output
                    tool_output_size = len(tool_output) if tool_output else 0
                    if tool_output and len(tool_output) > 10000:
                        tool_output = tool_output[:10000] + "... [truncated]"

                    tool_call_record = {
                        "id": str(uuid_lib.uuid4()),
                        "organization_id": organization["id"],
                        "execution_id": batch_data.execution_id,
                        "turn_id": tool_call.turn_id,
                        "tool_name": tool_call.tool_name,
                        "tool_use_id": tool_call.tool_use_id,
                        "started_at": tool_call.started_at,
                        "completed_at": tool_call.completed_at,
                        "duration_ms": tool_call.duration_ms,
                        "tool_input": tool_call.tool_input,
                        "tool_output": tool_output,
                        "tool_output_size": tool_output_size,
                        "success": tool_call.success,
                        "error_message": tool_call.error_message,
                        "error_type": tool_call.error_type,
                        "custom_metadata": tool_call.metadata,
                    }
                    client.table("execution_tool_calls").insert(tool_call_record).execute()
                    results["tool_calls_created"] += 1
                except Exception as e:
                    results["errors"].append(f"Tool call {tool_call.tool_name}: {str(e)}")

        # Create tasks
        if batch_data.tasks:
            for task in batch_data.tasks:
                try:
                    task_record = {
                        "id": str(uuid_lib.uuid4()),
                        "organization_id": organization["id"],
                        "execution_id": batch_data.execution_id,
                        "task_number": task.task_number,
                        "task_id": task.task_id,
                        "task_description": task.task_description,
                        "task_type": task.task_type,
                        "status": task.status,
                        "started_at": task.started_at,
                        "completed_at": task.completed_at,
                        "duration_ms": task.duration_ms,
                        "result": task.result,
                        "error_message": task.error_message,
                        "custom_metadata": task.metadata,
                    }
                    client.table("execution_tasks").insert(task_record).execute()
                    results["tasks_created"] += 1
                except Exception as e:
                    results["errors"].append(f"Task {task.task_description[:50]}: {str(e)}")

        logger.info(
            "batch_analytics_created",
            execution_id=batch_data.execution_id,
            turns_created=results["turns_created"],
            tool_calls_created=results["tool_calls_created"],
            tasks_created=results["tasks_created"],
            errors=len(results["errors"]),
            org_id=organization["id"]
        )

        return {
            "success": len(results["errors"]) == 0,
            "execution_id": batch_data.execution_id,
            **results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("batch_analytics_create_failed", error=str(e), execution_id=batch_data.execution_id)
        raise HTTPException(status_code=500, detail=f"Failed to create batch analytics: {str(e)}")


@router.patch("/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Update a task's status and completion information.

    This endpoint is called by workers to update task progress.
    """
    try:
        client = get_supabase()

        update_data = {}
        if task_update.status is not None:
            update_data["status"] = task_update.status
        if task_update.completed_at is not None:
            update_data["completed_at"] = task_update.completed_at
        if task_update.duration_ms is not None:
            update_data["duration_ms"] = task_update.duration_ms
        if task_update.result is not None:
            update_data["result"] = task_update.result
        if task_update.error_message is not None:
            update_data["error_message"] = task_update.error_message

        update_data["updated_at"] = datetime.utcnow().isoformat()

        result = client.table("execution_tasks").update(update_data).eq("id", task_id).eq("organization_id", organization["id"]).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Task not found")

        logger.info(
            "task_updated",
            task_id=task_id,
            status=task_update.status,
            org_id=organization["id"]
        )

        return {"success": True, "task_id": task_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("task_update_failed", error=str(e), task_id=task_id)
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")


# ============================================================================
# Reporting Endpoints (For Analytics Dashboard)
# ============================================================================

@router.get("/executions/{execution_id}/details")
async def get_execution_analytics(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Get comprehensive analytics for a specific execution.

    Returns:
    - Execution summary
    - Per-turn metrics
    - Tool call details
    - Task breakdown
    - Total costs and token usage
    """
    try:
        client = get_supabase()

        # Get execution
        exec_result = client.table("executions").select("*").eq("id", execution_id).eq("organization_id", organization["id"]).single().execute()
        if not exec_result.data:
            raise HTTPException(status_code=404, detail="Execution not found")

        execution = exec_result.data

        # Get turns
        turns_result = client.table("execution_turns").select("*").eq("execution_id", execution_id).eq("organization_id", organization["id"]).order("turn_number").execute()
        turns = turns_result.data if turns_result.data else []

        # Get tool calls
        tool_calls_result = client.table("execution_tool_calls").select("*").eq("execution_id", execution_id).eq("organization_id", organization["id"]).order("started_at").execute()
        tool_calls = tool_calls_result.data if tool_calls_result.data else []

        # Get tasks
        tasks_result = client.table("execution_tasks").select("*").eq("execution_id", execution_id).eq("organization_id", organization["id"]).order("task_number").execute()
        tasks = tasks_result.data if tasks_result.data else []

        # Calculate aggregated metrics
        total_turns = len(turns)
        total_tokens = sum(turn.get("total_tokens", 0) for turn in turns)
        total_cost = sum(turn.get("total_cost", 0.0) for turn in turns)
        total_duration_ms = sum(turn.get("duration_ms", 0) or 0 for turn in turns)

        total_tool_calls = len(tool_calls)
        successful_tool_calls = sum(1 for tc in tool_calls if tc.get("success", False))
        failed_tool_calls = total_tool_calls - successful_tool_calls

        unique_tools_used = list(set(tc.get("tool_name") for tc in tool_calls))

        # Task statistics
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task.get("status") == "completed")
        failed_tasks = sum(1 for task in tasks if task.get("status") == "failed")
        pending_tasks = sum(1 for task in tasks if task.get("status") in ["pending", "in_progress"])

        return {
            "execution": execution,
            "summary": {
                "execution_id": execution_id,
                "total_turns": total_turns,
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "total_duration_ms": total_duration_ms,
                "total_tool_calls": total_tool_calls,
                "successful_tool_calls": successful_tool_calls,
                "failed_tool_calls": failed_tool_calls,
                "unique_tools_used": unique_tools_used,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "pending_tasks": pending_tasks,
            },
            "turns": turns,
            "tool_calls": tool_calls,
            "tasks": tasks,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_execution_analytics_failed", error=str(e), execution_id=execution_id)
        raise HTTPException(status_code=500, detail=f"Failed to get execution analytics: {str(e)}")


@router.get("/summary")
async def get_organization_analytics_summary(
    request: Request,
    organization: dict = Depends(get_current_organization),
    days: int = Query(default=30, ge=1, le=365, description="Number of days to include in the summary"),
):
    """
    Get aggregated analytics summary for the organization.

    Returns high-level metrics over the specified time period:
    - Total executions
    - Total cost
    - Total tokens used
    - Model usage breakdown
    - Tool usage statistics
    - Success rates
    """
    try:
        client = get_supabase()

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        start_date_iso = start_date.isoformat()

        # Get executions in date range
        executions_result = client.table("executions").select("id, status, created_at").eq("organization_id", organization["id"]).gte("created_at", start_date_iso).execute()
        executions = executions_result.data if executions_result.data else []
        execution_ids = [exec["id"] for exec in executions]

        if not execution_ids:
            return {
                "period_days": days,
                "start_date": start_date_iso,
                "end_date": end_date.isoformat(),
                "total_executions": 0,
                "total_cost": 0.0,
                "total_tokens": 0,
                "total_turns": 0,
                "total_tool_calls": 0,
                "models_used": {},
                "tools_used": {},
                "success_rate": 0.0,
            }

        # Get all turns for these executions
        turns_result = client.table("execution_turns").select("*").eq("organization_id", organization["id"]).gte("created_at", start_date_iso).execute()
        turns = turns_result.data if turns_result.data else []

        # Get all tool calls for these executions
        tool_calls_result = client.table("execution_tool_calls").select("tool_name, success, duration_ms").eq("organization_id", organization["id"]).gte("created_at", start_date_iso).execute()
        tool_calls = tool_calls_result.data if tool_calls_result.data else []

        # Calculate aggregates
        total_executions = len(executions)
        successful_executions = sum(1 for exec in executions if exec.get("status") == "completed")
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0.0

        total_turns = len(turns)
        total_tokens = sum(turn.get("total_tokens", 0) for turn in turns)
        total_cost = sum(turn.get("total_cost", 0.0) for turn in turns)

        # Model usage breakdown
        models_used = {}
        for turn in turns:
            model = turn.get("model", "unknown")
            if model not in models_used:
                models_used[model] = {
                    "count": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                }
            models_used[model]["count"] += 1
            models_used[model]["total_tokens"] += turn.get("total_tokens", 0)
            models_used[model]["total_cost"] += turn.get("total_cost", 0.0)

        # Tool usage breakdown
        tools_used = {}
        total_tool_calls = len(tool_calls)
        for tool_call in tool_calls:
            tool_name = tool_call.get("tool_name", "unknown")
            if tool_name not in tools_used:
                tools_used[tool_name] = {
                    "count": 0,
                    "success_count": 0,
                    "fail_count": 0,
                    "avg_duration_ms": 0,
                    "total_duration_ms": 0,
                }
            tools_used[tool_name]["count"] += 1
            if tool_call.get("success", False):
                tools_used[tool_name]["success_count"] += 1
            else:
                tools_used[tool_name]["fail_count"] += 1

            duration = tool_call.get("duration_ms", 0) or 0
            tools_used[tool_name]["total_duration_ms"] += duration

        # Calculate average durations
        for tool_name, stats in tools_used.items():
            if stats["count"] > 0:
                stats["avg_duration_ms"] = stats["total_duration_ms"] / stats["count"]

        return {
            "period_days": days,
            "start_date": start_date_iso,
            "end_date": end_date.isoformat(),
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": total_executions - successful_executions,
            "success_rate": round(success_rate, 2),
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "total_turns": total_turns,
            "total_tool_calls": total_tool_calls,
            "models_used": models_used,
            "tools_used": tools_used,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_analytics_summary_failed", error=str(e), org_id=organization["id"])
        raise HTTPException(status_code=500, detail=f"Failed to get analytics summary: {str(e)}")


@router.get("/costs")
async def get_cost_breakdown(
    request: Request,
    organization: dict = Depends(get_current_organization),
    days: int = Query(default=30, ge=1, le=365, description="Number of days to include"),
    group_by: str = Query(default="day", regex="^(day|week|month)$", description="Group costs by time period"),
):
    """
    Get detailed cost breakdown over time.

    Returns cost metrics grouped by the specified time period.
    """
    try:
        client = get_supabase()

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        start_date_iso = start_date.isoformat()

        # Get all turns in date range
        turns_result = client.table("execution_turns").select("created_at, model, total_cost, total_tokens, input_tokens, output_tokens").eq("organization_id", organization["id"]).gte("created_at", start_date_iso).order("created_at").execute()
        turns = turns_result.data if turns_result.data else []

        # Group by time period
        cost_by_period = {}
        for turn in turns:
            created_at = datetime.fromisoformat(turn["created_at"].replace("Z", "+00:00"))

            # Determine period key
            if group_by == "day":
                period_key = created_at.strftime("%Y-%m-%d")
            elif group_by == "week":
                period_key = created_at.strftime("%Y-W%U")
            else:  # month
                period_key = created_at.strftime("%Y-%m")

            if period_key not in cost_by_period:
                cost_by_period[period_key] = {
                    "period": period_key,
                    "total_cost": 0.0,
                    "total_tokens": 0,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "turn_count": 0,
                    "models": {},
                }

            cost_by_period[period_key]["total_cost"] += turn.get("total_cost", 0.0)
            cost_by_period[period_key]["total_tokens"] += turn.get("total_tokens", 0)
            cost_by_period[period_key]["total_input_tokens"] += turn.get("input_tokens", 0)
            cost_by_period[period_key]["total_output_tokens"] += turn.get("output_tokens", 0)
            cost_by_period[period_key]["turn_count"] += 1

            # Track by model
            model = turn.get("model", "unknown")
            if model not in cost_by_period[period_key]["models"]:
                cost_by_period[period_key]["models"][model] = {
                    "cost": 0.0,
                    "tokens": 0,
                    "turns": 0,
                }
            cost_by_period[period_key]["models"][model]["cost"] += turn.get("total_cost", 0.0)
            cost_by_period[period_key]["models"][model]["tokens"] += turn.get("total_tokens", 0)
            cost_by_period[period_key]["models"][model]["turns"] += 1

        # Convert to list and sort
        cost_breakdown = sorted(cost_by_period.values(), key=lambda x: x["period"])

        # Calculate totals
        total_cost = sum(period["total_cost"] for period in cost_breakdown)
        total_tokens = sum(period["total_tokens"] for period in cost_breakdown)

        return {
            "period_days": days,
            "group_by": group_by,
            "start_date": start_date_iso,
            "end_date": end_date.isoformat(),
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "breakdown": cost_breakdown,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_cost_breakdown_failed", error=str(e), org_id=organization["id"])
        raise HTTPException(status_code=500, detail=f"Failed to get cost breakdown: {str(e)}")


@router.get("/aem/summary")
async def get_aem_summary(
    request: Request,
    organization: dict = Depends(get_current_organization),
    days: int = Query(default=30, ge=1, le=365, description="Number of days to include"),
):
    """
    Get Agentic Engineering Minutes (AEM) summary.

    Returns:
    - Total AEM consumed
    - Total AEM cost
    - Breakdown by model tier (Opus, Sonnet, Haiku)
    - Average runtime, model weight, tool complexity
    """
    try:
        client = get_supabase()

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        start_date_iso = start_date.isoformat()

        # Get all turns with AEM data
        turns_result = client.table("execution_turns").select(
            "runtime_minutes, model_weight, tool_calls_weight, aem_value, aem_cost, model, model_provider"
        ).eq("organization_id", organization["id"]).gte("created_at", start_date_iso).execute()
        turns = turns_result.data if turns_result.data else []

        if not turns:
            return {
                "period_days": days,
                "total_aem": 0.0,
                "total_aem_cost": 0.0,
                "total_runtime_minutes": 0.0,
                "turn_count": 0,
                "by_model_tier": {},
                "average_model_weight": 0.0,
                "average_tool_complexity": 0.0,
            }

        # Calculate totals
        total_aem = sum(turn.get("aem_value", 0.0) for turn in turns)
        total_aem_cost = sum(turn.get("aem_cost", 0.0) for turn in turns)
        total_runtime_minutes = sum(turn.get("runtime_minutes", 0.0) for turn in turns)
        total_model_weight = sum(turn.get("model_weight", 1.0) for turn in turns)
        total_tool_weight = sum(turn.get("tool_calls_weight", 1.0) for turn in turns)

        # Breakdown by model tier
        by_tier = {}
        for turn in turns:
            weight = turn.get("model_weight", 1.0)

            # Classify into tiers
            if weight >= 1.5:
                tier = "opus"
            elif weight >= 0.8:
                tier = "sonnet"
            else:
                tier = "haiku"

            if tier not in by_tier:
                by_tier[tier] = {
                    "tier": tier,
                    "turn_count": 0,
                    "total_aem": 0.0,
                    "total_aem_cost": 0.0,
                    "total_runtime_minutes": 0.0,
                    "models": set(),
                }

            by_tier[tier]["turn_count"] += 1
            by_tier[tier]["total_aem"] += turn.get("aem_value", 0.0)
            by_tier[tier]["total_aem_cost"] += turn.get("aem_cost", 0.0)
            by_tier[tier]["total_runtime_minutes"] += turn.get("runtime_minutes", 0.0)
            by_tier[tier]["models"].add(turn.get("model", "unknown"))

        # Convert sets to lists for JSON serialization
        for tier_data in by_tier.values():
            tier_data["models"] = list(tier_data["models"])

        return {
            "period_days": days,
            "start_date": start_date_iso,
            "end_date": end_date.isoformat(),
            "total_aem": round(total_aem, 2),
            "total_aem_cost": round(total_aem_cost, 2),
            "total_runtime_minutes": round(total_runtime_minutes, 2),
            "turn_count": len(turns),
            "average_aem_per_turn": round(total_aem / len(turns), 2) if turns else 0.0,
            "average_model_weight": round(total_model_weight / len(turns), 2) if turns else 0.0,
            "average_tool_complexity": round(total_tool_weight / len(turns), 2) if turns else 0.0,
            "by_model_tier": by_tier,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_aem_summary_failed", error=str(e), org_id=organization["id"])
        raise HTTPException(status_code=500, detail=f"Failed to get AEM summary: {str(e)}")


@router.get("/aem/trends")
async def get_aem_trends(
    request: Request,
    organization: dict = Depends(get_current_organization),
    days: int = Query(default=30, ge=1, le=365, description="Number of days to include"),
    group_by: str = Query(default="day", regex="^(day|week|month)$", description="Group by time period"),
):
    """
    Get AEM trends over time.

    Returns AEM consumption grouped by time period for trend analysis.
    """
    try:
        client = get_supabase()

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        start_date_iso = start_date.isoformat()

        # Get all turns with AEM data
        turns_result = client.table("execution_turns").select(
            "created_at, runtime_minutes, model_weight, tool_calls_weight, aem_value, aem_cost, model"
        ).eq("organization_id", organization["id"]).gte("created_at", start_date_iso).order("created_at").execute()
        turns = turns_result.data if turns_result.data else []

        # Group by time period
        aem_by_period = {}
        for turn in turns:
            created_at = datetime.fromisoformat(turn["created_at"].replace("Z", "+00:00"))

            # Determine period key
            if group_by == "day":
                period_key = created_at.strftime("%Y-%m-%d")
            elif group_by == "week":
                period_key = created_at.strftime("%Y-W%U")
            else:  # month
                period_key = created_at.strftime("%Y-%m")

            if period_key not in aem_by_period:
                aem_by_period[period_key] = {
                    "period": period_key,
                    "total_aem": 0.0,
                    "total_aem_cost": 0.0,
                    "total_runtime_minutes": 0.0,
                    "turn_count": 0,
                    "average_model_weight": 0.0,
                    "average_tool_complexity": 0.0,
                }

            aem_by_period[period_key]["total_aem"] += turn.get("aem_value", 0.0)
            aem_by_period[period_key]["total_aem_cost"] += turn.get("aem_cost", 0.0)
            aem_by_period[period_key]["total_runtime_minutes"] += turn.get("runtime_minutes", 0.0)
            aem_by_period[period_key]["turn_count"] += 1

        # Calculate averages
        for period_data in aem_by_period.values():
            if period_data["turn_count"] > 0:
                # Get turns for this period to calculate weighted averages
                period_turns = [t for t in turns if datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")).strftime(
                    "%Y-%m-%d" if group_by == "day" else "%Y-W%U" if group_by == "week" else "%Y-%m"
                ) == period_data["period"]]

                total_weight = sum(t.get("model_weight", 1.0) for t in period_turns)
                total_tool_weight = sum(t.get("tool_calls_weight", 1.0) for t in period_turns)

                period_data["average_model_weight"] = round(total_weight / len(period_turns), 2)
                period_data["average_tool_complexity"] = round(total_tool_weight / len(period_turns), 2)

        # Convert to list and sort
        aem_trends = sorted(aem_by_period.values(), key=lambda x: x["period"])

        # Calculate totals
        total_aem = sum(period["total_aem"] for period in aem_trends)
        total_aem_cost = sum(period["total_aem_cost"] for period in aem_trends)

        return {
            "period_days": days,
            "group_by": group_by,
            "start_date": start_date_iso,
            "end_date": end_date.isoformat(),
            "total_aem": round(total_aem, 2),
            "total_aem_cost": round(total_aem_cost, 2),
            "trends": aem_trends,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_aem_trends_failed", error=str(e), org_id=organization["id"])
        raise HTTPException(status_code=500, detail=f"Failed to get AEM trends: {str(e)}")
