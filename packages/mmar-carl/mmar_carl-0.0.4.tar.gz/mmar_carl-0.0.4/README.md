# MMAR CARL - Collaborative Agent Reasoning Library

A Python library for building chain-of-thought reasoning systems with DAG-based parallel execution and mmar-llm integration.

## Overview

CARL provides a structured framework for creating complex reasoning chains that can execute steps in parallel where dependencies allow. It's designed to work seamlessly with the `mmar-llm` library for production LLM integration and supports multi-language reasoning (Russian/English).

## Key Features

- **DAG-based Execution**: Automatically parallelizes reasoning steps based on dependencies
- **mmar-llm Integration**: Seamless integration with mmar-llm EntrypointsAccessor
- **Multi-language Support**: Built-in support for Russian and English languages
- **Clean Architecture**: No dirty patterns - uses proper dependency injection
- **Production Ready**: Async/sync compatibility, error handling, and retry logic
- **Parallel Processing**: Optimized execution with configurable worker pools
- **Financial Focus**: Designed for financial analysis with specialized prompts

## Quick Start

```python
import asyncio
from mmar_carl import (
    ReasoningChain, StepDescription, ReasoningContext,
    LLMClient, Language
)
from mmar_llm import EntrypointsAccessor, EntrypointsConfig

# Define a reasoning chain
EBITDA_ANALYSIS = [
    StepDescription(
        number=1,
        title="Рост EBITDA и стабильность",
        aim="Выяснить, стабильно ли растет EBITDA и насколько выросла",
        reasoning_questions="Насколько изменилась (выросла/уменьшилась) EBITDA за рассматриваемый период?",
        dependencies=[],
        entities=["EBITDA"],
        stage_action="Рассчитать темп прироста EBITDA за 12 последних месяцев год к году",
        example_reasoning="1) если темп > 0%, то положительный сигнал; если темп < 0%, то отрицательный сигнал"
    ),
    StepDescription(
        number=2,
        title="Маржинальность EBITDA",
        aim="Выяснить, сколько процентов выручки забирают операционные расходы",
        reasoning_questions="Какая маржинальность по EBITDA за рассматриваемый период?",
        dependencies=[1],  # Depends on step 1
        entities=["EBITDA_MARGIN", "EBITDA", "SALES_REVENUE"],
        stage_action="EBITDA маржа = EBITDA / SALES_REVENUE",
        example_reasoning="1) если маржа > 0%, то положительный сигнал: компания зарабатывает больше своих операционных расходов"
    )
]

# Create LLM client with mmar-llm integration
def create_llm_client(entrypoints_path: str, entrypoint_key: str = "default"):
    """Create LLM client with EntrypointsAccessor from configuration file."""
    import json
    with open(entrypoints_path, encoding="utf-8") as f:
        config_data = json.load(f)

    entrypoints_config = EntrypointsConfig.model_validate(config_data)
    entrypoints = EntrypointsAccessor(entrypoints_config)
    return LLMClient(entrypoints, entrypoint_key)

# Create and execute the reasoning chain
llm_client = create_llm_client("entrypoints.json", "my_entrypoint")
chain = ReasoningChain(
    steps=EBITDA_ANALYSIS,
    max_workers=2,
    enable_progress=True
)

context = ReasoningContext(
    outer_context="Период,EBITDA,SALES_REVENUE\n2023-Q1,1000000,5000000\n2023-Q2,1200000,5500000",
    llm_client=llm_client,
    language=Language.RUSSIAN,
    retry_max=3
)

result = chain.execute(context)
print(result.get_final_output())
```

## Installation

```bash
# For production use
pip install mmar-carl

# For development with mmar-llm integration
pip install mmar-carl mmar-llm>=1.0.3

# Development version with all dependencies
pip install mmar-carl[dev]
```

## Requirements

- Python 3.12+
- mmar-llm>=1.0.3 (for LLM integration)
- Pydantic for data models
- asyncio for parallel execution

## Documentation

- **Quick Start**: [docs/quickstart.md](docs/quickstart.md) - Get up and running quickly
- **Examples**: [docs/examples.md](docs/examples.md) - Real-world usage examples
- **Advanced Usage**: [docs/advanced.md](docs/advanced.md) - Advanced features and optimization
- **Methodology**: [docs/methodology.md](docs/methodology.md) - Development methodology (in Russian)

## Architecture

CARL is built around several key components:

- **StepDescription**: Defines individual reasoning steps with metadata and dependencies
- **ReasoningChain**: Orchestrates the execution of reasoning steps with DAG optimization
- **DAGExecutor**: Handles parallel execution based on dependencies with configurable workers
- **ReasoningContext**: Manages execution state, history, and multi-language support
- **LLMClient**: Clean integration with mmar-llm EntrypointsAccessor (no ContextVar patterns)
- **Language**: Built-in support for Russian and English languages
- **PromptTemplate**: Multi-language prompt templates for different analysis types

## Key Concepts

### DAG-Based Parallel Execution

CARL automatically analyzes step dependencies and creates execution batches for maximum parallelization:

```python
# Steps 1 and 2 execute in parallel
StepDescription(number=1, title="Revenue Analysis", dependencies=[])
StepDescription(number=2, title="Cost Analysis", dependencies=[])
# Step 3 waits for both to complete
StepDescription(number=3, title="Profitability Analysis", dependencies=[1, 2])
```

### Multi-language Support

Built-in support for Russian and English with appropriate prompt templates:

```python
# Russian language reasoning
context = ReasoningContext(
    outer_context=data,
    llm_client=llm_client,
    language=Language.RUSSIAN
)

# English language reasoning
context = ReasoningContext(
    outer_context=data,
    llm_client=llm_client,
    language=Language.ENGLISH
)
```

### Clean mmar-llm Integration

No dirty patterns - uses proper dependency injection:

```python
from carl import LLMClient
from mmar_llm import EntrypointsAccessor

# Clean constructor pattern
llm_client = LLMClient(entrypoints, entrypoint_key)
```

## Example Usage

See the [example.py](example.py) file for a complete end-to-end demonstration with:

- Real mmar-llm integration
- Multi-language support (Russian/English)
- Parallel execution demonstration
- Error handling and retry logic
- Performance metrics

Run it with:

```bash
# Set entrypoints configuration
export ENTRYPOINTS_PATH=/path/to/your/entrypoints.json

# Run the demonstration
python example.py entrypoints.json my_entrypoint_key
```

## License

MIT License - see LICENSE file for details.
