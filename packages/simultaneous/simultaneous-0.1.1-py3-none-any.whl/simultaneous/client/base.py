"""Base client interface for all Simultaneous clients.

This module defines the base structure that all clients (BrowserClient, ContainerClient,
CodeInterpreterClient) must follow. It ensures consistency across the SDK while allowing
flexibility for provider-specific implementations.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from simultaneous.client.llms import Models

logger = logging.getLogger(__name__)


class BaseClient(ABC):
    """
    Base class for all Simultaneous clients.
    
    This abstract base class defines the common interface and structure that all clients
    must implement. It ensures consistency while allowing flexibility for provider-specific
    implementations.
    
    All clients are AI-first and require model configuration for agentic features.
    """
    
    def __init__(
        self,
        *,
        session_url: Optional[str] = None,
        # Provider/adapter configuration (optional; enables self-launch)
        adapter: Any | None = None,  # ProviderAdapter type, but avoiding circular import
        provider: str | None = None,
        provider_config: dict | None = None,
        api_key: Optional[str] = None,
        # Agentic configuration (required for AI-first SDK)
        model_api_key: Optional[str] = None,
        model_name: str | Models,
        model_client_options: dict | None = None,
        **kwargs: Any,
    ):
        """
        Initialize BaseClient.
        
        Args:
            session_url: Session URL from provider (optional)
            adapter: Provider adapter instance (optional)
            provider: Provider name (e.g., "browserbase", "e2b") (optional)
            provider_config: Provider configuration (optional)
            api_key: Provider API key (optional)
            model_api_key: Model API key used by agentic features (required)
            model_name: Model identifier (e.g., "gpt-4o", "claude-3.5") (required)
            model_client_options: Extra client options (e.g., base_url, headers) (optional)
            **kwargs: Additional options for subclasses
        """
        self.session_url = session_url
        self.api_key = api_key
        self._options = kwargs
        
        # Provider/adapter configuration
        self._adapter = adapter
        self._provider = provider
        self._provider_config = provider_config or {}
        
        # Agentic configuration (required for AI-first SDK)
        # Convert enum to string using .value property to ensure we get the actual string value
        if isinstance(model_name, Models):
            self.model_name = model_name.value
        elif hasattr(model_name, 'value'):  # Handle other enum-like objects
            self.model_name = model_name.value
        else:
            self.model_name = str(model_name)
        self.model_api_key = model_api_key
        self.model_client_options = model_client_options or {}
        
        # Agentic wrapper (created in init() by subclasses)
        self._agentic_wrapper: Any | None = None
    
    @abstractmethod
    async def init(self) -> None:
        """
        Initialize the client and connect to the provider session.
        
        This must be called before using any client methods. Subclasses should:
        1. Connect to or create a provider session
        2. Initialize the underlying SDK
        3. Create and initialize the agentic wrapper
        
        Raises:
            RuntimeError: If initialization fails
            ImportError: If required SDK is not installed
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """
        Close the client session and clean up resources.
        
        Subclasses should:
        1. Close the underlying SDK connection
        2. Clean up the agentic wrapper
        3. Release any resources
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the underlying SDK is installed and available.
        
        Returns:
            True if SDK is available, False otherwise
        """
        pass
    
    def __repr__(self) -> str:
        """String representation."""
        class_name = self.__class__.__name__
        session_display = (
            f"session_url={self.session_url[:30]}..." 
            if self.session_url 
            else "session_url=None"
        )
        return f"{class_name}({session_display})"
    
    def has_agentic(self) -> bool:
        """
        Check if agentic features are available.
        
        Returns:
            True if agentic wrapper is initialized, False otherwise
        """
        return self._agentic_wrapper is not None
    
    async def act(self, instruction: str, context: dict[str, Any] | None = None) -> Any:
        """
        Execute a natural language instruction using agentic wrapper.
        
        This is the primary AI-first interface for all clients. Subclasses may override
        this to add provider-specific behavior, but should call super().act() if they
        want to use the default agentic wrapper.
        
        Args:
            instruction: Natural language instruction
            context: Optional context dictionary
            
        Returns:
            Result from the operation
            
        Raises:
            RuntimeError: If client is not initialized or agentic wrapper is not available
        """
        if not self._agentic_wrapper:
            raise RuntimeError(
                f"{self.__class__.__name__} not initialized. "
                f"Call await {self.__class__.__name__.lower()}.init() first."
            )
        
        return await self._agentic_wrapper.act(instruction, context)
    
    def _create_agentic_wrapper(
        self,
        sdk_instance: Any,
        wrapper_class: type,
    ) -> None:
        """
        Helper method to create and initialize agentic wrapper.
        
        Subclasses should call this in their init() method after creating the SDK instance.
        
        Args:
            sdk_instance: Instance of the provider SDK
            wrapper_class: Agentic wrapper class (e.g., E2BAgenticWrapper)
            
        Raises:
            RuntimeError: If agentic wrapper creation fails
        """
        try:
            self._agentic_wrapper = wrapper_class(
                sdk_instance=sdk_instance,
                model_name=self.model_name,
                model_api_key=self.model_api_key,
                model_client_options=self.model_client_options,
            )
        except ImportError as e:
            logger.error(f"Failed to initialize agentic wrapper: {e}")
            raise RuntimeError(
                "Agentic features require litellm. Install it with: pip install litellm"
            ) from e
        except Exception as e:
            logger.error(f"Failed to create agentic wrapper: {e}")
            raise RuntimeError(
                f"Failed to initialize agentic wrapper: {e}"
            ) from e

