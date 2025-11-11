"""Runtime-based execution activities for Temporal workflows.

This module provides activities that use the RuntimeFactory/RuntimeRegistry system
for agent execution, supporting multiple runtimes (Agno/Default, Claude Code, etc.)
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from temporalio import activity
import structlog
import os
import asyncio
import time

from control_plane_api.worker.runtimes.base import (
    RuntimeType,
    RuntimeExecutionContext,
    RuntimeExecutionResult,
)
from control_plane_api.worker.runtimes.factory import RuntimeFactory
from control_plane_api.worker.control_plane_client import get_control_plane_client
from control_plane_api.worker.services.cancellation_manager import CancellationManager
from control_plane_api.worker.services.runtime_analytics import submit_runtime_analytics
from control_plane_api.worker.services.analytics_service import AnalyticsService

logger = structlog.get_logger(__name__)


@dataclass
class ActivityRuntimeExecuteInput:
    """Input for runtime-based execution activity"""
    execution_id: str
    agent_id: str
    organization_id: str
    prompt: str
    runtime_type: str = "default"  # "default", "claude_code", etc.
    system_prompt: Optional[str] = None
    model_id: Optional[str] = None
    model_config: Optional[Dict[str, Any]] = None
    agent_config: Optional[Dict[str, Any]] = None
    skills: Optional[List[Dict[str, Any]]] = None
    mcp_servers: Optional[Dict[str, Any]] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None
    user_metadata: Optional[Dict[str, Any]] = None
    runtime_config: Optional[Dict[str, Any]] = None
    stream: bool = False

    def __post_init__(self):
        if self.model_config is None:
            self.model_config = {}
        if self.agent_config is None:
            self.agent_config = {}
        if self.skills is None:
            self.skills = []
        if self.mcp_servers is None:
            self.mcp_servers = {}
        if self.conversation_history is None:
            self.conversation_history = []
        if self.user_metadata is None:
            self.user_metadata = {}
        if self.runtime_config is None:
            self.runtime_config = {}


@activity.defn
async def execute_with_runtime(input: ActivityRuntimeExecuteInput) -> Dict[str, Any]:
    """
    Execute agent using the RuntimeFactory/RuntimeRegistry system.

    This activity:
    1. Creates a runtime based on runtime_type (default, claude_code, etc.)
    2. Builds execution context
    3. Executes (streaming or non-streaming)
    4. Returns results

    Args:
        input: Activity input with execution details and runtime_type

    Returns:
        Dict with response, usage, success flag, etc.
    """
    print("\n" + "="*80)
    print("🚀 RUNTIME-BASED EXECUTION START")
    print("="*80)
    print(f"Execution ID: {input.execution_id}")
    print(f"Agent ID: {input.agent_id}")
    print(f"Organization: {input.organization_id}")
    print(f"Runtime Type: {input.runtime_type}")
    print(f"Model: {input.model_id or 'default'}")
    print(f"Stream: {input.stream}")
    print(f"Skills: {len(input.skills)}")
    print(f"MCP Servers: {len(input.mcp_servers)}")
    print(f"Prompt: {input.prompt[:100]}..." if len(input.prompt) > 100 else f"Prompt: {input.prompt}")
    print("="*80 + "\n")

    activity.logger.info(
        "Executing with Runtime system",
        extra={
            "execution_id": input.execution_id,
            "agent_id": input.agent_id,
            "organization_id": input.organization_id,
            "runtime_type": input.runtime_type,
            "model_id": input.model_id,
            "stream": input.stream,
        }
    )

    try:
        # Track execution start time for analytics
        turn_start_time = time.time()

        # Get Control Plane client and cancellation manager
        control_plane = get_control_plane_client()
        cancellation_manager = CancellationManager()

        # Initialize analytics service for submission
        analytics_service = AnalyticsService(
            control_plane_url=control_plane.base_url if hasattr(control_plane, 'base_url') else "http://localhost:8000",
            api_key=os.environ.get("KUBIYA_API_KEY", ""),
        )

        # Parse runtime type
        try:
            runtime_type_enum = RuntimeType(input.runtime_type)
        except ValueError:
            logger.error(f"Invalid runtime_type: {input.runtime_type}, falling back to DEFAULT")
            runtime_type_enum = RuntimeType.DEFAULT

        # Create runtime using factory
        factory = RuntimeFactory()
        runtime = factory.create_runtime(
            runtime_type=runtime_type_enum,
            control_plane_client=control_plane,
            cancellation_manager=cancellation_manager,
        )

        logger.info(
            f"Created runtime",
            extra={
                "runtime_type": runtime_type_enum,
                "runtime_class": runtime.__class__.__name__,
                "capabilities": runtime.get_capabilities(),
            }
        )

        # Fetch and instantiate skills if runtime supports tools
        skills = input.skills or []
        if runtime.supports_tools():
            print(f"🔧 Fetching skills from Control Plane...")
            try:
                skill_configs = control_plane.get_skills(input.agent_id)
                if skill_configs:
                    print(f"✅ Resolved {len(skill_configs)} skill configs")
                    print(f"   Types: {[t.get('type') for t in skill_configs]}")
                    print(f"   Names: {[t.get('name') for t in skill_configs]}")
                    print(f"   Enabled: {[t.get('enabled', True) for t in skill_configs]}\n")

                    # DEBUG: Show full config for workflow_executor skills
                    for cfg in skill_configs:
                        if cfg.get('type') in ['workflow_executor', 'workflow']:
                            print(f"🔍 Workflow Executor Skill Config:")
                            print(f"   Name: {cfg.get('name')}")
                            print(f"   Type: {cfg.get('type')}")
                            print(f"   Enabled: {cfg.get('enabled', True)}")
                            print(f"   Config Keys: {list(cfg.get('configuration', {}).keys())}\n")

                    # Import here to avoid circular dependency
                    from worker.services.skill_factory import SkillFactory

                    skills = SkillFactory.create_skills_from_list(skill_configs)

                    if skills:
                        print(f"✅ Instantiated {len(skills)} skill(s)")
                        # Show types of instantiated skills
                        skill_types = [type(s).__name__ for s in skills]
                        print(f"   Skill classes: {skill_types}\n")
                    else:
                        print(f"⚠️  No skills were instantiated (all disabled or failed)\n")
                else:
                    print(f"⚠️  No skills found for agent\n")
            except Exception as e:
                print(f"❌ Error fetching skills: {str(e)}\n")
                logger.error("skill_fetch_error", error=str(e), exc_info=True)

        # Build execution context
        context = RuntimeExecutionContext(
            execution_id=input.execution_id,
            agent_id=input.agent_id,
            organization_id=input.organization_id,
            prompt=input.prompt,
            system_prompt=input.system_prompt,
            conversation_history=input.conversation_history,
            model_id=input.model_id,
            model_config=input.model_config,
            agent_config=input.agent_config,
            skills=skills,  # Use fetched skills
            mcp_servers=input.mcp_servers,
            user_metadata=input.user_metadata,
            runtime_config=input.runtime_config,
        )

        # Execute based on streaming preference
        if input.stream:
            # Streaming execution
            logger.info("Starting streaming execution")
            accumulated_response = ""
            final_result = None

            # Generate unique message ID for this turn (execution_id + timestamp)
            message_id = f"{input.execution_id}_{int(time.time() * 1000000)}"

            # Track tool events published
            tool_events_published = {"start": 0, "complete": 0}

            # Define event callback for publishing tool events to Control Plane
            def event_callback(event: Dict):
                """Callback to publish events (tool start/complete, content chunks) to Control Plane SSE"""
                event_type = event.get("type")

                if event_type == "content_chunk":
                    # Content chunks are already handled below via result.response
                    pass
                elif event_type == "tool_start":
                    # Publish tool start event (synchronous - this runs in async context via callback)
                    try:
                        print(f"\n🔧 TOOL START EVENT: {event.get('tool_name')} (ID: {event.get('tool_execution_id')})")
                        control_plane.publish_event(
                            execution_id=input.execution_id,
                            event_type="tool_started",  # Match default runtime event type
                            data={
                                "tool_name": event.get("tool_name"),
                                "tool_execution_id": event.get("tool_execution_id"),
                                "tool_arguments": event.get("tool_args", {}),
                                "message": f"🔧 Executing tool: {event.get('tool_name')}",
                                "source": "agent",
                            }
                        )
                        tool_events_published["start"] += 1
                        print(f"📡 Published tool_started event #{tool_events_published['start']}: {event.get('tool_name')}")
                    except Exception as e:
                        logger.error(f"❌ Failed to publish tool_start event: {e}", exc_info=True)
                        print(f"❌ Failed to publish tool_start event: {e}")
                elif event_type == "tool_complete":
                    # Publish tool complete event
                    try:
                        status = event.get("status", "success")
                        icon = "✅" if status == "success" else "❌"
                        print(f"\n{icon} TOOL COMPLETE EVENT: {event.get('tool_name')} ({status})")
                        control_plane.publish_event(
                            execution_id=input.execution_id,
                            event_type="tool_completed",  # Match default runtime event type
                            data={
                                "tool_name": event.get("tool_name"),
                                "tool_execution_id": event.get("tool_execution_id"),
                                "status": status,
                                "tool_output": event.get("output"),
                                "tool_error": event.get("error"),
                                "message": f"{icon} Tool {status}: {event.get('tool_name')}",
                                "source": "agent",
                            }
                        )
                        tool_events_published["complete"] += 1
                        print(f"📡 Published tool_completed event #{tool_events_published['complete']}: {event.get('tool_name')}\n")
                    except Exception as e:
                        logger.error(f"❌ Failed to publish tool_complete event: {e}", exc_info=True)
                        print(f"❌ Failed to publish tool_complete event: {e}")

            # Stream execution with event callback
            async for result in runtime.stream_execute(context, event_callback):
                if result.response:
                    accumulated_response += result.response

                    # Publish streaming chunk to control plane for real-time UI updates
                    try:
                        await control_plane.publish_event_async(
                            execution_id=input.execution_id,
                            event_type="message_chunk",
                            data={
                                "role": "assistant",
                                "content": result.response,
                                "is_chunk": True,
                                "message_id": message_id,
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Failed to publish streaming chunk: {e}")

                if result.finish_reason:
                    final_result = result
                    break

            if not final_result:
                raise RuntimeError("Streaming execution did not provide final result")

            # Log tool event summary
            print(f"\n📊 Tool Events Summary:")
            print(f"   tool_started events published: {tool_events_published['start']}")
            print(f"   tool_completed events published: {tool_events_published['complete']}")
            print(f"   tool_messages in result: {len(final_result.tool_messages or [])}\n")

            # Submit analytics (fire-and-forget)
            try:
                asyncio.create_task(
                    submit_runtime_analytics(
                        result=final_result,
                        execution_id=input.execution_id,
                        turn_number=1,  # TODO: Track turn number across conversation
                        turn_start_time=turn_start_time,
                        analytics_service=analytics_service,
                        turn_end_time=time.time(),
                    )
                )
                logger.info(
                    "analytics_submission_started",
                    execution_id=input.execution_id,
                    tokens=final_result.usage.get("total_tokens", 0) if final_result.usage else 0,
                )
            except Exception as e:
                logger.warning("analytics_submission_failed", error=str(e), execution_id=input.execution_id)

            return {
                "success": final_result.success,
                "response": accumulated_response,
                "usage": final_result.usage or {},
                "model": final_result.model,
                "finish_reason": final_result.finish_reason,
                "tool_messages": final_result.tool_messages or [],
                "metadata": final_result.metadata or {},
                "error": final_result.error,
            }

        else:
            # Non-streaming execution
            logger.info("Starting non-streaming execution")
            result = await runtime.execute(context)

            # Submit analytics (fire-and-forget)
            try:
                asyncio.create_task(
                    submit_runtime_analytics(
                        result=result,
                        execution_id=input.execution_id,
                        turn_number=1,  # TODO: Track turn number across conversation
                        turn_start_time=turn_start_time,
                        analytics_service=analytics_service,
                        turn_end_time=time.time(),
                    )
                )
                logger.info(
                    "analytics_submission_started",
                    execution_id=input.execution_id,
                    tokens=result.usage.get("total_tokens", 0) if result.usage else 0,
                )
            except Exception as e:
                logger.warning("analytics_submission_failed", error=str(e), execution_id=input.execution_id)

            return {
                "success": result.success,
                "response": result.response,
                "usage": result.usage or {},
                "model": result.model,
                "finish_reason": result.finish_reason,
                "tool_messages": result.tool_messages or [],
                "metadata": result.metadata or {},
                "error": result.error,
            }

    except Exception as e:
        logger.error(
            "Runtime execution failed",
            extra={
                "execution_id": input.execution_id,
                "runtime_type": input.runtime_type,
                "error": str(e),
            },
            exc_info=True,
        )

        return {
            "success": False,
            "response": "",
            "usage": {},
            "model": input.model_id,
            "finish_reason": "error",
            "tool_messages": [],
            "metadata": {},
            "error": f"{type(e).__name__}: {str(e)}",
        }
