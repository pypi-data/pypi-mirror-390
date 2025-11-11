"""
Team executor service with runtime abstraction support.

This version supports both Agno-based teams and Claude Code SDK runtime teams.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import structlog
import asyncio
import os

from control_plane_api.worker.control_plane_client import ControlPlaneClient
from control_plane_api.worker.services.session_service import SessionService
from control_plane_api.worker.services.cancellation_manager import CancellationManager
from runtimes import (
    RuntimeFactory,
    RuntimeType,
    RuntimeExecutionContext,
)
from control_plane_api.worker.utils.streaming_utils import StreamingHelper

logger = structlog.get_logger()


class TeamExecutorServiceV2:
    """
    Service for executing teams using runtime abstraction.

    This service orchestrates team execution by:
    1. Loading session history
    2. Determining runtime type (Agno or Claude Code)
    3. Delegating execution to appropriate runtime
    4. Persisting session after execution

    For Claude Code runtime:
    - Team leader uses Claude Code SDK with Task tool
    - Team members are executed as subagents via Task tool
    - Streaming and tool hooks supported

    For Agno runtime:
    - Uses existing Agno Team implementation
    - Full multi-agent coordination support
    """

    def __init__(
        self,
        control_plane: ControlPlaneClient,
        session_service: SessionService,
        cancellation_manager: CancellationManager,
    ):
        """
        Initialize the team executor service.

        Args:
            control_plane: Control Plane API client
            session_service: Session management service
            cancellation_manager: Execution cancellation manager
        """
        self.control_plane = control_plane
        self.session_service = session_service
        self.cancellation_manager = cancellation_manager
        self.runtime_factory = RuntimeFactory()

    async def execute(self, input: Any) -> Dict[str, Any]:
        """
        Execute a team using the configured runtime.

        Args:
            input: TeamExecutionInput with execution details

        Returns:
            Dict with response, usage, success flag, runtime_type, etc.
        """
        execution_id = input.execution_id

        print("\n" + "=" * 80)
        print("🚀 TEAM EXECUTION START (Runtime-Abstracted)")
        print("=" * 80)
        print(f"Execution ID: {execution_id}")
        print(f"Team ID: {input.team_id}")
        print(f"Organization: {input.organization_id}")
        print(f"Agent Count: {len(input.agents)}")
        print(f"Session ID: {input.session_id}")
        print(f"Prompt: {input.prompt[:100]}..." if len(input.prompt) > 100 else f"Prompt: {input.prompt}")
        print("=" * 80 + "\n")

        logger.info(
            "team_execution_start",
            execution_id=execution_id[:8],
            team_id=input.team_id,
            session_id=input.session_id,
            agent_count=len(input.agents)
        )

        try:
            # STEP 1: Load session history
            print("📚 Loading session history...")
            session_history = self.session_service.load_session(
                execution_id=execution_id,
                session_id=input.session_id
            )

            if session_history:
                print(f"✅ Loaded {len(session_history)} messages from previous session\n")
            else:
                print("ℹ️  Starting new conversation\n")

            # STEP 2: Determine runtime type from team configuration
            team_config = getattr(input, "team_config", {}) or {}
            runtime_type_str = team_config.get("runtime", "default")
            runtime_type = self.runtime_factory.parse_runtime_type(runtime_type_str)

            print(f"🔌 Runtime Type: {runtime_type.value}")
            print(f"   Framework: {self._get_framework_name(runtime_type)}\n")

            logger.info(
                "runtime_selected",
                execution_id=execution_id[:8],
                runtime=runtime_type.value,
            )

            # STEP 3: Execute based on runtime type
            if runtime_type == RuntimeType.CLAUDE_CODE:
                result = await self._execute_with_claude_code(input, session_history)
            else:
                # Fall back to Agno-based team execution
                from control_plane_api.worker.services.team_executor import TeamExecutorService

                agno_executor = TeamExecutorService(
                    self.control_plane,
                    self.session_service,
                    self.cancellation_manager
                )
                return await agno_executor.execute(input)

            print("\n✅ Team execution completed!")
            print(f"   Response Length: {len(result['response'])} chars")
            print(f"   Success: {result['success']}\n")

            logger.info(
                "team_execution_completed",
                execution_id=execution_id[:8],
                success=result["success"],
                response_length=len(result["response"]),
            )

            # STEP 4: Persist session
            if result["success"] and result["response"]:
                print("💾 Persisting session history...")

                # Build new messages
                new_messages = [
                    {"role": "user", "content": input.prompt},
                    {"role": "assistant", "content": result["response"]},
                ]

                # Combine with previous history
                complete_session = session_history + new_messages

                success = self.session_service.persist_session(
                    execution_id=execution_id,
                    session_id=input.session_id or execution_id,
                    user_id=input.user_id,
                    messages=complete_session,
                    metadata={
                        "team_id": input.team_id,
                        "organization_id": input.organization_id,
                        "runtime_type": runtime_type.value,
                        "turn_count": len(complete_session),
                        "member_count": len(input.agents),
                    },
                )

                if success:
                    print(f"✅ Session persisted ({len(complete_session)} total messages)\n")
                else:
                    print(f"⚠️  Session persistence failed\n")

            # STEP 5: Print usage metrics
            if result.get("usage"):
                print(f"📊 Token Usage:")
                print(f"   Input: {result['usage'].get('prompt_tokens', 0)}")
                print(f"   Output: {result['usage'].get('completion_tokens', 0)}")
                print(f"   Total: {result['usage'].get('total_tokens', 0)}\n")

            print("=" * 80)
            print("🏁 TEAM EXECUTION END")
            print("=" * 80 + "\n")

            return result

        except Exception as e:
            print("\n" + "=" * 80)
            print("❌ TEAM EXECUTION FAILED")
            print("=" * 80)
            print(f"Error: {str(e)}")
            print("=" * 80 + "\n")

            logger.error(
                "team_execution_failed",
                execution_id=execution_id[:8],
                error=str(e)
            )

            return {
                "success": False,
                "error": str(e),
                "model": input.model_id,
                "usage": {},
                "finish_reason": "error",
                "runtime_type": runtime_type_str if "runtime_type_str" in locals() else "unknown",
            }

    async def _execute_with_claude_code(
        self, input: Any, session_history: List[Dict]
    ) -> Dict[str, Any]:
        """
        Execute team using Claude Code SDK.

        Strategy:
        - Team leader is a Claude Code agent with Task tool enabled
        - Team members are defined as context for the leader
        - Leader uses Task tool to delegate work to members
        - Streaming and hooks provide real-time feedback

        Args:
            input: TeamExecutionInput
            session_history: Previous conversation messages

        Returns:
            Result dict
        """
        execution_id = input.execution_id

        print(f"⚙️  Creating Claude Code team leader...")

        # Create runtime instance
        runtime = self.runtime_factory.create_runtime(
            runtime_type=RuntimeType.CLAUDE_CODE,
            control_plane_client=self.control_plane,
            cancellation_manager=self.cancellation_manager,
        )

        print(f"✅ Runtime created: {runtime.get_runtime_info()}\n")

        # STEP 1: Build team context for system prompt
        team_context = self._build_team_context(input.agents)

        system_prompt = f"""You are the team leader coordinating a team of specialized AI agents.

Your team members:
{team_context}

When you need a team member to perform a task:
1. Use the Task tool to delegate work to the appropriate agent
2. Provide clear instructions in the subagent_type parameter
3. Wait for their response before continuing
4. Synthesize the results into a cohesive answer

Your goal is to coordinate the team effectively to solve the user's request.
"""

        print(f"📋 Team Context:")
        print(f"   Team Members: {len(input.agents)}")
        for agent in input.agents:
            print(f"   - {agent.get('name')}: {agent.get('role', 'No role specified')[:60]}...")
        print()

        # STEP 2: Get skills for team leader (must include Task tool)
        print(f"🔧 Fetching skills from Control Plane...")
        skills = []
        try:
            # Get skills from first agent (team leader)
            if input.agents:
                leader_id = input.agents[0].get("id")
                if leader_id:
                    skill_configs = self.control_plane.get_skills(leader_id)
                    if skill_configs:
                        print(f"✅ Resolved {len(skill_configs)} skills")

                        from services.skill_factory import SkillFactory
                        skills = SkillFactory.create_skills_from_list(skill_configs)

                        if skills:
                            print(f"✅ Instantiated {len(skills)} skill(s)")
        except Exception as e:
            print(f"⚠️  Error fetching skills: {str(e)}")
            logger.error("skill_fetch_error", error=str(e))

        # Always ensure Task tool is available for delegation
        task_skill = {"type": "task", "name": "Task"}
        if task_skill not in skills:
            skills.append(task_skill)
            print(f"✅ Added Task tool for team coordination\n")

        # STEP 3: Build execution context
        print("📦 Building execution context...")
        team_config = getattr(input, "team_config", {}) or {}
        context = RuntimeExecutionContext(
            execution_id=execution_id,
            agent_id=input.team_id,  # Use team_id as agent_id
            organization_id=input.organization_id,
            prompt=input.prompt,
            system_prompt=system_prompt,
            conversation_history=session_history,
            model_id=input.model_id,
            model_config=getattr(input, "model_config", None),
            agent_config=team_config,
            skills=skills,
            mcp_servers=getattr(input, "mcp_servers", None),
            user_metadata=getattr(input, "user_metadata", None),
            runtime_config=team_config.get("runtime_config"),
        )
        print("✅ Context ready\n")

        # STEP 4: Execute via runtime with streaming
        print("⚡ Executing team via Claude Code runtime...\n")

        if runtime.supports_streaming():
            result = await self._execute_streaming(runtime, context, input)
        else:
            exec_result = await runtime.execute(context)
            result = {
                "success": exec_result.success,
                "response": exec_result.response,
                "usage": exec_result.usage,
                "model": exec_result.model or input.model_id,
                "finish_reason": exec_result.finish_reason or "stop",
                "tool_messages": exec_result.tool_messages or [],
                "runtime_type": "claude_code",
                "error": exec_result.error,
                "team_member_count": len(input.agents),
            }

        return result

    async def _execute_streaming(
        self, runtime, context: RuntimeExecutionContext, input: Any
    ) -> Dict[str, Any]:
        """
        Execute with streaming and publish events to Control Plane.

        Args:
            runtime: Runtime instance
            context: Execution context
            input: Original input for additional metadata

        Returns:
            Result dict
        """
        # Create streaming helper for publishing events
        streaming_helper = StreamingHelper(
            control_plane_client=self.control_plane,
            execution_id=context.execution_id
        )

        accumulated_response = ""
        final_result = None

        # Define event callback for publishing to Control Plane
        def event_callback(event: Dict):
            """Callback to publish events to Control Plane SSE"""
            event_type = event.get("type")

            if event_type == "content_chunk":
                # Publish content chunk
                streaming_helper.publish_content_chunk(
                    content=event.get("content", ""),
                    message_id=event.get("message_id", context.execution_id),
                )
            elif event_type == "tool_start":
                # Publish tool start
                streaming_helper.publish_tool_start(
                    tool_name=event.get("tool_name"),
                    tool_execution_id=event.get("tool_execution_id"),
                    tool_args=event.get("tool_args", {}),
                    source="team_leader",
                )
            elif event_type == "tool_complete":
                # Publish tool completion
                streaming_helper.publish_tool_complete(
                    tool_name=event.get("tool_name"),
                    tool_execution_id=event.get("tool_execution_id"),
                    status=event.get("status", "success"),
                    output=event.get("output"),
                    error=event.get("error"),
                    source="team_leader",
                )

        # Stream execution
        async for chunk in runtime.stream_execute(context, event_callback):
            if chunk.response:
                accumulated_response += chunk.response
                print(chunk.response, end="", flush=True)

            # Keep final result for metadata
            if chunk.usage or chunk.finish_reason:
                final_result = chunk

        print()  # New line after streaming

        # Return final result with accumulated response
        if final_result:
            return {
                "success": final_result.success,
                "response": accumulated_response,
                "usage": final_result.usage,
                "model": final_result.model or input.model_id,
                "finish_reason": final_result.finish_reason or "stop",
                "tool_messages": final_result.tool_messages or [],
                "runtime_type": "claude_code",
                "error": final_result.error,
                "team_member_count": len(input.agents),
            }
        else:
            return {
                "success": True,
                "response": accumulated_response,
                "usage": {},
                "model": input.model_id,
                "finish_reason": "stop",
                "tool_messages": [],
                "runtime_type": "claude_code",
                "team_member_count": len(input.agents),
            }

    def _build_team_context(self, agents: List[Dict]) -> str:
        """
        Build team context description for system prompt.

        Args:
            agents: List of agent configurations

        Returns:
            Formatted team context string
        """
        context_lines = []
        for i, agent in enumerate(agents, 1):
            name = agent.get("name", f"Agent {i}")
            role = agent.get("role", "No role specified")
            agent_id = agent.get("id", "unknown")

            context_lines.append(
                f"{i}. **{name}** (ID: {agent_id})\n"
                f"   Role: {role}\n"
            )

        return "\n".join(context_lines)

    def _get_framework_name(self, runtime_type: RuntimeType) -> str:
        """
        Get friendly framework name for runtime type.

        Args:
            runtime_type: Runtime type enum

        Returns:
            Framework name string
        """
        mapping = {
            RuntimeType.DEFAULT: "Agno",
            RuntimeType.CLAUDE_CODE: "Claude Code SDK",
        }
        return mapping.get(runtime_type, "Unknown")
