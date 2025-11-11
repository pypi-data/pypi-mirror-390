"""Async environment variables for sandboxes."""

from typing import Optional, Dict
import logging
from ._async_agent_client import AsyncAgentHTTPClient

logger = logging.getLogger(__name__)


class AsyncEnvironmentVariables:
    """Async environment variable operations."""
    
    def __init__(self, sandbox):
        """Initialize with sandbox reference."""
        self._sandbox = sandbox
        logger.debug("AsyncEnvironmentVariables initialized")
    
    async def _get_client(self) -> AsyncAgentHTTPClient:
        """Get agent client from sandbox."""
        await self._sandbox._ensure_agent_client()
        return self._sandbox._agent_client
    
    async def get(self, name: str) -> Optional[str]:
        """Get environment variable."""
        client = await self._get_client()
        response = await client.get(
            f"/env/{name}",
            operation="get env var",
            context={"name": name}
        )
        return response.get("value")
    
    async def set(self, name: str, value: str) -> None:
        """Set environment variable."""
        client = await self._get_client()
        await client.post(
            "/env",
            json={"name": name, "value": value},
            operation="set env var",
            context={"name": name}
        )
    
    async def get_all(self) -> Dict[str, str]:
        """Get all environment variables."""
        client = await self._get_client()
        response = await client.get(
            "/env",
            operation="get all env vars"
        )
        return response.get("env_vars", {})
    
    async def delete(self, name: str) -> None:
        """Delete environment variable."""
        client = await self._get_client()
        await client.delete(
            f"/env/{name}",
            operation="delete env var",
            context={"name": name}
        )
