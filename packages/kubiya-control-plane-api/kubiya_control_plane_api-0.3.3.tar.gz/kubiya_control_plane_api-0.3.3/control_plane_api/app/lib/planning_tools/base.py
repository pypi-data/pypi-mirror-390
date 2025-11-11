"""
Base classes and utilities for planning tools
"""

from typing import Optional, Dict, Any, List
from agno.tools.toolkit import Toolkit
import structlog
import httpx
import json

logger = structlog.get_logger()


class BasePlanningTools(Toolkit):
    """
    Base class for all planning tools with common utilities

    Provides:
    - HTTP client for API calls
    - Common error handling
    - Response formatting
    - Logging utilities
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        organization_id: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize base planning tools

        Args:
            base_url: Base URL for the control plane API
            organization_id: Organization context for filtering
            timeout: HTTP request timeout in seconds
        """
        super().__init__(name="base_planning_tools")
        self.base_url = base_url.rstrip("/")
        self.organization_id = organization_id
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )
        return self._client

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with error handling

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (will be appended to base_url)
            params: Query parameters
            data: Request body data

        Returns:
            Parsed JSON response

        Raises:
            Exception: If request fails
        """
        client = await self._get_client()

        try:
            logger.info(
                "planning_tool_request",
                method=method,
                endpoint=endpoint,
                has_params=bool(params),
                has_data=bool(data),
            )

            response = await client.request(
                method=method,
                url=endpoint,
                params=params,
                json=data,
            )
            response.raise_for_status()

            result = response.json()
            logger.info(
                "planning_tool_response",
                endpoint=endpoint,
                status_code=response.status_code,
            )

            return result

        except httpx.HTTPStatusError as e:
            logger.error(
                "planning_tool_http_error",
                endpoint=endpoint,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise Exception(f"HTTP {e.response.status_code}: {str(e)}")
        except Exception as e:
            logger.error(
                "planning_tool_error",
                endpoint=endpoint,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    def _format_list_response(
        self,
        items: List[Dict[str, Any]],
        title: str,
        key_fields: List[str],
    ) -> str:
        """
        Format a list of items as a readable string

        Args:
            items: List of items to format
            title: Title for the list
            key_fields: Fields to include in the output

        Returns:
            Formatted string representation
        """
        if not items:
            return f"{title}: None available"

        output = [f"{title} ({len(items)} total):"]
        for idx, item in enumerate(items, 1):
            output.append(f"\n{idx}. {item.get('name', 'Unnamed')} (ID: {item.get('id', 'N/A')})")
            for field in key_fields:
                if field in item and item[field]:
                    value = item[field]
                    # Format nested objects
                    if isinstance(value, dict):
                        value = json.dumps(value, indent=2)
                    elif isinstance(value, list):
                        value = f"{len(value)} items"
                    output.append(f"   - {field}: {value}")

        return "\n".join(output)

    def _format_detail_response(
        self,
        item: Dict[str, Any],
        title: str,
    ) -> str:
        """
        Format a single item as a readable string

        Args:
            item: Item to format
            title: Title for the item

        Returns:
            Formatted string representation
        """
        if not item:
            return f"{title}: Not found"

        output = [f"{title}:"]
        for key, value in item.items():
            if isinstance(value, dict):
                value = json.dumps(value, indent=2)
            elif isinstance(value, list):
                value = f"{len(value)} items: {', '.join([str(v) for v in value[:3]])}{'...' if len(value) > 3 else ''}"
            output.append(f"  {key}: {value}")

        return "\n".join(output)

    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
