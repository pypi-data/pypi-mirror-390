"""
MAESTRO CARL (Collaborative Agent Reasoning Library)

A library for building chain-of-thought reasoning systems with DAG-based parallel execution.
"""

from .chain import ChainBuilder, ReasoningChain
from .executor import DAGExecutor
from .llm import LLMClient, LLMClientBase
from .models import Language, PromptTemplate, ReasoningContext, ReasoningResult, StepDescription, StepExecutionResult

__version__ = "0.0.3"
__all__ = [
    "Language",
    "StepDescription",
    "ReasoningContext",
    "StepExecutionResult",
    "ReasoningResult",
    "PromptTemplate",
    "ReasoningChain",
    "ChainBuilder",
    "DAGExecutor",
    "LLMClientBase",
    "LLMClient",
]
