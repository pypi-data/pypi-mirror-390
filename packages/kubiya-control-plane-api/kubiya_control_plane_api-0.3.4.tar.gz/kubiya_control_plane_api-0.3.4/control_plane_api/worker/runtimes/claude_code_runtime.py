"""
Claude Code runtime implementation using Claude Code SDK.

This runtime adapter integrates the Claude Code SDK to power agents with
advanced coding capabilities, file operations, and specialized tools.
"""

from typing import Dict, Any, Optional, AsyncIterator, Callable, TYPE_CHECKING, List
import structlog
import os
import asyncio
import time

from .base import (
    RuntimeType,
    RuntimeExecutionResult,
    RuntimeExecutionContext,
    RuntimeCapabilities,
    BaseRuntime,
    RuntimeRegistry,
)

if TYPE_CHECKING:
    from control_plane_client import ControlPlaneClient
    from services.cancellation_manager import CancellationManager

logger = structlog.get_logger(__name__)


@RuntimeRegistry.register(RuntimeType.CLAUDE_CODE)
class ClaudeCodeRuntime(BaseRuntime):
    """
    Runtime implementation using Claude Code SDK.

    This runtime leverages Claude Code's specialized capabilities for
    software engineering tasks, file operations, and developer workflows.

    Features:
    - Streaming execution with real-time updates
    - Conversation history support via ClaudeSDKClient
    - Custom tool integration via MCP
    - Hooks for tool execution monitoring
    - Cancellation support via interrupt()
    """

    def __init__(
        self,
        control_plane_client: "ControlPlaneClient",
        cancellation_manager: "CancellationManager",
        **kwargs,
    ):
        """
        Initialize the Claude Code runtime.

        Args:
            control_plane_client: Client for Control Plane API
            cancellation_manager: Manager for execution cancellation
            **kwargs: Additional configuration options
        """
        super().__init__(control_plane_client, cancellation_manager, **kwargs)

        # Track active SDK clients for cancellation
        self._active_clients: Dict[str, Any] = {}

    def get_runtime_type(self) -> RuntimeType:
        """Return RuntimeType.CLAUDE_CODE."""
        return RuntimeType.CLAUDE_CODE

    def get_capabilities(self) -> RuntimeCapabilities:
        """Return Claude Code runtime capabilities."""
        return RuntimeCapabilities(
            streaming=True,
            tools=True,
            mcp=True,
            hooks=True,
            cancellation=True,
            conversation_history=True,
            custom_tools=True
        )

    async def _execute_impl(
        self, context: RuntimeExecutionContext
    ) -> RuntimeExecutionResult:
        """
        Execute agent using Claude Code SDK (non-streaming).

        Production-grade implementation with:
        - Comprehensive error handling
        - Proper resource cleanup
        - Detailed logging
        - Timeout management
        - Graceful degradation

        Args:
            context: Execution context with prompt, history, config

        Returns:
            RuntimeExecutionResult with response and metadata
        """
        client = None
        start_time = asyncio.get_event_loop().time()

        try:
            from claude_agent_sdk import ClaudeSDKClient, ResultMessage

            self.logger.info(
                "Starting Claude Code non-streaming execution",
                execution_id=context.execution_id,
                model=context.model_id,
                has_history=bool(context.conversation_history),
            )

            # Build Claude Code options with validation
            options, _ = self._build_claude_options(context)  # active_tools not needed for non-streaming

            # Create client and manually manage lifecycle to avoid asyncio cancel scope issues
            client = ClaudeSDKClient(options=options)
            await client.connect()
            self._active_clients[context.execution_id] = client

            # Send prompt (SDK handles conversation history via session resume)
            # No need to manually inject history - the SDK maintains it via session_id
            prompt = context.prompt

            self.logger.debug(
                "Sending query to Claude Code SDK",
                execution_id=context.execution_id,
                prompt_length=len(prompt),
                using_session_resume=bool(options.resume),
            )

            await client.query(prompt)

            # Collect complete response
            response_text = ""
            usage = {}
            tool_messages = []
            finish_reason = None
            message_count = 0

            # Use receive_response() to get messages until ResultMessage
            async for message in client.receive_response():
                    message_count += 1

                    # Extract content from AssistantMessage
                    if hasattr(message, "content"):
                        for block in message.content:
                            if hasattr(block, "text"):
                                response_text += block.text
                            elif hasattr(block, "name"):  # ToolUseBlock
                                tool_messages.append(
                                    {
                                        "tool": block.name,
                                        "input": getattr(block, "input", {}),
                                        "tool_use_id": getattr(block, "id", None),
                                    }
                                )

                    # Extract usage, finish reason, and session_id from ResultMessage
                    if isinstance(message, ResultMessage):
                        if message.usage:
                            # Use Anthropic field names for consistency with analytics
                            usage = {
                                "input_tokens": getattr(message.usage, "input_tokens", 0),
                                "output_tokens": getattr(message.usage, "output_tokens", 0),
                                "total_tokens": getattr(message.usage, "input_tokens", 0) + getattr(message.usage, "output_tokens", 0),
                                "cache_read_tokens": getattr(message.usage, "cache_read_input_tokens", 0),
                                "cache_creation_tokens": getattr(message.usage, "cache_creation_input_tokens", 0),
                            }
                            self.logger.info(
                                "Claude Code usage extracted",
                                execution_id=context.execution_id[:8],
                                input_tokens=usage["input_tokens"],
                                output_tokens=usage["output_tokens"],
                                cache_read=usage["cache_read_tokens"],
                            )
                        else:
                            self.logger.warning(
                                "Claude Code ResultMessage has no usage",
                                execution_id=context.execution_id[:8],
                            )
                        finish_reason = message.subtype  # "success" or "error"

                        # Extract session_id for conversation continuity
                        # This will be passed back to enable multi-turn conversations
                        session_id = getattr(message, "session_id", None)
                        if session_id:
                            # Store in metadata to use on next turn
                            metadata["claude_code_session_id"] = session_id
                            self.logger.info(
                                "✅ Claude Code session captured for conversation continuity",
                                execution_id=context.execution_id[:8],
                                session_id=session_id[:16],
                                message="This session_id will enable multi-turn conversations"
                            )
                        else:
                            self.logger.warning(
                                "⚠️  No session_id in ResultMessage - multi-turn may not work",
                                execution_id=context.execution_id[:8],
                            )

                        self.logger.info(
                            "Claude Code execution completed",
                            execution_id=context.execution_id[:8],
                            finish_reason=finish_reason,
                            message_count=message_count,
                            response_length=len(response_text),
                            tool_count=len(tool_messages),
                            tokens=usage.get("total_tokens", 0),
                            has_session_id=bool(session_id),
                        )
                        break

            elapsed_time = asyncio.get_event_loop().time() - start_time

            # Merge accumulated metadata (including session_id) with execution stats
            final_metadata = {
                **metadata,  # Includes claude_code_session_id if present
                "elapsed_time": elapsed_time,
                "message_count": message_count,
            }

            return RuntimeExecutionResult(
                response=response_text,
                usage=usage,
                success=finish_reason == "success",
                finish_reason=finish_reason or "stop",
                tool_messages=tool_messages,
                model=context.model_id,
                metadata=final_metadata,
            )

        except ImportError as e:
            self.logger.error(
                "Claude Code SDK not installed",
                execution_id=context.execution_id,
                error=str(e),
            )
            return RuntimeExecutionResult(
                response="",
                usage={},
                success=False,
                error=f"Claude Code SDK not available: {str(e)}",
            )

        except asyncio.TimeoutError:
            self.logger.error(
                "Claude Code execution timeout",
                execution_id=context.execution_id,
                elapsed_time=asyncio.get_event_loop().time() - start_time,
            )
            return RuntimeExecutionResult(
                response="",
                usage={},
                success=False,
                error="Execution timeout exceeded",
            )

        except asyncio.CancelledError:
            self.logger.warning(
                "Claude Code execution cancelled",
                execution_id=context.execution_id,
            )
            raise  # Re-raise to propagate cancellation

        except Exception as e:
            self.logger.error(
                "Claude Code execution failed",
                execution_id=context.execution_id,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )

            return RuntimeExecutionResult(
                response="",
                usage={},
                success=False,
                error=f"{type(e).__name__}: {str(e)}",
            )

        finally:
            # Ensure cleanup happens
            # Note: We don't call client.disconnect() here because it has
            # asyncio cancel scope issues. The subprocess cleanup happens
            # automatically when the client object is garbage collected.
            if context.execution_id in self._active_clients:
                try:
                    del self._active_clients[context.execution_id]
                    self.logger.debug(
                        "Cleaned up Claude SDK client reference",
                        execution_id=context.execution_id,
                    )
                except Exception as cleanup_error:
                    self.logger.warning(
                        "Error during client cleanup",
                        execution_id=context.execution_id,
                        error=str(cleanup_error),
                    )

    async def _stream_execute_impl(
        self,
        context: RuntimeExecutionContext,
        event_callback: Optional[Callable[[Dict], None]] = None,
    ) -> AsyncIterator[RuntimeExecutionResult]:
        """
        Production-grade streaming execution with Claude Code SDK.

        This implementation provides:
        - Comprehensive error handling with specific exception types
        - Detailed structured logging at each stage
        - Proper resource cleanup with finally blocks
        - Real-time event callbacks for tool execution
        - Accumulated metrics and metadata tracking

        Args:
            context: Execution context with prompt, history, config
            event_callback: Optional callback for real-time events

        Yields:
            RuntimeExecutionResult chunks as they arrive, ending with final metadata
        """
        client = None
        start_time = asyncio.get_event_loop().time()
        chunk_count = 0

        try:
            from claude_agent_sdk import (
                ClaudeSDKClient,
                AssistantMessage,
                ResultMessage,
                TextBlock,
                ToolUseBlock,
                ToolResultBlock,
            )

            self.logger.info(
                "Starting Claude Code streaming execution",
                execution_id=context.execution_id,
                model=context.model_id,
                has_history=bool(context.conversation_history),
                has_callback=event_callback is not None,
            )

            # Build Claude Code options with hooks
            options, active_tools = self._build_claude_options(context, event_callback)

            self.logger.info(
                "Created Claude Code SDK options",
                execution_id=context.execution_id,
                has_tools=bool(context.skills),
                has_mcp=len(options.mcp_servers) > 0 if hasattr(options, 'mcp_servers') else False,
                has_hooks=bool(options.hooks) if hasattr(options, 'hooks') else False,
                has_event_callback=event_callback is not None,
            )

            # Create client and manually manage lifecycle to avoid asyncio cancel scope issues
            client = ClaudeSDKClient(options=options)
            await client.connect()
            self._active_clients[context.execution_id] = client

            # Cache execution metadata
            try:
                self.control_plane.cache_metadata(context.execution_id, "AGENT")
            except Exception as cache_error:
                self.logger.warning(
                    "Failed to cache metadata (non-fatal)",
                    execution_id=context.execution_id,
                    error=str(cache_error),
                )

            # Send prompt (SDK handles conversation history via session resume)
            # No need to manually inject history - the SDK maintains it via session_id
            prompt = context.prompt

            self.logger.debug(
                "Sending streaming query to Claude Code SDK",
                execution_id=context.execution_id,
                prompt_length=len(prompt),
                using_session_resume=bool(options.resume),
            )

            await client.query(prompt)

            # Stream messages
            accumulated_response = ""
            accumulated_usage = {}
            tool_messages = []
            # active_tools dict is shared with hooks (from _build_claude_options)
            message_count = 0
            received_stream_events = False  # Track if we got streaming events

            # Generate unique message_id for this turn (execution_id + timestamp)
            message_id = f"{context.execution_id}_{int(time.time() * 1000000)}"

            # Use receive_response() to get messages for this specific query
            # receive_response() yields messages until ResultMessage (completion)
            # This is better than receive_messages() which expects multiple queries
            # Check if verbose debug logging is enabled
            debug_mode = os.getenv("CLAUDE_CODE_DEBUG", "false").lower() == "true"

            async for message in client.receive_response():
                    message_count += 1
                    message_type_name = type(message).__name__

                    # Handle StreamEvent messages (these contain partial chunks!)
                    if message_type_name == "StreamEvent":
                        # StreamEvent has 'event' attribute (not 'data'!) with the partial content
                        if hasattr(message, 'event') and message.event:
                            event_data = message.event

                            # Extract text from event data
                            # The structure is: {'type': 'content_block_delta', 'delta': {'type': 'text_delta', 'text': 'content'}}
                            content = None
                            if isinstance(event_data, dict):
                                event_type = event_data.get('type')

                                # Handle content_block_delta events (these have the actual text!)
                                if event_type == 'content_block_delta':
                                    delta = event_data.get('delta', {})
                                    if isinstance(delta, dict):
                                        content = delta.get('text')
                                    elif isinstance(delta, str):
                                        content = delta

                                # Fallback: try direct text extraction
                                if not content:
                                    content = event_data.get('text') or event_data.get('content')

                            elif isinstance(event_data, str):
                                content = event_data
                            elif hasattr(event_data, 'content'):
                                content = event_data.content
                            elif hasattr(event_data, 'text'):
                                content = event_data.text

                            if content:
                                received_stream_events = True  # Mark that we got streaming chunks
                                chunk_count += 1
                                accumulated_response += content

                                # Publish event
                                if event_callback:
                                    try:
                                        event_callback({
                                            "type": "content_chunk",
                                            "content": content,
                                            "message_id": message_id,
                                            "execution_id": context.execution_id,
                                        })
                                    except Exception as callback_error:
                                        self.logger.warning(
                                            "StreamEvent callback failed",
                                            execution_id=context.execution_id,
                                            error=str(callback_error),
                                        )

                                # Yield chunk
                                yield RuntimeExecutionResult(
                                    response=content,
                                    usage={},
                                    success=True,
                                )
                        continue  # Skip to next message

                    # Handle assistant messages (final complete message)
                    if isinstance(message, AssistantMessage):
                        for block_idx, block in enumerate(message.content):
                            if isinstance(block, TextBlock):
                                # Skip sending TextBlock content if we already streamed it via StreamEvents
                                if received_stream_events:
                                    # Still accumulate for final result (in case it wasn't fully streamed)
                                    # But don't send to callback or yield (would be duplicate)
                                    continue

                                # Only send if we didn't receive StreamEvents
                                chunk_count += 1
                                accumulated_response += block.text

                                if event_callback:
                                    try:
                                        event_callback(
                                            {
                                                "type": "content_chunk",
                                                "content": block.text,
                                                "message_id": message_id,
                                                "execution_id": context.execution_id,
                                            }
                                        )
                                    except Exception as callback_error:
                                        self.logger.warning(
                                            "Event callback failed (non-fatal)",
                                            execution_id=context.execution_id,
                                            error=str(callback_error),
                                        )

                                yield RuntimeExecutionResult(
                                    response=block.text,
                                    usage={},
                                    success=True,
                                )

                            elif isinstance(block, ToolUseBlock):
                                # Tool use event - Store for later lookup
                                tool_info = {
                                    "tool": block.name,
                                    "input": block.input,
                                    "tool_use_id": block.id,
                                }
                                tool_messages.append(tool_info)
                                active_tools[block.id] = block.name

                                # NOTE: Don't publish tool_start here - pre-tool hook will publish it
                                # Hooks fire before stream processing, so publishing here causes events in wrong order

                            elif isinstance(block, ToolResultBlock):
                                # Tool result - Look up tool name from active_tools
                                tool_name = active_tools.get(block.tool_use_id, "unknown")
                                if tool_name == "unknown":
                                    self.logger.warning(
                                        "Could not find tool name for tool_use_id",
                                        execution_id=context.execution_id,
                                        tool_use_id=block.tool_use_id,
                                        active_tools_keys=list(active_tools.keys()),
                                    )

                                status = "success" if not block.is_error else "failed"

                                # Publish via callback (non-blocking)
                                if event_callback:
                                    try:
                                        event_callback(
                                            {
                                                "type": "tool_complete",
                                                "tool_name": tool_name,
                                                "tool_execution_id": block.tool_use_id,
                                                "status": status,
                                                "output": str(block.content)[:1000] if block.content else None,
                                                "error": str(block.content) if block.is_error else None,
                                                "execution_id": context.execution_id,
                                            }
                                        )
                                    except Exception as callback_error:
                                        self.logger.error(
                                            "Tool complete callback failed",
                                            execution_id=context.execution_id,
                                            tool_name=tool_name,
                                            error=str(callback_error),
                                            exc_info=True,
                                        )

                    # Handle result message (final)
                    elif isinstance(message, ResultMessage):
                        if message.usage:
                            accumulated_usage = {
                                "prompt_tokens": getattr(message.usage, "input_tokens", 0),
                                "completion_tokens": getattr(message.usage, "output_tokens", 0),
                                "total_tokens": getattr(message.usage, "total_tokens", 0),
                            }

                        # Extract session_id for conversation continuity
                        session_id = getattr(message, "session_id", None)
                        if session_id:
                            self.logger.info(
                                "✅ Claude Code session captured for conversation continuity (streaming)",
                                execution_id=context.execution_id[:8],
                                session_id=session_id[:16],
                            )
                        else:
                            self.logger.warning(
                                "⚠️  No session_id in ResultMessage (streaming) - multi-turn may not work",
                                execution_id=context.execution_id[:8],
                            )

                        elapsed_time = asyncio.get_event_loop().time() - start_time

                        self.logger.info(
                            "Claude Code streaming completed",
                            execution_id=context.execution_id,
                            finish_reason=message.subtype,
                            chunk_count=chunk_count,
                            message_count=message_count,
                            response_length=len(accumulated_response),
                            tool_count=len(tool_messages),
                            usage=accumulated_usage,
                            elapsed_time=f"{elapsed_time:.2f}s",
                            has_session_id=bool(session_id),
                        )

                        # Final result message
                        yield RuntimeExecutionResult(
                            response="",  # Already streamed
                            usage=accumulated_usage,
                            success=message.subtype == "success",
                            finish_reason=message.subtype,
                            tool_messages=tool_messages,
                            model=context.model_id,
                            metadata={
                                "accumulated_response": accumulated_response,
                                "elapsed_time": elapsed_time,
                                "chunk_count": chunk_count,
                                "message_count": message_count,
                                "claude_code_session_id": session_id,  # Store for next turn
                            },
                        )
                        break

        except ImportError as e:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(
                "Claude Code SDK not installed",
                execution_id=context.execution_id,
                error=str(e),
                elapsed_time=f"{elapsed_time:.2f}s",
            )
            yield RuntimeExecutionResult(
                response="",
                usage={},
                success=False,
                error=f"Claude Code SDK not available: {str(e)}",
            )

        except asyncio.TimeoutError:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(
                "Claude Code streaming timeout",
                execution_id=context.execution_id,
                elapsed_time=f"{elapsed_time:.2f}s",
                chunks_before_timeout=chunk_count,
            )
            yield RuntimeExecutionResult(
                response="",
                usage={},
                success=False,
                error="Streaming execution timeout exceeded",
            )

        except asyncio.CancelledError:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            self.logger.warning(
                "Claude Code streaming cancelled",
                execution_id=context.execution_id,
                elapsed_time=f"{elapsed_time:.2f}s",
                chunks_before_cancellation=chunk_count,
            )
            # Yield error result before re-raising
            yield RuntimeExecutionResult(
                response="",
                usage={},
                success=False,
                error="Execution was cancelled",
            )
            raise  # Re-raise to propagate cancellation

        except Exception as e:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(
                "Claude Code streaming failed",
                execution_id=context.execution_id,
                error=str(e),
                error_type=type(e).__name__,
                elapsed_time=f"{elapsed_time:.2f}s",
                chunks_before_error=chunk_count,
                exc_info=True,
            )
            yield RuntimeExecutionResult(
                response="",
                usage={},
                success=False,
                error=f"{type(e).__name__}: {str(e)}",
            )

        finally:
            # Ensure cleanup happens regardless of how we exit
            # Note: We don't call client.disconnect() here because it has
            # asyncio cancel scope issues. The subprocess cleanup happens
            # automatically when the client object is garbage collected.
            if context.execution_id in self._active_clients:
                try:
                    del self._active_clients[context.execution_id]
                    self.logger.debug(
                        "Cleaned up Claude SDK client reference",
                        execution_id=context.execution_id,
                    )
                except Exception as cleanup_error:
                    self.logger.warning(
                        "Error during streaming client cleanup",
                        execution_id=context.execution_id,
                        error=str(cleanup_error),
                    )

    async def cancel(self, execution_id: str) -> bool:
        """
        Cancel an in-progress execution via Claude SDK interrupt.

        Args:
            execution_id: ID of execution to cancel

        Returns:
            True if cancellation succeeded
        """
        if execution_id in self._active_clients:
            try:
                client = self._active_clients[execution_id]
                await client.interrupt()
                self.logger.info("Claude Code execution interrupted", execution_id=execution_id)
                return True
            except Exception as e:
                self.logger.error(
                    "Failed to interrupt Claude Code execution",
                    execution_id=execution_id,
                    error=str(e),
                )
                return False
        return False


    # Private helper methods

    def _build_claude_options(
        self, context: RuntimeExecutionContext, event_callback: Optional[Callable] = None
    ) -> Any:
        """
        Build ClaudeAgentOptions from execution context.

        Args:
            context: Execution context
            event_callback: Optional event callback for hooks

        Returns:
            ClaudeAgentOptions instance
        """
        from claude_agent_sdk import ClaudeAgentOptions

        # Extract configuration
        agent_config = context.agent_config or {}
        runtime_config = context.runtime_config or {}

        # Get LiteLLM configuration (same as DefaultRuntime/Agno)
        litellm_api_base = os.getenv("LITELLM_API_BASE", "https://llm-proxy.kubiya.ai")
        litellm_api_key = os.getenv("LITELLM_API_KEY")

        if not litellm_api_key:
            raise ValueError("LITELLM_API_KEY environment variable not set")

        # Determine model (use LiteLLM format)
        model = context.model_id or os.environ.get(
            "LITELLM_DEFAULT_MODEL", "kubiya/claude-sonnet-4"
        )

        # Map skills to Claude Code tool names
        allowed_tools = self._map_skills_to_tools(context.skills)

        # Build MCP servers (both from context and custom skills)
        mcp_servers, mcp_tool_names = self._build_mcp_servers(context)

        # Add MCP tool names to allowed_tools so they have permission to execute
        # This grants permission to all MCP server tools (e.g., workflow executor tools)
        allowed_tools.extend(mcp_tool_names)

        # Allow explicit MCP tool names from runtime_config (workaround for external MCP servers)
        # Usage: runtime_config = {"explicit_mcp_tools": ["mcp__check_prod_health", "other_tool"]}
        explicit_mcp_tools = runtime_config.get("explicit_mcp_tools", [])
        if explicit_mcp_tools:
            allowed_tools.extend(explicit_mcp_tools)
            self.logger.info(
                "Added explicit MCP tools from runtime_config",
                explicit_tools_count=len(explicit_mcp_tools),
                tools=explicit_mcp_tools,
            )

        self.logger.info(
            "✅ Final allowed_tools list configured",
            total_count=len(allowed_tools),
            builtin_tools_count=len(allowed_tools) - len(mcp_tool_names) - len(explicit_mcp_tools),
            mcp_tools_count=len(mcp_tool_names),
            explicit_mcp_tools_count=len(explicit_mcp_tools),
            all_tools=allowed_tools[:50],  # Limit to 50 for readability
            truncated=len(allowed_tools) > 50,
        )

        # If there are MCP servers and we have low confidence in tool extraction
        if context.mcp_servers and len(mcp_tool_names) < len(context.mcp_servers) * 2:
            self.logger.warning(
                "⚠️  LOW MCP TOOL CONFIDENCE - If you get permission errors, add to runtime_config:",
                mcp_servers_count=len(context.mcp_servers),
                mcp_tools_added=len(mcp_tool_names),
                example_config={
                    "explicit_mcp_tools": [
                        "mcp__your_server_name__your_tool_name",
                        "# Example: mcp__check_prod_health__status"
                    ]
                },
                message="See Claude's error message for the exact tool name it's trying to use"
            )

        # Create shared active_tools dict for tool name tracking
        # This is populated in the stream when ToolUseBlock is received,
        # and used in hooks to look up tool names
        active_tools: Dict[str, str] = {}

        # Build hooks for tool execution monitoring
        hooks = self._build_hooks(context, event_callback, active_tools) if event_callback else {}

        # Build environment with LiteLLM configuration
        env = runtime_config.get("env", {}).copy()

        # Configure Claude Code SDK to use LiteLLM proxy
        # The SDK respects ANTHROPIC_BASE_URL and ANTHROPIC_API_KEY
        env["ANTHROPIC_BASE_URL"] = litellm_api_base
        env["ANTHROPIC_API_KEY"] = litellm_api_key

        # Pass Kubiya API credentials for workflow execution
        # Workflow executor tools need these to execute workflows remotely
        kubiya_api_key = os.environ.get("KUBIYA_API_KEY")
        if kubiya_api_key:
            env["KUBIYA_API_KEY"] = kubiya_api_key
            self.logger.debug("Added KUBIYA_API_KEY to Claude Code subprocess environment")

        kubiya_api_base = os.environ.get("KUBIYA_API_BASE")
        if kubiya_api_base:
            env["KUBIYA_API_BASE"] = kubiya_api_base
            self.logger.debug(f"Added KUBIYA_API_BASE to Claude Code subprocess environment: {kubiya_api_base}")

        # Get session_id from previous turn for conversation continuity
        # Session IDs are stored in user_metadata from previous executions
        # NOTE: conversation_history is often empty because Agno/Claude Code manages history via session_id
        # So we check user_metadata directly instead of requiring conversation_history to be populated
        previous_session_id = None
        if context.user_metadata:
            previous_session_id = context.user_metadata.get("claude_code_session_id")

        self.logger.info(
            "Building Claude Code options",
            has_user_metadata=bool(context.user_metadata),
            has_session_id_in_metadata=bool(previous_session_id),
            previous_session_id=previous_session_id[:16] if previous_session_id else None,
            will_resume=bool(previous_session_id),
        )

        # Build options
        options = ClaudeAgentOptions(
            system_prompt=context.system_prompt,
            allowed_tools=allowed_tools,
            mcp_servers=mcp_servers,
            permission_mode=runtime_config.get("permission_mode", "acceptEdits"),
            cwd=agent_config.get("cwd") or runtime_config.get("cwd"),
            model=model,
            env=env,
            max_turns=runtime_config.get("max_turns"),
            hooks=hooks,
            setting_sources=[],  # Explicit: don't load filesystem settings
            include_partial_messages=True,  # Enable character-by-character streaming
            resume=previous_session_id,  # Resume previous conversation if available
        )

        # DEBUG: Verify the option is set
        self.logger.info(
            "🔧 Claude Code options configured",
            include_partial_messages=getattr(options, 'include_partial_messages', 'NOT SET'),
            permission_mode=options.permission_mode,
            model=options.model,
        )

        # Return both options and the shared active_tools dict for tool name tracking
        return options, active_tools

    def _build_prompt_with_history(self, context: RuntimeExecutionContext) -> str:
        """
        Build prompt with conversation history.

        Since ClaudeSDKClient maintains session continuity, we include
        the conversation history as context in the prompt.

        Args:
            context: Execution context

        Returns:
            Prompt string with history context
        """
        if not context.conversation_history:
            return context.prompt

        # Build context from history
        history_context = "Previous conversation:\n"
        for msg in context.conversation_history[-10:]:  # Last 10 messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            history_context += f"{role.capitalize()}: {content[:200]}...\n" if len(content) > 200 else f"{role.capitalize()}: {content}\n"

        return f"{history_context}\n\nCurrent request:\n{context.prompt}"

    def _map_skills_to_tools(self, skills: list) -> list:
        """
        Map skills to Claude Code tool names.

        This function translates our generic skill types to the specific
        tool names that Claude Code understands.

        Args:
            skills: List of skill objects

        Returns:
            List of Claude Code tool names
        """
        # Skill type to Claude Code tool mapping
        tool_mapping = {
            "shell": ["Bash", "BashOutput", "KillShell"],
            "file_system": ["Read", "Write", "Edit", "Glob", "Grep"],
            "web": ["WebFetch", "WebSearch"],
            "docker": ["Bash"],  # Docker commands via Bash
            "kubernetes": ["Bash"],  # kubectl via Bash
            "git": ["Bash"],  # git commands via Bash
            "task": ["Task"],  # Subagent tasks
            "notebook": ["NotebookEdit"],
            "planning": ["TodoWrite", "ExitPlanMode"],
        }

        tools = []
        for skill in skills:
            # Get skill type
            skill_type = None
            if hasattr(skill, "type"):
                skill_type = skill.type
            elif isinstance(skill, dict):
                skill_type = skill.get("type")

            # Map to Claude Code tools
            if skill_type and skill_type in tool_mapping:
                tools.extend(tool_mapping[skill_type])

        # Deduplicate and add default tools if none specified
        unique_tools = list(set(tools)) if tools else ["Read", "Write", "Bash"]

        self.logger.info(
            "Mapped skills to Claude Code tools",
            skill_count=len(skills),
            tool_count=len(unique_tools),
            tools=unique_tools,
        )

        return unique_tools

    def _extract_mcp_tool_names(self, server_name: str, server_obj: Any) -> list[str]:
        """
        Extract tool names from an MCP server object.

        MCP servers can have different structures, so we try multiple approaches:
        1. Check for 'tools' attribute (list of tool objects/dicts)
        2. Check for 'list_tools()' method
        3. Check if it's a dict with 'tools' key
        4. Use naming convention: mcp__<server_name> for the server itself

        Args:
            server_name: Name of the MCP server
            server_obj: MCP server object (could be various types)

        Returns:
            List of tool names that should be added to allowed_tools
        """
        tool_names = []

        try:
            # Approach 1: Check if server has a 'tools' attribute (list)
            if hasattr(server_obj, 'tools'):
                tools_attr = getattr(server_obj, 'tools')
                if isinstance(tools_attr, list):
                    for tool in tools_attr:
                        # Tool might be an object with 'name' attribute
                        if hasattr(tool, 'name'):
                            tool_names.append(tool.name)
                        # Or a dict with 'name' key
                        elif isinstance(tool, dict) and 'name' in tool:
                            tool_names.append(tool['name'])
                        # Or a callable with __name__
                        elif callable(tool) and hasattr(tool, '__name__'):
                            tool_names.append(tool.__name__)

            # Approach 2: Check if server has a list_tools() method
            elif hasattr(server_obj, 'list_tools') and callable(getattr(server_obj, 'list_tools')):
                try:
                    tools_list = server_obj.list_tools()
                    if isinstance(tools_list, list):
                        for tool in tools_list:
                            if isinstance(tool, str):
                                tool_names.append(tool)
                            elif isinstance(tool, dict) and 'name' in tool:
                                tool_names.append(tool['name'])
                            elif hasattr(tool, 'name'):
                                tool_names.append(tool.name)
                except Exception as e:
                    self.logger.debug(
                        f"Failed to call list_tools() on MCP server {server_name}: {e}"
                    )

            # Approach 3: Check if it's a dict with 'tools' key
            elif isinstance(server_obj, dict) and 'tools' in server_obj:
                tools_list = server_obj['tools']
                if isinstance(tools_list, list):
                    for tool in tools_list:
                        if isinstance(tool, str):
                            tool_names.append(tool)
                        elif isinstance(tool, dict) and 'name' in tool:
                            tool_names.append(tool['name'])

            # Approach 4: For external MCP servers, tools often follow pattern mcp__<server_name>__<tool_name>
            # But without knowing the tool names, we can't construct them
            # So we'll just log that we couldn't extract tools

            if tool_names:
                self.logger.debug(
                    f"Extracted {len(tool_names)} tools from MCP server '{server_name}'",
                    tools=tool_names
                )
            else:
                self.logger.debug(
                    f"Could not extract tool names from MCP server '{server_name}' using standard approaches"
                )

        except Exception as e:
            self.logger.error(
                f"Error extracting tools from MCP server '{server_name}': {e}",
                exc_info=True
            )

        return tool_names

    def _build_mcp_servers(self, context: RuntimeExecutionContext) -> tuple[Dict[str, Any], list[str]]:
        """
        Build MCP server configurations from context and custom skills.

        This converts our skills into Claude Code MCP servers for custom tools.
        Handles both legacy get_tools() and Toolkit.functions patterns.

        Args:
            context: Execution context

        Returns:
            Tuple of (MCP server configurations dict, list of all MCP tool names)
        """
        from claude_agent_sdk import create_sdk_mcp_server, tool as mcp_tool
        import asyncio

        mcp_servers = {}
        all_mcp_tool_names = []  # Track all tool names across all MCP servers

        # Include MCP servers from context (if any)
        if context.mcp_servers:
            self.logger.info(
                "Processing MCP servers from context",
                server_count=len(context.mcp_servers),
                server_names=list(context.mcp_servers.keys()),
            )

            for server_name, server_obj in context.mcp_servers.items():
                mcp_servers[server_name] = server_obj

                # Try to extract tool names from the MCP server object
                # MCP servers may have different structures, so we try multiple approaches
                extracted_tools = self._extract_mcp_tool_names(server_name, server_obj)
                if extracted_tools:
                    # Construct full MCP tool names: mcp__<server_name>__<tool_name>
                    # This is the format Claude Code expects in allowed_tools
                    # IMPORTANT: Sanitize names by replacing spaces with underscores
                    full_tool_names = []
                    for tool_name in extracted_tools:
                        # If tool already has mcp__ prefix, use as-is
                        if tool_name.startswith("mcp__"):
                            full_tool_names.append(tool_name)
                        else:
                            # Sanitize names: replace spaces with underscores
                            sanitized_server = server_name.replace(" ", "_")
                            sanitized_tool = tool_name.replace(" ", "_")
                            # Construct: mcp__<server_name>__<tool_name>
                            full_tool_name = f"mcp__{sanitized_server}__{sanitized_tool}"
                            full_tool_names.append(full_tool_name)

                    all_mcp_tool_names.extend(full_tool_names)
                    self.logger.info(
                        "Extracted and constructed MCP tool names",
                        server_name=server_name,
                        raw_tool_count=len(extracted_tools),
                        raw_tools=extracted_tools,
                        full_tool_names=full_tool_names,
                    )
                else:
                    # If we can't extract tools, try comprehensive fallback patterns
                    # MCP servers can expose tools in various ways - try all common patterns
                    # IMPORTANT: Sanitize by replacing spaces with underscores
                    sanitized_server = server_name.replace(" ", "_")

                    fallback_tools = [
                        f"mcp__{sanitized_server}",         # Pattern: mcp__<server_name>
                        sanitized_server,                    # Pattern: <server_name> (raw)
                        server_name,                         # Pattern: <server_name> (unsanitized)
                    ]

                    # If server name already has mcp__ prefix, also try without prefix
                    if server_name.startswith("mcp__"):
                        clean_name = server_name[5:]  # Remove "mcp__" prefix
                        fallback_tools.append(clean_name)
                        fallback_tools.append(f"mcp__{clean_name}")
                    else:
                        # Also try with mcp__ prefix prepended
                        fallback_tools.append(f"mcp__{sanitized_server}")

                    # Try common tool name patterns for this server (sanitized)
                    common_tool_names = ["check", "status", "health", "run", "execute"]
                    for tool_name in common_tool_names:
                        fallback_tools.append(f"mcp__{sanitized_server}__{tool_name}")

                    # Deduplicate
                    fallback_tools = list(set(fallback_tools))
                    all_mcp_tool_names.extend(fallback_tools)

                    # Log warning with comprehensive debug info
                    self.logger.warning(
                        "⚠️  Could not extract tool names from MCP server - using COMPREHENSIVE fallback patterns",
                        server_name=server_name,
                        fallback_tools_count=len(fallback_tools),
                        fallback_tools=fallback_tools,
                        server_type=type(server_obj).__name__,
                        has_tools_attr=hasattr(server_obj, 'tools'),
                        has_list_tools=hasattr(server_obj, 'list_tools'),
                        is_dict=isinstance(server_obj, dict),
                        dict_keys=list(server_obj.keys()) if isinstance(server_obj, dict) else None,
                        object_attrs=dir(server_obj)[:20] if hasattr(server_obj, '__dict__') else None,
                        message="⚠️  IMPORTANT: Check logs after execution - if still getting permission errors, add exact tool names to runtime_config.explicit_mcp_tools"
                    )

        # Convert custom skills to MCP servers
        for skill in context.skills:
            tools_list = []
            registered_tool_names = []  # Track tool names for logging
            skill_name = getattr(skill, "name", "custom_skill")

            # Check for Toolkit pattern (has .functions attribute)
            if hasattr(skill, "functions") and hasattr(skill.functions, 'items'):
                self.logger.info(
                    "Found skill with registered functions",
                    skill_name=skill_name,
                    function_count=len(skill.functions),
                    function_names=list(skill.functions.keys()),
                )

                # Extract tools from functions registry
                for func_name, func_obj in skill.functions.items():
                    # Skip helper tools for workflow_executor skills to avoid confusion
                    # Only expose the main workflow tool(s), not list_all_workflows or get_workflow_info
                    if func_name in ["list_all_workflows", "get_workflow_info"]:
                        self.logger.debug(
                            "Skipping helper tool for workflow_executor skill",
                            skill_name=skill_name,
                            tool_name=func_name,
                        )
                        continue

                    # Get entrypoint (the actual callable)
                    entrypoint = getattr(func_obj, 'entrypoint', None)
                    if not entrypoint:
                        self.logger.warning(
                            "Function missing entrypoint",
                            skill_name=skill_name,
                            function_name=func_name,
                        )
                        continue

                    # Get function metadata - use function name as-is
                    tool_name = func_name
                    tool_description = getattr(func_obj, 'description', None) or entrypoint.__doc__ or f"{tool_name} tool"
                    tool_parameters = getattr(func_obj, 'parameters', {})

                    # Create a closure that captures the entrypoint with proper variable scope
                    def make_tool_wrapper(tool_entrypoint, tool_func_name, tool_func_description, tool_func_parameters, tool_skill_name):
                        """Factory to create tool wrappers with proper closure"""
                        @mcp_tool(tool_func_name, tool_func_description, tool_func_parameters)
                        async def wrapped_tool(args: dict) -> dict:
                            try:
                                self.logger.debug(
                                    "Executing workflow tool",
                                    tool_name=tool_func_name,
                                    args=args,
                                )
                                # Call the entrypoint with unpacked args
                                if asyncio.iscoroutinefunction(tool_entrypoint):
                                    result = await tool_entrypoint(**args) if args else await tool_entrypoint()
                                    self.logger.info(
                                        "Async workflow tool completed successfully",
                                        tool_name=tool_func_name,
                                        result_length=len(str(result)),
                                        result_preview=str(result)[:500] if result else "(empty)"
                                    )
                                else:
                                    # ✅ Run synchronous tools in thread pool to avoid blocking event loop
                                    # This is critical for tools that do blocking I/O (like streaming HTTP requests)
                                    result = await asyncio.to_thread(
                                        lambda: tool_entrypoint(**args) if args else tool_entrypoint()
                                    )

                                self.logger.info(
                                    "Workflow tool completed successfully",
                                    tool_name=tool_func_name,
                                    result_length=len(str(result)),
                                    result_preview=str(result)[:500] if result else "(empty)"
                                )

                                return {
                                    "content": [{
                                        "type": "text",
                                        "text": str(result)
                                    }]
                                }
                            except Exception as e:
                                self.logger.error(
                                    "Workflow tool execution failed",
                                    tool_name=tool_func_name,
                                    error=str(e),
                                    exc_info=True,
                                )
                                return {
                                    "content": [{
                                        "type": "text",
                                        "text": f"Error executing {tool_func_name}: {str(e)}"
                                    }],
                                    "isError": True
                                }
                        return wrapped_tool

                    wrapped_tool = make_tool_wrapper(entrypoint, tool_name, tool_description, tool_parameters, skill_name)
                    tools_list.append(wrapped_tool)
                    registered_tool_names.append(tool_name)

                    # Construct full MCP tool name for allowed_tools: mcp__<server>__<tool>
                    # IMPORTANT: Replace spaces with underscores to match Claude Code SDK sanitization
                    sanitized_skill_name = skill_name.replace(" ", "_")
                    sanitized_tool_name = tool_name.replace(" ", "_")

                    # If tool name matches skill name, don't duplicate (e.g., mcp__run_ado_test not mcp__run_ado_test__run_ado_test)
                    if sanitized_tool_name == sanitized_skill_name:
                        full_mcp_tool_name = f"mcp__{sanitized_skill_name}"
                    else:
                        full_mcp_tool_name = f"mcp__{sanitized_skill_name}__{sanitized_tool_name}"

                    all_mcp_tool_names.append(full_mcp_tool_name)  # Track for allowed_tools

                    self.logger.info(
                        "Registered MCP tool from skill function",
                        skill_name=skill_name,
                        tool_name=tool_name,
                        full_mcp_tool_name=full_mcp_tool_name,
                    )

            # Legacy: Check if skill has get_tools() method
            elif hasattr(skill, "get_tools"):
                for tool_func in skill.get_tools():
                    # Wrap each tool function with MCP tool decorator
                    tool_name = getattr(tool_func, "__name__", "custom_tool")
                    tool_description = getattr(tool_func, "__doc__", f"{tool_name} tool")

                    # Create MCP tool wrapper
                    @mcp_tool(tool_name, tool_description, {})
                    async def wrapped_tool(args: dict) -> dict:
                        # ✅ Run synchronous tools in thread pool to avoid blocking event loop
                        if asyncio.iscoroutinefunction(tool_func):
                            result = await tool_func(**args) if args else await tool_func()
                        else:
                            result = await asyncio.to_thread(
                                lambda: tool_func(**args) if args else tool_func()
                            )
                        return {
                            "content": [{
                                "type": "text",
                                "text": str(result)
                            }]
                        }

                    tools_list.append(wrapped_tool)
                    registered_tool_names.append(tool_name)

                    # Construct full MCP tool name for allowed_tools: mcp__<server>__<tool>
                    # IMPORTANT: Replace spaces with underscores to match Claude Code SDK sanitization
                    sanitized_skill_name = skill_name.replace(" ", "_")
                    sanitized_tool_name = tool_name.replace(" ", "_")

                    # If tool name matches skill name, don't duplicate (e.g., mcp__run_ado_test not mcp__run_ado_test__run_ado_test)
                    if sanitized_tool_name == sanitized_skill_name:
                        full_mcp_tool_name = f"mcp__{sanitized_skill_name}"
                    else:
                        full_mcp_tool_name = f"mcp__{sanitized_skill_name}__{sanitized_tool_name}"

                    all_mcp_tool_names.append(full_mcp_tool_name)  # Track for allowed_tools

            # Create MCP server for this skill if it has tools
            if tools_list:
                # Use clean server name
                server_name = skill_name

                mcp_servers[server_name] = create_sdk_mcp_server(
                    name=server_name,
                    version="1.0.0",
                    tools=tools_list
                )

                self.logger.info(
                    "Created MCP server for skill",
                    skill_name=skill_name,
                    server_name=server_name,
                    tool_count=len(tools_list),
                )

        self.logger.info(
            "Built MCP servers",
            server_count=len(mcp_servers),
            servers=list(mcp_servers.keys()),
            mcp_tool_count=len(all_mcp_tool_names),
            mcp_tools=all_mcp_tool_names[:10] if len(all_mcp_tool_names) > 10 else all_mcp_tool_names,
        )

        return mcp_servers, all_mcp_tool_names

    def _build_hooks(
        self, context: RuntimeExecutionContext, event_callback: Callable, active_tools: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Build hooks for tool execution monitoring.

        Hooks intercept events like PreToolUse and PostToolUse to provide
        real-time feedback and monitoring. Since Claude Code SDK doesn't send
        ToolResultBlock in the stream, hooks are the only place to publish tool_completed events.

        Args:
            context: Execution context
            event_callback: Callback for publishing events
            active_tools: Shared dict mapping tool_use_id -> tool_name (populated from ToolUseBlock)

        Returns:
            Dict of hook configurations
        """
        from claude_agent_sdk import HookMatcher

        execution_id = context.execution_id

        async def pre_tool_hook(input_data, tool_use_id, tool_context):
            """Hook called before tool execution"""
            # ALWAYS debug to see what's available in pre-tool hook
            print(f"\n🪝 Pre-Tool Hook DEBUG:")
            print(f"   Tool Use ID: {tool_use_id}")
            print(f"   input_data type: {type(input_data)}")
            print(f"   input_data keys: {list(input_data.keys()) if isinstance(input_data, dict) else 'not a dict'}")
            print(f"   input_data: {str(input_data)[:500]}")
            print(f"   tool_context: {tool_context}")

            # Try to extract tool name from input_data (similar to post-tool hook)
            tool_name = "unknown"
            tool_args = {}

            if isinstance(input_data, dict):
                # Check if input_data has tool_name like output_data does
                tool_name = input_data.get("tool_name", "unknown")
                tool_args = input_data.get("tool_input", {})

                if tool_name == "unknown":
                    print(f"   ❌ No tool_name in input_data")
                else:
                    print(f"   ✅ Found tool_name: {tool_name}")

            # Publish tool_start event
            if event_callback and tool_name != "unknown":
                try:
                    event_callback({
                        "type": "tool_start",
                        "tool_name": tool_name,
                        "tool_args": tool_args,
                        "tool_execution_id": tool_use_id,
                        "execution_id": execution_id,
                    })
                    print(f"   ✅ Published tool_start event")
                except Exception as e:
                    self.logger.error(
                        "Failed to publish tool_start",
                        tool_name=tool_name,
                        error=str(e),
                        exc_info=True
                    )
                    print(f"   ❌ Failed to publish: {e}")

            return {}

        async def post_tool_hook(output_data, tool_use_id, tool_context):
            """Hook called after tool execution"""
            # Extract tool name from output_data (provided by Claude Code SDK)
            tool_name = "unknown"
            if isinstance(output_data, dict):
                # Claude SDK provides tool_name directly in output_data
                tool_name = output_data.get("tool_name", "unknown")

            is_error = tool_context.get("is_error", False)

            # Debug mode logging
            debug_mode = os.getenv("CLAUDE_CODE_DEBUG", "false").lower() == "true"
            if debug_mode:
                print(f"\n🪝 Post-Tool Hook:")
                print(f"   Tool: {tool_name}")
                print(f"   Status: {'failed' if is_error else 'success'}")

            # Publish tool_complete event (hooks are the ONLY place for Claude Code)
            # ToolResultBlock doesn't appear in Claude Code streams
            if event_callback:
                try:
                    event_callback({
                        "type": "tool_complete",
                        "tool_name": tool_name,
                        "tool_execution_id": tool_use_id,
                        "status": "failed" if is_error else "success",
                        "output": str(output_data)[:1000] if output_data else None,
                        "error": str(output_data) if is_error else None,
                        "execution_id": execution_id,
                    })
                except Exception as e:
                    self.logger.error(
                        "Failed to publish tool_complete",
                        tool_name=tool_name,
                        error=str(e),
                        exc_info=True
                    )

            return {}

        # Build hook configuration
        hooks = {
            "PreToolUse": [HookMatcher(hooks=[pre_tool_hook])],
            "PostToolUse": [HookMatcher(hooks=[post_tool_hook])],
        }

        return hooks

    def _get_sdk_version(self) -> str:
        """Get Claude Code SDK version."""
        try:
            import claude_agent_sdk
            return getattr(claude_agent_sdk, "__version__", "unknown")
        except:
            return "unknown"
