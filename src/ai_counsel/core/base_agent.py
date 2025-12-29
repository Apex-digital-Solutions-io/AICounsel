"""Base agent class for all AI Counsel agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import anthropic
from pydantic import BaseModel


class AgentRole(str, Enum):
    """Roles for specialized agents in the counsel."""

    ORCHESTRATOR = "orchestrator"
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    SECURITY = "security"
    TESTER = "tester"
    DEVOPS = "devops"
    DOCUMENTATION = "documentation"


@dataclass
class AgentResponse:
    """Response from an agent."""

    agent_role: AgentRole
    content: str
    reasoning: Optional[str] = None
    suggestions: list[str] = field(default_factory=list)
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "agent_role": self.agent_role.value,
            "content": self.content,
            "reasoning": self.reasoning,
            "suggestions": self.suggestions,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


class AgentContext(BaseModel):
    """Context passed to agents for task execution."""

    task: str
    project_context: Optional[str] = None
    code_context: Optional[str] = None
    previous_responses: list[dict[str, Any]] = []
    constraints: list[str] = []
    preferences: dict[str, Any] = {}


class BaseAgent(ABC):
    """Base class for all AI Counsel agents."""

    def __init__(
        self,
        role: AgentRole,
        client: anthropic.Anthropic,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
        max_tokens: int = 8192,
    ):
        self.role = role
        self.client = client
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    @property
    @abstractmethod
    def expertise(self) -> list[str]:
        """Return the areas of expertise for this agent."""
        pass

    @property
    def description(self) -> str:
        """Return a description of the agent's role."""
        return f"{self.role.value.title()} Agent"

    def _build_messages(self, context: AgentContext) -> list[dict[str, str]]:
        """Build the message list for the API call."""
        messages = []

        # Add previous responses as context if available
        if context.previous_responses:
            prev_context = "\n\n".join(
                f"[{r['agent_role'].upper()}]: {r['content']}"
                for r in context.previous_responses
            )
            messages.append(
                {
                    "role": "user",
                    "content": f"Previous counsel responses for context:\n\n{prev_context}",
                }
            )
            messages.append(
                {
                    "role": "assistant",
                    "content": "I've reviewed the previous counsel responses and will provide my specialized perspective.",
                }
            )

        # Build the main task message
        task_parts = [f"## Task\n{context.task}"]

        if context.project_context:
            task_parts.append(f"## Project Context\n{context.project_context}")

        if context.code_context:
            task_parts.append(f"## Code Context\n```\n{context.code_context}\n```")

        if context.constraints:
            task_parts.append(
                f"## Constraints\n" + "\n".join(f"- {c}" for c in context.constraints)
            )

        messages.append({"role": "user", "content": "\n\n".join(task_parts)})

        return messages

    async def execute(self, context: AgentContext) -> AgentResponse:
        """Execute the agent's task and return a response."""
        messages = self._build_messages(context)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=self.system_prompt,
            messages=messages,
        )

        content = response.content[0].text if response.content else ""

        return AgentResponse(
            agent_role=self.role,
            content=content,
            metadata={
                "model": self.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            },
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} role={self.role.value}>"
