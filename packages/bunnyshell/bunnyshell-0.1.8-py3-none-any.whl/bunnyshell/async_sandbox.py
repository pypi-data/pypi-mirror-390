"""Async Sandbox class - for async/await usage."""

from typing import Optional, List, AsyncIterator, Dict
from .models import SandboxInfo, Template
from ._async_client import AsyncHTTPClient
from ._utils import remove_none_values


class AsyncSandbox:
    """
    Async Bunnyshell Sandbox - lightweight VM management with async/await.
    
    For async Python applications (FastAPI, aiohttp, etc.)
    
    Example:
        >>> from bunnyshell import AsyncSandbox
        >>> 
        >>> async with AsyncSandbox.create(template="nodejs") as sandbox:
        ...     info = await sandbox.get_info()
        ...     print(info.public_host)
        # Automatically cleaned up!
    """
    
    def __init__(
        self,
        sandbox_id: str,
        *,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
        timeout: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize AsyncSandbox instance.
        
        Note: Prefer using AsyncSandbox.create() or AsyncSandbox.connect() instead.
        
        Args:
            sandbox_id: Sandbox ID
            api_key: API key (or use BUNNYSHELL_API_KEY env var)
            base_url: API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.sandbox_id = sandbox_id
        self._client = AsyncHTTPClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
    
    # =============================================================================
    # CLASS METHODS (Static - for creating/listing sandboxes)
    # =============================================================================
    
    @classmethod
    async def create(
        cls,
        template: Optional[str] = None,
        *,
        template_id: Optional[str] = None,
        region: Optional[str] = None,
        timeout: int = 300,
        env_vars: Optional[Dict[str, str]] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> "AsyncSandbox":
        """
        Create a new sandbox (async).
        
        You can create a sandbox in two ways:
        1. From template ID (resources auto-loaded from template)
        2. Custom sandbox (specify template name + resources)
        
        Args:
            template: Template name for custom sandbox (e.g., "code-interpreter", "nodejs")
            template_id: Template ID to create from (resources auto-loaded, no vcpu/memory needed)
            vcpu: Number of vCPUs (required for custom sandbox, ignored for template_id)
            memory_mb: Memory in MB (required for custom sandbox, ignored for template_id)
            disk_gb: Disk size in GB (optional)
            region: Preferred region (optional)
            timeout: Sandbox timeout in seconds (default: 300)
            env_vars: Environment variables (optional)
            api_key: API key (or use BUNNYSHELL_API_KEY env var)
            base_url: API base URL
        
        Returns:
            AsyncSandbox instance
        
        Examples:
            >>> # Create from template ID
            >>> sandbox = await AsyncSandbox.create(template_id="282")
            
            >>> # Create custom sandbox
            >>> sandbox = await AsyncSandbox.create(template="nodejs", vcpu=4, memory_mb=4096)
        """
        client = AsyncHTTPClient(api_key=api_key, base_url=base_url)
        
        # Validate parameters
        if template_id:
            # Create from template ID (resources from template)
            data = remove_none_values({
                "template_id": template_id,
                "region": region,
                "env_vars": env_vars,
            })
        elif template:
            # Create from template name (resources from template)
            data = remove_none_values({
                "template_name": template,
                "region": region,
                "env_vars": env_vars,
            })
        else:
            raise ValueError("Either 'template' or 'template_id' must be provided")
        
        response = await client.post("/v1/sandboxes", json=data)
        sandbox_id = response["id"]
        
        return cls(
            sandbox_id=sandbox_id,
            api_key=api_key,
            base_url=base_url,
        )
    
    @classmethod
    async def connect(
        cls,
        sandbox_id: str,
        *,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> "AsyncSandbox":
        """
        Connect to an existing sandbox (async).
        
        Args:
            sandbox_id: Sandbox ID
            api_key: API key (or use BUNNYSHELL_API_KEY env var)
            base_url: API base URL
        
        Returns:
            AsyncSandbox instance
        
        Example:
            >>> sandbox = await AsyncSandbox.connect("sandbox_id")
            >>> info = await sandbox.get_info()
        """
        instance = cls(
            sandbox_id=sandbox_id,
            api_key=api_key,
            base_url=base_url,
        )
        
        # Verify it exists
        await instance.get_info()
        
        return instance
    
    @classmethod
    async def list(
        cls,
        *,
        status: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 100,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> List["AsyncSandbox"]:
        """
        List all sandboxes (async).
        
        Args:
            status: Filter by status
            region: Filter by region
            limit: Maximum number of results
            api_key: API key
            base_url: API base URL
        
        Returns:
            List of AsyncSandbox instances
        
        Example:
            >>> sandboxes = await AsyncSandbox.list(status="running")
            >>> for sb in sandboxes:
            ...     info = await sb.get_info()
            ...     print(info.public_host)
        """
        client = AsyncHTTPClient(api_key=api_key, base_url=base_url)
        
        params = remove_none_values({
            "status": status,
            "region": region,
            "limit": limit,
        })
        
        response = await client.get("/v1/sandboxes", params=params)
        sandboxes_data = response.get("data", [])
        
        return [
            cls(
                sandbox_id=sb["id"],
                api_key=api_key,
                base_url=base_url,
            )
            for sb in sandboxes_data
        ]
    
    @classmethod
    async def iter(
        cls,
        *,
        status: Optional[str] = None,
        region: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> AsyncIterator["AsyncSandbox"]:
        """
        Lazy async iterator for sandboxes.
        
        Yields sandboxes one by one, fetching pages as needed.
        
        Args:
            status: Filter by status
            region: Filter by region
            api_key: API key
            base_url: API base URL
        
        Yields:
            AsyncSandbox instances
        
        Example:
            >>> async for sandbox in AsyncSandbox.iter(status="running"):
            ...     info = await sandbox.get_info()
            ...     print(info.public_host)
            ...     if found:
            ...         break  # Doesn't fetch remaining pages
        """
        client = AsyncHTTPClient(api_key=api_key, base_url=base_url)
        limit = 100
        has_more = True
        cursor = None
        
        while has_more:
            params = {"limit": limit}
            if status:
                params["status"] = status
            if region:
                params["region"] = region
            if cursor:
                params["cursor"] = cursor
            
            response = await client.get("/v1/sandboxes", params=params)
            
            for item in response.get("data", []):
                yield cls(
                    sandbox_id=item["id"],
                    api_key=api_key,
                    base_url=base_url,
                )
            
            has_more = response.get("has_more", False)
            cursor = response.get("next_cursor")
    
    @classmethod
    async def list_templates(
        cls,
        *,
        category: Optional[str] = None,
        language: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> List[Template]:
        """
        List available templates (async).
        
        Args:
            category: Filter by category
            language: Filter by language
            api_key: API key
            base_url: API base URL
        
        Returns:
            List of Template objects
        
        Example:
            >>> templates = await AsyncSandbox.list_templates()
            >>> for t in templates:
            ...     print(f"{t.name}: {t.display_name}")
        """
        client = AsyncHTTPClient(api_key=api_key, base_url=base_url)
        
        params = remove_none_values({
            "category": category,
            "language": language,
        })
        
        response = await client.get("/v1/templates", params=params)
        templates_data = response.get("data", [])
        
        return [Template(**t) for t in templates_data]
    
    @classmethod
    async def get_template(
        cls,
        name: str,
        *,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> Template:
        """
        Get template details (async).
        
        Args:
            name: Template name
            api_key: API key
            base_url: API base URL
        
        Returns:
            Template object
        
        Example:
            >>> template = await AsyncSandbox.get_template("nodejs")
            >>> print(template.description)
        """
        client = AsyncHTTPClient(api_key=api_key, base_url=base_url)
        response = await client.get(f"/v1/templates/{name}")
        return Template(**response)
    
    # =============================================================================
    # INSTANCE METHODS (for managing individual sandbox)
    # =============================================================================
    
    async def get_info(self) -> SandboxInfo:
        """
        Get current sandbox information (async).
        
        Returns:
            SandboxInfo with current state
        
        Example:
            >>> info = await sandbox.get_info()
            >>> print(f"Status: {info.status}")
        """
        response = await self._client.get(f"/v1/sandboxes/{self.sandbox_id}")
        return SandboxInfo(
            sandbox_id=response["id"],
            template_id=response.get("template_id"),
            template_name=response.get("template_name"),
            organization_id=response.get("organization_id", ""),
            node_id=response.get("node_id"),
            region=response.get("region"),
            status=response["status"],
            public_host=response.get("public_host") or response.get("direct_url", ""),
            vcpu=response.get("resources", {}).get("vcpu"),
            memory_mb=response.get("resources", {}).get("memory_mb"),
            disk_mb=response.get("resources", {}).get("disk_mb"),
            created_at=response.get("created_at"),
            started_at=None,
            end_at=None,
        )
    
    async def stop(self) -> None:
        """Stop the sandbox (async)."""
        await self._client.post(f"/v1/sandboxes/{self.sandbox_id}/stop")
    
    async def start(self) -> None:
        """Start a stopped sandbox (async)."""
        await self._client.post(f"/v1/sandboxes/{self.sandbox_id}/start")
    
    async def pause(self) -> None:
        """Pause the sandbox (async)."""
        await self._client.post(f"/v1/sandboxes/{self.sandbox_id}/pause")
    
    async def resume(self) -> None:
        """Resume a paused sandbox (async)."""
        await self._client.post(f"/v1/sandboxes/{self.sandbox_id}/resume")
    
    async def kill(self) -> None:
        """
        Destroy the sandbox immediately (async).
        
        This action is irreversible.
        
        Example:
            >>> await sandbox.kill()
        """
        await self._client.delete(f"/v1/sandboxes/{self.sandbox_id}")
    
    # =============================================================================
    # ASYNC CONTEXT MANAGER (auto-cleanup)
    # =============================================================================
    
    async def __aenter__(self) -> "AsyncSandbox":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, *args) -> None:
        """Async context manager exit - auto cleanup."""
        try:
            await self.kill()
        except Exception:
            # Ignore errors on cleanup
            pass
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def __repr__(self) -> str:
        return f"<AsyncSandbox {self.sandbox_id}>"
    
    def __str__(self) -> str:
        return f"AsyncSandbox(id={self.sandbox_id})"

