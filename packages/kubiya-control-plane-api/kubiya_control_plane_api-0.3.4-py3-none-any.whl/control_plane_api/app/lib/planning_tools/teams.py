"""
Team Context Tools - Fetch team information for task planning
"""

from typing import Optional
from control_plane_api.app.lib.planning_tools.base import BasePlanningTools


class TeamsContextTools(BasePlanningTools):
    """
    Tools for fetching team context and composition

    Provides methods to:
    - List all available teams
    - Get detailed team information
    - Query team member capabilities
    - Check team availability
    """

    def __init__(self, base_url: str = "http://localhost:8000", organization_id: Optional[str] = None):
        super().__init__(base_url=base_url, organization_id=organization_id)
        self.name = "team_context_tools"

    async def list_teams(self, limit: int = 50) -> str:
        """
        List all available teams with their basic information

        Args:
            limit: Maximum number of teams to return

        Returns:
            Formatted string with team information including:
            - Team name and ID
            - Number of agents
            - Team description
            - Agent composition
        """
        try:
            params = {"limit": limit}
            if self.organization_id:
                params["organization_id"] = self.organization_id

            response = await self._make_request("GET", "/teams", params=params)

            teams = response if isinstance(response, list) else response.get("teams", [])

            return self._format_list_response(
                items=teams,
                title="Available Teams",
                key_fields=["description", "agent_count", "status"],
            )

        except Exception as e:
            return f"Error listing teams: {str(e)}"

    async def get_team_details(self, team_id: str) -> str:
        """
        Get detailed information about a specific team

        Args:
            team_id: ID of the team to fetch

        Returns:
            Detailed team information including:
            - Full team configuration
            - List of all team members with their roles
            - Team capabilities (aggregate of member capabilities)
            - Coordination strategy
        """
        try:
            response = await self._make_request("GET", f"/teams/{team_id}")

            team_name = response.get("name", "Unknown")
            agents = response.get("agents", [])

            output = [
                f"Team Details: {team_name}",
                f"  ID: {response.get('id')}",
                f"  Description: {response.get('description', 'No description')}",
                f"  Agent Count: {len(agents)}",
                "",
                "Team Members:",
            ]

            for idx, agent in enumerate(agents, 1):
                output.append(f"  {idx}. {agent.get('name', 'Unnamed')} (ID: {agent.get('id')})")
                if "model_id" in agent:
                    output.append(f"     Model: {agent['model_id']}")
                if "description" in agent:
                    output.append(f"     Capabilities: {agent['description'][:100]}")

            return "\n".join(output)

        except Exception as e:
            return f"Error fetching team {team_id}: {str(e)}"

    async def get_team_members(self, team_id: str) -> str:
        """
        Get list of agents in a specific team

        Args:
            team_id: ID of the team

        Returns:
            List of team members with their capabilities
        """
        try:
            response = await self._make_request("GET", f"/teams/{team_id}")

            agents = response.get("agents", [])

            if not agents:
                return f"Team {team_id} has no members"

            return self._format_list_response(
                items=agents,
                title=f"Team Members ({len(agents)} total)",
                key_fields=["model_id", "description", "runner_name"],
            )

        except Exception as e:
            return f"Error fetching team members: {str(e)}"

    async def search_teams_by_capability(self, capability: str) -> str:
        """
        Search for teams that have agents with a specific capability

        Args:
            capability: Capability to search for (e.g., "devops", "security", "data")

        Returns:
            List of teams with members having the capability
        """
        try:
            params = {}
            if self.organization_id:
                params["organization_id"] = self.organization_id

            response = await self._make_request("GET", "/teams", params=params)
            teams = response if isinstance(response, list) else response.get("teams", [])

            matching_teams = []
            for team in teams:
                team_text = f"{team.get('name', '')} {team.get('description', '')}".lower()
                agents = team.get("agents", [])
                agent_text = " ".join([a.get("description", "") for a in agents]).lower()

                if capability.lower() in team_text or capability.lower() in agent_text:
                    matching_teams.append(team)

            return self._format_list_response(
                items=matching_teams,
                title=f"Teams with '{capability}' capability",
                key_fields=["description", "agent_count"],
            )

        except Exception as e:
            return f"Error searching teams: {str(e)}"

    async def get_team_execution_history(self, team_id: str, limit: int = 10) -> str:
        """
        Get recent execution history for a team

        Args:
            team_id: ID of the team
            limit: Number of recent executions to fetch

        Returns:
            Recent execution history with success rates
        """
        try:
            params = {"limit": limit, "entity_id": team_id, "execution_type": "team"}
            response = await self._make_request("GET", "/executions", params=params)

            executions = response if isinstance(response, list) else response.get("executions", [])

            if not executions:
                return f"No execution history found for team {team_id}"

            completed = sum(1 for e in executions if e.get("status") == "completed")
            total = len(executions)
            success_rate = (completed / total * 100) if total > 0 else 0

            output = [
                f"Execution History for Team (Last {total} runs):",
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
