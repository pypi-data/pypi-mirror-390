"""
LLM client implementations for CARL using mmar-llm library.

Provides integration with mmar-llm library for production use.
"""

from mmar_llm import EntrypointsAccessor

from .models import LLMClientBase


class LLMClient(LLMClientBase):
    """
    LLM client implementation using mmar-llm library.

    Integrates with the mmar-llm EntrypointsAccessor for LLM calls.
    """

    def __init__(self, entrypoints: EntrypointsAccessor, entrypoint_key: str):
        if not entrypoint_key:
            raise ValueError("entrypoint_key is required and cannot be empty")

        self.entrypoints = entrypoints
        self.entrypoint_key = entrypoint_key

    async def get_response(self, prompt: str) -> str:
        # Get the specific entrypoint
        ep = self.entrypoints[self.entrypoint_key]

        # Check if the method is async or sync
        result = ep.get_response_with_retries(prompt, retries=1)

        # If the result is a coroutine (async), await it
        if hasattr(result, "__await__") or hasattr(result, "__aiter__"):
            return await result
        else:
            # If it's already a string, return it directly
            return result

    async def get_response_with_retries(self, prompt: str, retries: int = 3) -> str:
        ep = self.entrypoints[self.entrypoint_key]

        # Use mmar-llm's built-in retry functionality
        result = ep.get_response_with_retries(prompt, retries=retries)

        # If the result is a coroutine (async), await it
        if hasattr(result, "__await__") or hasattr(result, "__aiter__"):
            return await result
        else:
            # If it's already a string, return it directly
            return result
