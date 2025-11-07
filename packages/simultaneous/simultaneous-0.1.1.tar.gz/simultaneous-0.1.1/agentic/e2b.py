"""E2B-specific agentic wrapper for adding AI capabilities to E2B Sandbox SDK."""

import asyncio
import inspect
import logging
from typing import Any, Optional

from simultaneous.agentic.base import BaseAgenticWrapper

logger = logging.getLogger(__name__)


class E2BAgenticWrapper(BaseAgenticWrapper):
    """
    Agentic wrapper for E2B Sandbox SDK.
    
    Translates natural language instructions into E2B SDK operations
    using litellm, enabling AI-powered code execution and file operations.
    """
    
    def _get_available_operations(self) -> dict[str, Any]:
        """
        Introspect E2B Sandbox instance to discover available operations.
        
        Returns:
            Dictionary mapping operation names to descriptions
        """
        operations = {}
        sandbox = self.sdk_instance
        
        # Introspect sandbox methods
        if hasattr(sandbox, "files"):
            files_api = sandbox.files
            if hasattr(files_api, "write"):
                operations["files.write"] = "Write content to a file path"
            if hasattr(files_api, "read"):
                operations["files.read"] = "Read content from a file path"
            if hasattr(files_api, "list"):
                operations["files.list"] = "List files in a directory path"
            if hasattr(files_api, "remove"):
                operations["files.remove"] = "Remove a file or directory"
        
        if hasattr(sandbox, "process"):
            process_api = sandbox.process
            if hasattr(process_api, "start"):
                operations["process.start"] = "Start a process with a command"
            if hasattr(process_api, "list"):
                operations["process.list"] = "List running processes"
        
        if hasattr(sandbox, "run"):
            operations["run"] = "Execute a shell command synchronously"
        
        # Add code execution helper
        operations["execute_code"] = "Execute Python code (auto-generates temp file and runs)"
        
        return operations
    
    async def _execute_operation(self, operation: dict[str, Any]) -> Any:
        """
        Execute a generated operation on the E2B Sandbox instance.
        
        Args:
            operation: Operation dictionary with method name, args, kwargs
            
        Returns:
            Result from SDK operation
        """
        method_path = operation["method"]
        args = operation.get("args", [])
        kwargs = operation.get("kwargs", {})
        
        sandbox = self.sdk_instance
        
        # Handle special "execute_code" operation
        if method_path == "execute_code":
            return await self._execute_code_operation(args, kwargs)
        
        # Handle nested method paths (e.g., "files.write")
        if "." in method_path:
            parts = method_path.split(".")
            obj = sandbox
            for part in parts[:-1]:
                if not hasattr(obj, part):
                    raise AttributeError(f"SDK instance has no attribute '{part}'")
                obj = getattr(obj, part)
            method_name = parts[-1]
            method = getattr(obj, method_name)
        else:
            method = getattr(sandbox, method_path)
        
        # Execute method (handle both sync and async)
        if inspect.iscoroutinefunction(method):
            result = await method(*args, **kwargs)
        else:
            # Run sync method in thread pool
            result = await asyncio.to_thread(method, *args, **kwargs)
        
        return result
    
    async def _execute_code_operation(self, args: list, kwargs: dict) -> Any:
        """
        Execute Python code operation (helper for code execution).
        
        Args:
            args: Arguments (should contain code string)
            kwargs: Keyword arguments (may contain language, timeout)
            
        Returns:
            Execution result
        """
        if not args:
            raise ValueError("execute_code requires code string as argument")
        
        code = args[0]
        language = kwargs.get("language", "python")
        timeout = kwargs.get("timeout", None)
        
        sandbox = self.sdk_instance
        
        if language == "python":
            # Create temp file and execute
            import tempfile
            import uuid
            
            temp_file = f"/tmp/e2b_code_{uuid.uuid4().hex[:8]}.py"
            
            # Write code to temp file
            if hasattr(sandbox, "files"):
                await asyncio.to_thread(
                    sandbox.files.write,
                    temp_file,
                    code,
                )
            else:
                raise AttributeError("Sandbox has no 'files' attribute")
            
            # Execute Python file
            if hasattr(sandbox, "process"):
                process = await asyncio.to_thread(
                    sandbox.process.start,
                    cmd=f"python {temp_file}",
                    timeout=timeout,
                )
                await asyncio.to_thread(process.wait)
                
                stdout = process.stdout if hasattr(process, "stdout") else ""
                stderr = process.stderr if hasattr(process, "stderr") else ""
                exit_code = process.exit_code if hasattr(process, "exit_code") else 0
                
                return {
                    "stdout": stdout,
                    "stderr": stderr,
                    "exit_code": exit_code,
                }
            else:
                raise AttributeError("Sandbox has no 'process' attribute")
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    async def execute_natural(self, instruction: str) -> dict[str, Any]:
        """
        Execute natural language instruction as code execution.
        
        Args:
            instruction: Natural language instruction for code execution
            
        Returns:
            Execution result with stdout, stderr, exit_code
        """
        # Enhance instruction with code execution context
        enhanced_instruction = f"Execute Python code to: {instruction}"
        
        result = await self.act(enhanced_instruction)
        
        # Normalize result format
        if isinstance(result, dict):
            return result
        else:
            return {
                "stdout": str(result),
                "stderr": "",
                "exit_code": 0,
            }
    
    async def file_operation_natural(self, instruction: str) -> Any:
        """
        Execute natural language instruction as file operation.
        
        Args:
            instruction: Natural language instruction for file operation
            
        Returns:
            Result from file operation
        """
        # Enhance instruction with file operation context
        enhanced_instruction = f"Perform file operation: {instruction}"
        
        return await self.act(enhanced_instruction)

