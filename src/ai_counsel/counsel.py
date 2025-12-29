"""Main AI Counsel class - the entry point for using the counsel."""

from typing import Optional

import anthropic

from .agents import (
    ArchitectAgent,
    DeveloperAgent,
    DevOpsAgent,
    DocumentationAgent,
    ReviewerAgent,
    SecurityAgent,
    TesterAgent,
)
from .core.base_agent import AgentRole
from .core.config import Config
from .core.orchestrator import CounselSession, Orchestrator


class AICounsel:
    """
    AI Counsel - A council of specialized AI agents for building applications.

    This is the main entry point for using the AI Counsel system. It initializes
    all specialist agents and provides a simple interface for consulting them.

    Example:
        ```python
        from ai_counsel import AICounsel
        from ai_counsel.core.config import Config

        config = Config.from_env()
        counsel = AICounsel(config)

        # Consult on a task
        session = await counsel.consult(
            task="Design a REST API for a todo application",
            agents=[AgentRole.ARCHITECT, AgentRole.DEVELOPER, AgentRole.SECURITY]
        )

        # Access responses
        for response in session.responses:
            print(f"{response.agent_role}: {response.content}")

        # Get synthesized recommendation
        print(session.synthesis)
        ```
    """

    def __init__(self, config: Config):
        """
        Initialize the AI Counsel.

        Args:
            config: Configuration object with API keys and settings
        """
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.api_key)

        # Initialize all specialist agents
        agent_model = config.model.agent_model
        agent_kwargs = {
            "temperature": config.model.temperature,
            "max_tokens": config.model.max_tokens,
        }

        self.agents = {
            AgentRole.ARCHITECT: ArchitectAgent(
                client=self.client, model=agent_model, **agent_kwargs
            ),
            AgentRole.DEVELOPER: DeveloperAgent(
                client=self.client, model=agent_model, **agent_kwargs
            ),
            AgentRole.REVIEWER: ReviewerAgent(
                client=self.client, model=agent_model, **agent_kwargs
            ),
            AgentRole.SECURITY: SecurityAgent(
                client=self.client, model=agent_model, **agent_kwargs
            ),
            AgentRole.TESTER: TesterAgent(
                client=self.client, model=agent_model, **agent_kwargs
            ),
            AgentRole.DEVOPS: DevOpsAgent(
                client=self.client, model=agent_model, **agent_kwargs
            ),
            AgentRole.DOCUMENTATION: DocumentationAgent(
                client=self.client, model=agent_model, **agent_kwargs
            ),
        }

        # Initialize orchestrator
        self.orchestrator = Orchestrator(
            client=self.client,
            agents=list(self.agents.values()),
            model=config.model.lead_model,
            enable_parallel=config.counsel.enable_parallel,
            max_parallel=config.counsel.max_parallel_agents,
            verbose=config.counsel.verbose,
        )

    async def consult(
        self,
        task: str,
        agents: Optional[list[AgentRole]] = None,
        project_context: Optional[str] = None,
        code_context: Optional[str] = None,
    ) -> CounselSession:
        """
        Consult the AI Counsel on a task.

        Args:
            task: The task or question to consult on
            agents: Optional list of specific agents to consult
                   (auto-selects if None)
            project_context: Optional context about the project
            code_context: Optional code snippet for context

        Returns:
            CounselSession containing all responses and synthesis
        """
        return await self.orchestrator.consult(
            task=task,
            project_context=project_context,
            code_context=code_context,
            agents=agents,
        )

    def get_agent(self, role: AgentRole):
        """Get a specific agent by role."""
        return self.agents.get(role)

    def list_agents(self) -> list[dict]:
        """List all available agents with their info."""
        return [
            {
                "role": agent.role.value,
                "description": agent.description,
                "expertise": agent.expertise,
            }
            for agent in self.agents.values()
        ]
