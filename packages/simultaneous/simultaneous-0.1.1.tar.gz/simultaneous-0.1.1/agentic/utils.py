"""Utilities for agentic SDK wrappers."""

import inspect
from typing import Any, Callable


def introspect_sdk_methods(sdk_instance: Any) -> dict[str, dict[str, Any]]:
    """
    Introspect SDK instance to discover available methods.
    
    Args:
        sdk_instance: SDK instance to introspect
        
    Returns:
        Dictionary mapping method names to their signatures
    """
    methods = {}
    
    for name in dir(sdk_instance):
        if name.startswith("_"):
            continue
        
        attr = getattr(sdk_instance, name)
        
        if callable(attr):
            try:
                sig = inspect.signature(attr)
                methods[name] = {
                    "signature": str(sig),
                    "is_async": inspect.iscoroutinefunction(attr),
                }
            except (ValueError, TypeError):
                # Skip if signature can't be inspected
                pass
    
    return methods


def build_operation_prompt(
    instruction: str,
    available_methods: dict[str, dict[str, Any]],
    context: dict[str, Any] | None = None,
) -> str:
    """
    Build prompt for LLM to generate SDK operation.
    
    Args:
        instruction: Natural language instruction
        available_methods: Dictionary of available SDK methods
        context: Optional context dictionary
        
    Returns:
        Formatted prompt string
    """
    prompt_parts = [f"Instruction: {instruction}\n"]
    
    if context:
        prompt_parts.append(f"Context: {context}\n")
    
    prompt_parts.append("\nAvailable SDK methods:")
    for method_name, method_info in available_methods.items():
        sig = method_info.get("signature", "")
        is_async = method_info.get("is_async", False)
        async_marker = " (async)" if is_async else ""
        prompt_parts.append(f"- {method_name}{async_marker}: {sig}")
    
    prompt_parts.append(
        "\nGenerate a JSON object with 'method', 'args', and 'kwargs' fields."
    )
    
    return "\n".join(prompt_parts)

