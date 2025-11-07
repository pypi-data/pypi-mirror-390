"""Browser automation clients for use in agent code.

This module provides browser automation clients (like Stagehand) that can be used
inside agent code to interact with browsers. These are different from providers
(like Browserbase) which provide the infrastructure/runtime.
"""

from typing import Any, Optional
import asyncio
import logging
import re
import os
from simultaneous.runtime.base import RuntimeKind
from simultaneous.providers.base import ProviderAdapter
from simultaneous.providers.router import get_adapter
from simultaneous.client.base import BaseClient

logger = logging.getLogger(__name__)


class BrowserClient(BaseClient):
    """
    Browser automation client for use in agent code.
    
    This client wraps browser automation SDKs (like Stagehand) and can be used inside
    agent code to interact with browsers. It connects to a session URL provided by
    the provider (e.g., Browserbase) and exposes browser automation primitives.
    
    Example:
        ```python
        from simultaneous import SimClient, Browser, BrowserClient
        
        client = SimClient()
        
        @client.agent(name="scrape", runtime=Browser(provider="browserbase"))
        async def scrape(query: str):
            # BrowserClient is initialized with the session URL from the provider
            browser = BrowserClient(session_url="wss://...")
            await browser.init()
            page = browser.page
            await page.goto(f"https://example.com/search?q={query}")
            # ... automation code
        ```
    
    Note:
        BrowserClient is a browser automation client wrapper, not a provider. The provider
        (e.g., Browserbase via Simultaneous API) provides the session URL that
        BrowserClient connects to.
    """
    
    def __init__(
        self,
        *,
        browserbase_session_id: Optional[str] = None,
        session_url: Optional[str] = None,
        # Provider/adapter configuration (optional; enables self-launch)
        adapter: ProviderAdapter | None = None,
        provider: str | None = None,
        provider_config: dict | None = None,
        browser_project_id: str | None = None,  # e.g., Browserbase projectId
        model_api_key: Optional[str] = None,
        model_name: str,
        model_client_options: dict | None = None,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ):
        """
        Initialize BrowserClient.
        
        Args:
            browserbase_session_id: Browserbase session ID (preferred)
            session_url: Browser session URL (WebSocket endpoint from provider)
            model_api_key: Model API key used by Stagehand AI features (required)
            model_name: Model identifier (e.g., "gpt-4o", "claude-3.5") (required)
            model_client_options: Extra client options (e.g., base_url, headers) (optional)
            api_key: Reserved for future browser SDK auth (optional)
            **kwargs: Additional options
        """
        # Initialize base client
        super().__init__(
            session_url=session_url,
            adapter=adapter,
            provider=provider,
            provider_config=provider_config,
            api_key=api_key,
            model_api_key=model_api_key,
            model_name=model_name,
            model_client_options=model_client_options,
            **kwargs,
        )
        
        # Browser-specific attributes
        self.browserbase_session_id = browserbase_session_id
        self._browser_project_id = browser_project_id or os.getenv("BROWSERBASE_PROJECT_ID")
        # Track if we launched this session ourselves (so we know to cancel it on cleanup)
        self._session_launched_by_us = False
        
        # Try to import stagehand if available
        try:
            from stagehand import Stagehand, StagehandConfig
            self._Stagehand = Stagehand
            self._StagehandConfig = StagehandConfig
            self._has_stagehand = True
            self._stagehand_instance = None
            self._page = None
        except ImportError:
            self._Stagehand = None
            self._StagehandConfig = None
            self._has_stagehand = False
            self._stagehand_instance = None
            self._page = None
    
    def __repr__(self) -> str:
        """String representation."""
        return super().__repr__()
    
    def is_available(self) -> bool:
        """Check if Stagehand SDK is installed."""
        return self._has_stagehand
    
    def _extract_session_id_from_url(self, url: str) -> Optional[str]:
        """Extract Browserbase session ID from WebSocket URL if possible."""
        # Try to extract session ID from URL patterns
        # This is a best-effort extraction
        match = re.search(r'session[_-]?id=([a-f0-9\-]+)', url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    async def init(self) -> None:
        """
        Initialize the browser client and connect to the session.
        
        This must be called before accessing the page object.
        """
        if not self._has_stagehand:
            raise ImportError(
                "Browser automation SDK (Stagehand) is not installed. Install it with: pip install stagehand"
            )
        
        # Determine session ID to use; if missing, launch via adapter/provider
        session_id = self.browserbase_session_id
        if not session_id and self.session_url:
            session_id = self._extract_session_id_from_url(self.session_url)
        
        if not session_id:
            # Attempt to launch a new provider session if adapter/provider provided
            if self._adapter is None and self._provider:
                self._adapter = get_adapter(
                    runtime_kind=RuntimeKind.BROWSER,
                    provider=self._provider,
                    config={**self._provider_config},
                )
            if self._adapter is not None:
                # Start with any provider config given by user
                launch_opts: dict[str, Any] = {**(self._provider_config or {})}
                # Ensure region default
                launch_opts.setdefault("region", os.getenv("BROWSERBASE_REGION", "sfo"))
                # Ensure Browserbase project id is set
                if self._browser_project_id:
                    launch_opts.setdefault("projectId", self._browser_project_id)
                # Sensible defaults for recording + playback longevity
                launch_opts.setdefault("keepAlive", True)
                launch_opts.setdefault("timeoutSec", 600)
                # Merge/ensure browserSettings defaults
                bs = launch_opts.get("browserSettings") or {}
                bs.setdefault("recordSession", True)
                launch_opts["browserSettings"] = bs

                result = await self._adapter.launch(options=launch_opts)
                session_id = result.get("session_id")
                # Capture provider connect URL when available for direct connection
                # Prioritize session_url from result, but also check selenium_url as fallback
                connect_url = result.get("session_url") or result.get("selenium_url")
                if connect_url:
                    self.session_url = connect_url
                # Persist for external access
                self.browserbase_session_id = session_id
                # Mark that we launched this session, so we know to cancel it on cleanup
                self._session_launched_by_us = True
                
                # Small delay to ensure session is ready for connection
                # Browserbase sessions may take a moment to become available
                if connect_url:
                    await asyncio.sleep(1)
        
        if not session_id:
            raise ValueError(
                "Either browserbase_session_id or a session_url with extractable session ID is required"
            )
        
        # Enable LiteLLM debug mode if requested via environment variable
        # Stagehand uses LiteLLM internally, so this helps debug LLM-related issues
        if os.getenv("LITELLM_DEBUG", "").lower() in ("true", "1", "yes"):
            try:
                import litellm
                if hasattr(litellm, 'set_verbose'):
                    litellm.set_verbose = True
                elif hasattr(litellm, '_turn_on_debug'):
                    litellm._turn_on_debug()
                logger.info("LiteLLM debug mode enabled via LITELLM_DEBUG environment variable")
            except ImportError:
                pass  # litellm not available, skip
            except Exception as e:
                logger.warning(f"Failed to enable LiteLLM debug mode: {e}")
        
        # Create Stagehand config (connect to existing session; we pass our model)
        # Ensure model_name is a string (not enum) - use .value if it's an enum
        model_name_str = self.model_name.value if hasattr(self.model_name, 'value') else str(self.model_name)
        
        # Determine if we should use API mode or direct connection
        # Use API mode if we don't have a connect URL - Stagehand will fetch it via Browserbase API
        use_api_mode = not bool(self.session_url)
        
        config_params = {
            "env": "BROWSERBASE",
            "browserbase_session_id": session_id,
            "use_api": use_api_mode,
            "model_name": model_name_str,
        }
        
        # If we have a direct Browserbase connect URL, pass it through to Stagehand
        # This allows Stagehand to connect directly via WebSocket without API calls
        if self.session_url:
            config_params["browserbase_connect_url"] = self.session_url
        # Only include model_api_key if explicitly provided; otherwise Stagehand will read from env
        if self.model_api_key:
            config_params["model_api_key"] = self.model_api_key

        # Provide sane defaults for OpenAI O-series Computer Use models
        # These models only support temperature=1; also instruct LiteLLM to drop unsupported params
        default_client_opts: dict[str, Any] = {}
        if isinstance(model_name_str, str) and model_name_str in {"o4", "o4-mini", "openai/o4", "openai/o4-mini"}:
            default_client_opts = {"temperature": 1, "drop_params": True}

        # Merge client options with defaults (user-provided options take precedence)
        merged_client_opts = {**default_client_opts, **(self.model_client_options or {})}
        if merged_client_opts:
            config_params["model_client_options"] = merged_client_opts
        
        # Merge with any additional options
        config_params.update(self._options)
        
        config = self._StagehandConfig(**config_params)
        
        # Initialize Stagehand
        self._stagehand_instance = self._Stagehand(config=config)
        await self._stagehand_instance.init()
        
        # Get the page object
        self._page = self._stagehand_instance.page
    
    @property
    def page(self):
        """
        Get the browser page object.
        
        Note: You must call init() first before accessing this property.
        """
        if not self._stagehand_instance:
            raise RuntimeError(
                "BrowserClient not initialized. Call await browser.init() first."
            )
        return self._page
    
    async def close(self) -> None:
        """
        Close the browser session and clean up resources.
        
        This method:
        1. Closes the Stagehand instance
        2. Cancels the Browserbase session if we launched it
        3. Closes the adapter connection
        """
        # Close Stagehand instance first
        if self._stagehand_instance:
            try:
                await self._stagehand_instance.close()
            except Exception as e:
                # Log but don't fail on Stagehand close errors
                logger = logging.getLogger(__name__)
                logger.warning(f"Error closing Stagehand instance: {e}")
            finally:
                self._stagehand_instance = None
                self._page = None
        
        # Cancel Browserbase session if we launched it ourselves
        if self._session_launched_by_us and self.browserbase_session_id and self._adapter:
            try:
                await self._adapter.cancel(self.browserbase_session_id)
            except Exception as e:
                # Log but don't fail on cancel errors (session might already be closed)
                logger = logging.getLogger(__name__)
                logger.warning(f"Error canceling Browserbase session {self.browserbase_session_id}: {e}")
        
        # Close adapter connection
        if self._adapter:
            try:
                await self._adapter.close()
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"Error closing adapter: {e}")
        
        # Call parent cleanup
        await super().close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.init()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - ensures cleanup on exit or error."""
        await self.close()
        return False  # Don't suppress exceptions

