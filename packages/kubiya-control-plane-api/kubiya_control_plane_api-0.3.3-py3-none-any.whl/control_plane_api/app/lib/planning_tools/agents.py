"""
Agent Context Tools - Fetch agent information for task planning
"""

from typing import Optional
from control_plane_api.app.lib.planning_tools.base import BasePlanningTools


class AgentsContextTools(BasePlanningTools):
    """
    Tools for fetching agent context and capabilities

    Provides methods to:
    - List all available agents
    - Get detailed agent information
    - Query agent capabilities
    - Check agent availability
    """

    def __init__(self, base_url: str = "http://localhost:8000", organization_id: Optional[str] = None):
        super().__init__(base_url=base_url, organization_id=organization_id)
        self.name = "agent_context_tools"

    async def list_agents(self, limit: int = 50) -> str:
        """
        List all available agents with their basic information

        Args:
            limit: Maximum number of agents to return

        Returns:
            Formatted string with agent information including:
            - Agent name and ID
            - Model being used
            - Description/capabilities
            - Current status
        """
        try:
            params = {"limit": limit}
            if self.organization_id:
                params["organization_id"] = self.organization_id

            response = await self._make_request("GET", "/agents", params=params)

            agents = response if isinstance(response, list) else response.get("agents", [])

            return self._format_list_response(
                items=agents,
                title="Available Agents",
                key_fields=["model_id", "description", "status", "runner_name"],
            )

        except Exception as e:
            return f"Error listing agents: {str(e)}"

    async def get_agent_details(self, agent_id: str) -> str:
        """
        Get detailed information about a specific agent

        Args:
            agent_id: ID of the agent to fetch

        Returns:
            Detailed agent information including:
            - Full configuration
            - Available tools/capabilities
            - Model details
            - Resource requirements
        """
        try:
            response = await self._make_request("GET", f"/agents/{agent_id}")

            return self._format_detail_response(
                item=response,
                title=f"Agent Details: {response.get('name', 'Unknown')}",
            )

        except Exception as e:
            return f"Error fetching agent {agent_id}: {str(e)}"

    async def search_agents_by_capability(self, capability: str) -> str:
        """
        Search for agents that have a specific capability

        Args:
            capability: Capability to search for (e.g., "kubernetes", "aws", "python")

        Returns:
            List of agents matching the capability
        """
        try:
            # First get all agents
            params = {}
            if self.organization_id:
                params["organization_id"] = self.organization_id

            response = await self._make_request("GET", "/agents", params=params)
            agents = response if isinstance(response, list) else response.get("agents", [])

            # Filter by capability (search in description and tools)
            matching_agents = []
            for agent in agents:
                agent_text = f"{agent.get('name', '')} {agent.get('description', '')}".lower()
                if capability.lower() in agent_text:
                    matching_agents.append(agent)

            return self._format_list_response(
                items=matching_agents,
                title=f"Agents with '{capability}' capability",
                key_fields=["model_id", "description"],
            )

        except Exception as e:
            return f"Error searching agents: {str(e)}"

    async def get_agent_execution_history(self, agent_id: str, limit: int = 10) -> str:
        """
        Get recent execution history for an agent

        Args:
            agent_id: ID of the agent
            limit: Number of recent executions to fetch

        Returns:
            Recent execution history with success rates
        """
        try:
            params = {"limit": limit, "entity_id": agent_id}
            response = await self._make_request("GET", "/executions", params=params)

            executions = response if isinstance(response, list) else response.get("executions", [])

            if not executions:
                return f"No execution history found for agent {agent_id}"

            # Calculate success rate
            completed = sum(1 for e in executions if e.get("status") == "completed")
            total = len(executions)
            success_rate = (completed / total * 100) if total > 0 else 0

            output = [
                f"Execution History for Agent (Last {total} runs):",
                f"Success Rate: {success_rate:.1f}% ({completed}/{total})",
                "\nRecent Executions:",
            ]

            for idx, execution in enumerate(executions[:5], 1):
                status = execution.get("status", "unknown")
                prompt = execution.get("prompt", "No description")[:50]
                output.append(f"{idx}. Status: {status} | Task: {prompt}...")

            return "\n".join(output)

        except Exception as e:
            return f"Error fetching execution history: {str(e)}"
