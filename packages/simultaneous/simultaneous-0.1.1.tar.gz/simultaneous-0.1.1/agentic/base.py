"""Base agentic wrapper for adding AI capabilities to raw provider SDKs."""

import asyncio
import inspect
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

try:
    from litellm import acompletion
    import litellm
    HAS_LITELLM = True
except ImportError:
    HAS_LITELLM = False
    litellm = None
    acompletion = None

logger = logging.getLogger(__name__)


class BaseAgenticWrapper(ABC):
    """
    Base class for adding AI capabilities to raw provider SDKs.
    
    This wrapper uses litellm to translate natural language instructions
    into SDK operations, similar to how Stagehand adds AI to Playwright.
    
    Subclasses should implement provider-specific operation translation.
    """
    
    def __init__(
        self,
        sdk_instance: Any,
        model_name: str,
        model_api_key: Optional[str] = None,
        model_client_options: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize agentic wrapper.
        
        Args:
            sdk_instance: Instance of the provider SDK (e.g., E2B Sandbox)
            model_name: LLM model identifier (e.g., "gpt-4o", "claude-3.5")
            model_api_key: API key for the LLM (optional, reads from env if not provided)
            model_client_options: Additional client options (base_url, headers, etc.)
        """
        if not HAS_LITELLM:
            raise ImportError(
                "litellm is not installed. Install it with: pip install litellm"
            )
        
        # Enable LiteLLM debug mode if requested via environment variable
        import os
        if os.getenv("LITELLM_DEBUG", "").lower() in ("true", "1", "yes"):
            try:
                if hasattr(litellm, 'set_verbose'):
                    litellm.set_verbose = True
                elif hasattr(litellm, '_turn_on_debug'):
                    litellm._turn_on_debug()
                logger.info("LiteLLM debug mode enabled via LITELLM_DEBUG environment variable")
            except Exception as e:
                logger.warning(f"Failed to enable LiteLLM debug mode: {e}")
        
        self.sdk_instance = sdk_instance
        self.model_name = model_name
        self.model_api_key = model_api_key
        self.model_client_options = model_client_options or {}
        
        # Conversation context for multi-step operations
        self._conversation_context: list[dict[str, Any]] = []
        
        # Cache of available operations (introspected from SDK)
        self._available_operations: Optional[dict[str, Any]] = None
    
    @abstractmethod
    def _get_available_operations(self) -> dict[str, Any]:
        """
        Introspect SDK instance to discover available operations.
        
        Returns:
            Dictionary mapping operation names to their signatures/descriptions
        """
        pass
    
    @abstractmethod
    async def _execute_operation(self, operation: dict[str, Any]) -> Any:
        """
        Execute a generated operation on the SDK instance.
        
        Args:
            operation: Operation dictionary with method name, args, kwargs
            
        Returns:
            Result from SDK operation
        """
        pass
    
    async def _generate_operation(
        self,
        instruction: str,
        available_operations: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Use LLM to translate natural language instruction into SDK operation.
        
        Args:
            instruction: Natural language instruction
            available_operations: Dictionary of available SDK operations
            context: Optional context dictionary for the operation
            
        Returns:
            Operation dictionary with method name, args, kwargs
        """
        # Build prompt for LLM
        system_prompt = self._build_system_prompt(available_operations)
        user_prompt = self._build_user_prompt(instruction, context)
        
        # Add conversation history
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        # Add conversation context if available
        if self._conversation_context:
            messages.extend(self._conversation_context[-5:])  # Last 5 messages
        
        messages.append({"role": "user", "content": user_prompt})
        
        # Call LLM via litellm
        try:
            response = await acompletion(
                model=self.model_name,
                messages=messages,
                api_key=self.model_api_key,
                **self.model_client_options,
            )
            
            # Extract operation from response
            operation = self._parse_llm_response(response)
            
            # Add to conversation context
            self._conversation_context.append({
                "role": "user",
                "content": instruction,
            })
            self._conversation_context.append({
                "role": "assistant",
                "content": str(operation),
            })
            
            return operation
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to generate operation with model {self.model_name}: {error_msg}")
            
            # Provide helpful error message with debug hint
            if "LiteLLM" in error_msg or "litellm" in error_msg.lower() or "debug" in error_msg.lower():
                logger.info(
                    "💡 To enable LiteLLM debug mode for more detailed error information, "
                    "set LITELLM_DEBUG=true environment variable before running your script"
                )
            
            raise
    
    def _build_system_prompt(self, available_operations: dict[str, Any]) -> str:
        """Build system prompt describing available SDK operations."""
        operations_desc = "\n".join(
            f"- {name}: {desc}" for name, desc in available_operations.items()
        )
        
        return f"""You are an AI assistant that translates natural language instructions into SDK operations.

Available SDK operations:
{operations_desc}

Respond with a JSON object containing:
- "method": The method name to call
- "args": List of positional arguments (if any)
- "kwargs": Dictionary of keyword arguments (if any)

Be precise and only use the available operations. If the instruction requires multiple steps, break it down into a single operation that can be executed, or return the first step."""
    
    def _build_user_prompt(
        self,
        instruction: str,
        context: Optional[dict[str, Any]] = None,
    ) -> str:
        """Build user prompt with instruction and context."""
        prompt = f"Instruction: {instruction}\n\n"
        
        if context:
            prompt += f"Context: {context}\n\n"
        
        prompt += "Generate the SDK operation to execute this instruction."
        
        return prompt
    
    def _parse_llm_response(self, response: Any) -> dict[str, Any]:
        """Parse LLM response into operation dictionary."""
        import json
        
        # Extract content from litellm response
        content = response.choices[0].message.content if hasattr(response, "choices") else str(response)
        
        # Try to parse JSON from response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            operation = json.loads(content)
            
            # Validate operation structure
            if not isinstance(operation, dict):
                raise ValueError("Operation must be a dictionary")
            
            if "method" not in operation:
                raise ValueError("Operation must contain 'method' field")
            
            return {
                "method": operation["method"],
                "args": operation.get("args", []),
                "kwargs": operation.get("kwargs", {}),
            }
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse LLM response: {e}\nResponse: {content}")
            raise ValueError(f"Invalid operation format from LLM: {e}")
    
    async def act(
        self,
        natural_language_instruction: str,
        context: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Execute a natural language instruction by translating it to SDK operations.
        
        Args:
            natural_language_instruction: Natural language instruction
            context: Optional context dictionary
            
        Returns:
            Result from SDK operation
        """
        # Get available operations (cached after first call)
        if self._available_operations is None:
            self._available_operations = self._get_available_operations()
        
        # Generate operation from natural language
        operation = await self._generate_operation(
            natural_language_instruction,
            self._available_operations,
            context,
        )
        
        # Execute operation
        result = await self._execute_operation(operation)
        
        return result
    
    def clear_context(self) -> None:
        """Clear conversation context."""
        self._conversation_context.clear()

