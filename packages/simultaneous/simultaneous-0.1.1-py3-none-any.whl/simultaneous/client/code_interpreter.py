"""Code interpreter clients for use in agent code.

This module provides code interpreter clients (like E2B Code Interpreter) that can be used
inside agent code to execute code in sandboxes with AI capabilities. These are different from providers
(like E2B) which provide the infrastructure/runtime.
"""

import logging
from typing import Any, Optional
import os
import asyncio
from simultaneous.runtime.base import RuntimeKind
from simultaneous.providers.base import ProviderAdapter
from simultaneous.providers.router import get_adapter
from simultaneous.client.llms import Models
from simultaneous.client.base import BaseClient

logger = logging.getLogger(__name__)


class CodeExecutionResult:
    """
    Result of code execution.
    
    Similar to the JavaScript Code Interpreter SDK's execution result.
    """
    
    def __init__(
        self,
        text: str,
        error: str | None = None,
        exit_code: int = 0,
        language: str = "python",
    ):
        """
        Initialize code execution result.
        
        Args:
            text: Standard output text
            error: Error output text (if any)
            exit_code: Exit code of the execution
            language: Programming language used
        """
        self.text = text
        self.error = error
        self.exit_code = exit_code
        self.language = language
    
    def __repr__(self) -> str:
        """String representation."""
        status = "✓" if self.exit_code == 0 else "✗"
        return f"CodeExecutionResult({status} text={self.text[:50]}...)"
    
    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.exit_code == 0 and self.error is None


class CodeInterpreterClient(BaseClient):
    """
    Code interpreter client for use in agent code.
    
    This client wraps code execution SDKs (like E2B) and provides a high-level API
    similar to the JavaScript Code Interpreter SDK. It can optionally use an agentic
    wrapper to add AI-powered natural language capabilities.
    
    Example:
        ```python
        from simultaneous import SimClient, Sandbox, CodeInterpreterClient
        
        client = SimClient()
        
        @client.agent(name="code-exec", runtime=Sandbox(provider="e2b"))
        async def code_exec():
            # CodeInterpreterClient with agentic capabilities
            interpreter = CodeInterpreterClient(
                session_url="mcp://...",
                model_name="gpt-4o",
                model_api_key="sk-...",
            )
            await interpreter.init()
            
            # High-level code execution API
            result = await interpreter.run_code("x = 1")
            result = await interpreter.run_code("x += 1; x")
            print(result.text)  # Outputs: 2
            
            # Agentic natural language execution
            result = await interpreter.execute_natural(
                "analyze the data in /tmp/data.csv and create a summary"
            )
            
            # Access underlying sandbox for advanced operations
            sandbox = interpreter.sandbox
            await sandbox.files.write("/tmp/file.txt", "content")
        ```
    
    Note:
        CodeInterpreterClient is a code execution client wrapper, not a provider. The provider
        (e.g., E2B via Simultaneous API) provides the session URL that
        CodeInterpreterClient connects to.
    """
    
    def __init__(
        self,
        *,
        e2b_sandbox_id: Optional[str] = None,
        session_url: Optional[str] = None,
        # Provider/adapter configuration (optional; enables self-launch)
        adapter: ProviderAdapter | None = None,
        provider: str | None = None,
        provider_config: dict | None = None,
        api_key: Optional[str] = None,
        template: str | None = None,
        # Agentic configuration (required for AI-first SDK)
        model_api_key: Optional[str] = None,
        model_name: str | Models,
        model_client_options: dict | None = None,
        **kwargs: Any,
    ):
        """
        Initialize CodeInterpreterClient.
        
        Args:
            e2b_sandbox_id: E2B sandbox ID (preferred)
            session_url: Container session URL (MCP endpoint from provider)
            api_key: E2B API key (optional, defaults to E2B_API_KEY env var)
            template: E2B template ID (defaults to "base")
            adapter: Provider adapter instance (optional)
            provider: Provider name (e.g., "e2b") (optional)
            provider_config: Provider configuration (optional)
            model_api_key: Model API key used by agentic features (required)
            model_name: Model identifier (e.g., "gpt-4o", "claude-3.5") (required)
            model_client_options: Extra client options (e.g., base_url, headers) (optional)
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
        
        # CodeInterpreter-specific attributes
        self.e2b_sandbox_id = e2b_sandbox_id
        self.template = template or os.getenv("E2B_TEMPLATE", "base")
        
        # Try to import e2b if available
        try:
            from e2b import Sandbox
            self._Sandbox = Sandbox
            self._has_e2b = True
            self._sandbox_instance = None
        except ImportError:
            self._Sandbox = None
            self._has_e2b = False
            self._sandbox_instance = None
    
    def __repr__(self) -> str:
        """String representation."""
        return super().__repr__()
    
    def is_available(self) -> bool:
        """Check if E2B SDK is installed."""
        return self._has_e2b
    
    async def init(self) -> None:
        """
        Initialize the code interpreter client and connect to the sandbox.
        
        This must be called before using run_code() or accessing the sandbox object.
        """
        if not self._has_e2b:
            raise ImportError(
                "Code interpreter SDK (E2B) is not installed. Install it with: pip install e2b"
            )
        
        # Determine sandbox ID to use; if missing, launch via adapter/provider
        sandbox_id = self.e2b_sandbox_id
        if not sandbox_id and self.session_url:
            # Try to extract sandbox ID from session URL if possible
            # E2B MCP URLs may contain sandbox ID
            pass
        
        if not sandbox_id:
            # Attempt to launch a new provider session if adapter/provider provided
            if self._adapter is None and self._provider:
                self._adapter = get_adapter(
                    runtime_kind=RuntimeKind.SANDBOX,
                    provider=self._provider,
                    config={**self._provider_config},
                )
            if self._adapter is not None:
                # Start with any provider config given by user
                launch_opts: dict[str, Any] = {**(self._provider_config or {})}
                # Ensure template default
                launch_opts.setdefault("template", self.template)

                result = await self._adapter.launch(options=launch_opts)
                sandbox_id = result.get("session_id")
                # Capture provider session URL when available for direct connection
                if result.get("session_url"):
                    self.session_url = result.get("session_url")
                # Persist for external access
                self.e2b_sandbox_id = sandbox_id
        
        if not sandbox_id:
            raise ValueError(
                "Either e2b_sandbox_id or a session_url with extractable sandbox ID is required"
            )
        
        # Set API key if provided
        if self.api_key and not os.getenv("E2B_API_KEY"):
            os.environ["E2B_API_KEY"] = self.api_key
        
        # Reconnect to existing sandbox using E2B SDK
        def reconnect_sandbox():
            """Reconnect to sandbox."""
            if hasattr(self._Sandbox, "reconnect"):
                return self._Sandbox.reconnect(sandbox_id=sandbox_id)
            else:
                raise RuntimeError(
                    "E2B SDK reconnect method not available. "
                    "The sandbox instance should be stored when creating it."
                )
        
        self._sandbox_instance = await asyncio.to_thread(reconnect_sandbox)
        
        # Initialize agentic wrapper using base class helper
        from simultaneous.agentic.e2b import E2BAgenticWrapper
        self._create_agentic_wrapper(self._sandbox_instance, E2BAgenticWrapper)
    
    async def run_code(
        self,
        code: str,
        language: str = "python",
        timeout: float | None = None,
    ) -> CodeExecutionResult:
        """
        Execute code in the sandbox and return structured results.
        
        This is the high-level API similar to the JavaScript Code Interpreter SDK.
        
        Args:
            code: Code to execute
            language: Programming language (default: "python")
            timeout: Execution timeout in seconds (optional)
            
        Returns:
            CodeExecutionResult with text output, errors, and metadata
            
        Example:
            ```python
            result = await interpreter.run_code("x = 1")
            result = await interpreter.run_code("x += 1; x")
            print(result.text)  # Outputs: 2
            ```
        """
        if not self._sandbox_instance:
            raise RuntimeError(
                "CodeInterpreterClient not initialized. Call await interpreter.init() first."
            )
        
        # Execute code via E2B SDK
        import asyncio
        import tempfile
        import uuid
        
        if language == "python":
            # For code with multiple lines or complex syntax, use a temp file
            if "\n" in code or ";" in code:
                # Create temp file and execute
                temp_file = f"/tmp/e2b_code_{uuid.uuid4().hex[:8]}.py"
                
                # Write code to temp file
                await asyncio.to_thread(
                    self._sandbox_instance.files.write,
                    temp_file,
                    code,
                )
                command = f"python {temp_file}"
            else:
                # Simple one-liner
                # Escape quotes for shell safety
                escaped_code = code.replace('"', '\\"').replace("'", "\\'")
                command = f'python -c "{escaped_code}"'
            
            # Execute command
            if hasattr(self._sandbox_instance, "process"):
                process = await asyncio.to_thread(
                    self._sandbox_instance.process.start,
                    cmd=command,
                    timeout=timeout,
                )
                await asyncio.to_thread(process.wait)
                
                stdout = process.stdout if hasattr(process, "stdout") else ""
                stderr = process.stderr if hasattr(process, "stderr") else ""
                exit_code = process.exit_code if hasattr(process, "exit_code") else 0
            else:
                # Fallback: use run() method if available
                result = await asyncio.to_thread(
                    self._sandbox_instance.run,
                    command,
                    timeout=timeout,
                )
                stdout = result.stdout if hasattr(result, "stdout") else str(result)
                stderr = result.stderr if hasattr(result, "stderr") else ""
                exit_code = result.exit_code if hasattr(result, "exit_code") else 0
            
            return CodeExecutionResult(
                text=stdout.strip(),
                error=stderr.strip() if exit_code != 0 else None,
                exit_code=exit_code,
                language=language,
            )
        else:
            # For other languages, use appropriate execution method
            if hasattr(self._sandbox_instance, "process"):
                process = await asyncio.to_thread(
                    self._sandbox_instance.process.start,
                    cmd=code,
                    timeout=timeout,
                )
                await asyncio.to_thread(process.wait)
                
                stdout = process.stdout if hasattr(process, "stdout") else ""
                stderr = process.stderr if hasattr(process, "stderr") else ""
                exit_code = process.exit_code if hasattr(process, "exit_code") else 0
            else:
                result = await asyncio.to_thread(
                    self._sandbox_instance.run,
                    code,
                    timeout=timeout,
                )
                stdout = result.stdout if hasattr(result, "stdout") else str(result)
                stderr = result.stderr if hasattr(result, "stderr") else ""
                exit_code = result.exit_code if hasattr(result, "exit_code") else 0
            
            return CodeExecutionResult(
                text=stdout.strip(),
                error=stderr.strip() if exit_code != 0 else None,
                exit_code=exit_code,
                language=language,
            )
    
    async def execute_natural(self, instruction: str) -> CodeExecutionResult:
        """
        Execute a natural language instruction using agentic wrapper.
        
        This is the primary AI-first interface for CodeInterpreterClient.
        
        Args:
            instruction: Natural language instruction for code execution
            
        Returns:
            CodeExecutionResult with execution output
            
        Example:
            ```python
            result = await interpreter.execute_natural(
                "analyze the data in /tmp/data.csv and create a summary"
            )
            ```
        """
        if not self._agentic_wrapper:
            raise RuntimeError(
                "CodeInterpreterClient not initialized. Call await interpreter.init() first."
            )
        
        result = await self._agentic_wrapper.execute_natural(instruction)
        
        # Convert to CodeExecutionResult
        return CodeExecutionResult(
            text=result.get("stdout", ""),
            error=result.get("stderr") if result.get("exit_code", 0) != 0 else None,
            exit_code=result.get("exit_code", 0),
            language="python",
        )
    
    async def act(self, instruction: str, context: dict[str, Any] | None = None) -> Any:
        """
        Execute a natural language instruction using agentic wrapper.
        
        This is a general-purpose agentic method that can handle various operations
        (code execution, file operations, etc.).
        
        Args:
            instruction: Natural language instruction
            context: Optional context dictionary
            
        Returns:
            Result from the operation
            
        Example:
            ```python
            result = await interpreter.act(
                "read the file /tmp/data.json and parse it"
            )
            ```
        """
        return await super().act(instruction, context)
    
    @property
    def sandbox(self):
        """
        Get the E2B sandbox object.
        
        This exposes the underlying E2B SDK Sandbox instance for advanced operations.
        
        Note: You must call init() first before accessing this property.
        """
        if not self._sandbox_instance:
            raise RuntimeError(
                "CodeInterpreterClient not initialized. Call await interpreter.init() first."
            )
        return self._sandbox_instance
    
    async def close(self) -> None:
        """Close the code interpreter session."""
        if self._sandbox_instance:
            await asyncio.to_thread(self._sandbox_instance.close)
            self._sandbox_instance = None
            self._agentic_wrapper = None
        await super().close()

