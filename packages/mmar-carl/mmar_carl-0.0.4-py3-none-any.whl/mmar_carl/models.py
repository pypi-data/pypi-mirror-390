"""
Core data models for CARL reasoning system.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Language(StrEnum):
    """Supported languages."""

    RUSSIAN = "ru"
    ENGLISH = "en"


class StepDescription(BaseModel):
    """
    Defines a single reasoning step in a chain.

    This model encapsulates all the metadata needed for a reasoning step,
    including its dependencies, objectives, and execution guidance.
    """

    number: int = Field(..., description="Step number in the sequence")
    title: str = Field(..., description="Human-readable title of the step")
    aim: str = Field(..., description="Primary objective of this step")
    reasoning_questions: str = Field(..., description="Key questions to answer")
    dependencies: list[int] = Field(default_factory=list, description="List of step numbers this step depends on")
    entities: list[str] = Field(default_factory=list, description="Entities/concepts this step works with")
    stage_action: str = Field(..., description="Specific action to perform")
    example_reasoning: str = Field(..., description="Example of expert reasoning")

    def depends_on(self, step_number: int) -> bool:
        """Check if this step depends on a given step number."""
        return step_number in self.dependencies

    def has_dependencies(self) -> bool:
        """Check if this step has any dependencies."""
        return len(self.dependencies) > 0


class ReasoningContext(BaseModel):
    """
    Context object that maintains state during reasoning execution.

    Contains the input data, entrypoints accessor, execution history, and configuration.
    """

    outer_context: str = Field(..., description="Input data as string (it can be CSV or other text information)")
    entrypoints: Any = Field(..., description="EntrypointsAccessor for LLM execution")
    entrypoint_key: str = Field(default="default", description="Key for the specific entrypoint to use")
    retry_max: int = Field(default=3, description="Maximum retry attempts")
    history: list[str] = Field(default_factory=list, description="Accumulated reasoning history")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata and state")
    language: Language = Field(default=Language.RUSSIAN, description="Language for reasoning prompts")

    def add_to_history(self, entry: str) -> None:
        """Add a new entry to the reasoning history."""
        self.history.append(entry)

    def get_current_history(self) -> str:
        """Get the current reasoning history as a single string."""
        return "\n".join(self.history)

    model_config = {"arbitrary_types_allowed": True}


class StepExecutionResult(BaseModel):
    """
    Result of executing a single reasoning step.
    """

    step_number: int = Field(..., description="Number of the executed step")
    step_title: str = Field(..., description="Title of the executed step")
    result: str = Field(..., description="Result content from LLM")
    success: bool = Field(..., description="Whether execution succeeded")
    error_message: str | None = Field(default=None, description="Error message if execution failed")
    execution_time: float | None = Field(default=None, description="Time taken for execution in seconds")
    updated_history: list[str] = Field(default_factory=list, description="History after this step's execution")


class ReasoningResult(BaseModel):
    """
    Final result of executing a complete reasoning chain.
    """

    success: bool = Field(..., description="Whether overall execution succeeded")
    history: list[str] = Field(..., description="Complete reasoning history")
    step_results: list[StepExecutionResult] = Field(..., description="Results from each step")
    total_execution_time: float | None = Field(default=None, description="Total execution time in seconds")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional result metadata")

    def get_final_output(self) -> str:
        """Get the final reasoning output as a single string."""
        return "\n".join(self.history)

    def get_successful_steps(self) -> list[StepExecutionResult]:
        """Get all successfully executed steps."""
        return [step for step in self.step_results if step.success]

    def get_failed_steps(self) -> list[StepExecutionResult]:
        """Get all failed steps."""
        return [step for step in self.step_results if not step.success]




class PromptTemplate(BaseModel):
    """
    Template for generating prompts from reasoning steps.
    """

    system_prompt: str | None = Field(default=None, description="System-level instructions")

    # Russian templates
    ru_step_template: str = Field(
        default="Шаг {step_number}. {step_title}\nЦель: {aim}\nЗадача: {stage_action}\nВопросы: {reasoning_questions}\nПример рассуждений: {example_reasoning}",
        description="Template for individual step prompts in Russian",
    )
    ru_chain_template: str = Field(
        default="Данные для анализа:\n{outer_context}\n{step_prompt}\nОтвечай кратко, подумай какие можно сделать выводы о результатах. Ответ должен состоять из одного параграфа. Не задавай дополнительных вопросов и не передавай инструкций. Пиши только текстом, без математических формул.",
        description="Template for complete chain prompts in Russian",
    )
    ru_history_template: str = Field(
        default="История предыдущих шагов:\n{history}\nОсновываясь на результатах предыдущих шагов, выполни следующую задачу:\n{current_task}",
        description="Template for including history in prompts in Russian",
    )

    # English templates
    en_step_template: str = Field(
        default="Step {step_number}. {step_title}\nObjective: {aim}\nTask: {stage_action}\nQuestions: {reasoning_questions}\nExample reasoning: {example_reasoning}",
        description="Template for individual step prompts in English",
    )
    en_chain_template: str = Field(
        default="Data for analysis:\n{outer_context}\n{step_prompt}\nRespond concisely, consider what conclusions can be drawn from the results. Response should be one paragraph. Do not ask additional questions or provide instructions. Write in text only, without mathematical formulas.",
        description="Template for complete chain prompts in English",
    )
    en_history_template: str = Field(
        default="History of previous steps:\n{history}\nBased on the results of previous steps, perform the following task:\n{current_task}",
        description="Template for including history in prompts in English",
    )

    def format_step_prompt(self, step: StepDescription, language: Language = Language.RUSSIAN) -> str:
        """Format a single step prompt."""
        if language == Language.ENGLISH:
            return self.en_step_template.format(
                step_number=step.number,
                step_title=step.title,
                aim=step.aim,
                stage_action=step.stage_action,
                reasoning_questions=step.reasoning_questions,
                example_reasoning=step.example_reasoning,
            )
        else:  # Russian
            return self.ru_step_template.format(
                step_number=step.number,
                step_title=step.title,
                aim=step.aim,
                stage_action=step.stage_action,
                reasoning_questions=step.reasoning_questions,
                example_reasoning=step.example_reasoning,
            )

    def format_chain_prompt(
        self, outer_context: str, current_task: str, history: str = "", language: Language = Language.RUSSIAN
    ) -> str:
        """Format a complete chain prompt."""
        if language == Language.ENGLISH:
            if history:
                current_task = self.en_history_template.format(history=history, current_task=current_task)

            return self.en_chain_template.format(outer_context=outer_context, step_prompt=current_task)
        else:  # Russian
            if history:
                current_task = self.ru_history_template.format(history=history, current_task=current_task)

            return self.ru_chain_template.format(outer_context=outer_context, step_prompt=current_task)
