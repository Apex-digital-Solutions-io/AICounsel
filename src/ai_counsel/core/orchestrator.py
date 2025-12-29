"""Lead Orchestrator for the AI Counsel system."""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Optional

import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .base_agent import AgentContext, AgentResponse, AgentRole, BaseAgent


@dataclass
class CounselSession:
    """A session with the AI Counsel."""

    task: str
    responses: list[AgentResponse] = field(default_factory=list)
    synthesis: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    """
    Lead Orchestrator that coordinates the AI Counsel.

    Responsibilities:
    - Analyzes incoming tasks and determines which specialists to consult
    - Delegates tasks to appropriate specialist agents
    - Synthesizes responses from multiple agents
    - Manages cross-validation between agents
    """

    def __init__(
        self,
        client: anthropic.Anthropic,
        agents: list[BaseAgent],
        model: str = "claude-sonnet-4-20250514",
        enable_parallel: bool = True,
        max_parallel: int = 4,
        verbose: bool = False,
    ):
        self.client = client
        self.agents = {agent.role: agent for agent in agents}
        self.model = model
        self.enable_parallel = enable_parallel
        self.max_parallel = max_parallel
        self.verbose = verbose
        self.console = Console()

    @property
    def system_prompt(self) -> str:
        return """You are the Lead Orchestrator of an AI Counsel - a team of specialized AI agents
that collaborate to help build software applications.

Your role is to:
1. Analyze incoming tasks and break them down into components
2. Determine which specialist agents should be consulted
3. Coordinate the workflow between agents
4. Synthesize responses into actionable recommendations

Available specialist agents:
- ARCHITECT: System design, patterns, architecture decisions
- DEVELOPER: Code implementation, best practices
- REVIEWER: Code quality, improvements, refactoring
- SECURITY: Security analysis, vulnerability assessment
- TESTER: Test strategies, test cases, QA
- DEVOPS: CI/CD, deployment, infrastructure
- DOCUMENTATION: Technical writing, API docs

When analyzing a task, respond with a JSON structure:
{
    "analysis": "Brief analysis of the task",
    "agents_needed": ["ARCHITECT", "DEVELOPER", ...],
    "execution_order": "parallel" or "sequential",
    "priority_agent": "The most important agent for this task",
    "subtasks": [
        {"agent": "AGENT_ROLE", "task": "Specific task for this agent"}
    ]
}
"""

    async def analyze_task(self, task: str, project_context: Optional[str] = None) -> dict[str, Any]:
        """Analyze a task and determine which agents to consult."""
        messages = [
            {
                "role": "user",
                "content": f"""Analyze this task and determine which specialist agents should be consulted.

Task: {task}

{f"Project Context: {project_context}" if project_context else ""}

Respond with the JSON structure as specified in your instructions.""",
            }
        ]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            temperature=0.3,
            system=self.system_prompt,
            messages=messages,
        )

        content = response.content[0].text if response.content else "{}"

        # Parse JSON from response
        import json
        try:
            # Try to extract JSON from the response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
        except json.JSONDecodeError:
            pass

        # Default fallback
        return {
            "analysis": "Could not parse task analysis",
            "agents_needed": ["ARCHITECT", "DEVELOPER"],
            "execution_order": "sequential",
            "priority_agent": "ARCHITECT",
            "subtasks": [
                {"agent": "ARCHITECT", "task": task},
                {"agent": "DEVELOPER", "task": task},
            ],
        }

    async def _execute_agent(
        self, agent: BaseAgent, context: AgentContext
    ) -> AgentResponse:
        """Execute a single agent's task."""
        return await agent.execute(context)

    async def _execute_parallel(
        self, agents: list[BaseAgent], context: AgentContext
    ) -> list[AgentResponse]:
        """Execute multiple agents in parallel."""
        tasks = [self._execute_agent(agent, context) for agent in agents]

        # Limit parallel execution
        semaphore = asyncio.Semaphore(self.max_parallel)

        async def bounded_execute(task):
            async with semaphore:
                return await task

        bounded_tasks = [bounded_execute(task) for task in tasks]
        return await asyncio.gather(*bounded_tasks)

    async def _execute_sequential(
        self, agents: list[BaseAgent], base_context: AgentContext
    ) -> list[AgentResponse]:
        """Execute agents sequentially, passing context between them."""
        responses = []
        context = base_context

        for agent in agents:
            response = await self._execute_agent(agent, context)
            responses.append(response)

            # Update context with previous responses
            context = AgentContext(
                task=base_context.task,
                project_context=base_context.project_context,
                code_context=base_context.code_context,
                previous_responses=[r.to_dict() for r in responses],
                constraints=base_context.constraints,
                preferences=base_context.preferences,
            )

        return responses

    async def synthesize_responses(
        self, task: str, responses: list[AgentResponse]
    ) -> str:
        """Synthesize multiple agent responses into a cohesive recommendation."""
        responses_text = "\n\n".join(
            f"## {r.agent_role.value.upper()} Agent Response\n{r.content}"
            for r in responses
        )

        messages = [
            {
                "role": "user",
                "content": f"""As the Lead Orchestrator, synthesize these specialist responses into
a cohesive, actionable recommendation.

Original Task: {task}

Specialist Responses:
{responses_text}

Provide a synthesized recommendation that:
1. Highlights key insights from each specialist
2. Resolves any conflicts between recommendations
3. Provides a clear, prioritized action plan
4. Notes any areas of strong consensus or disagreement""",
            }
        ]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.5,
            system="You are synthesizing expert recommendations into actionable guidance.",
            messages=messages,
        )

        return response.content[0].text if response.content else ""

    async def consult(
        self,
        task: str,
        project_context: Optional[str] = None,
        code_context: Optional[str] = None,
        agents: Optional[list[AgentRole]] = None,
    ) -> CounselSession:
        """
        Consult the AI Counsel on a task.

        Args:
            task: The task or question to consult on
            project_context: Optional context about the project
            code_context: Optional code snippet for context
            agents: Optional specific agents to consult (auto-selects if None)

        Returns:
            CounselSession with all responses and synthesis
        """
        session = CounselSession(task=task)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            # Step 1: Analyze task
            progress.add_task("Analyzing task...", total=None)
            analysis = await self.analyze_task(task, project_context)
            session.metadata["analysis"] = analysis

            # Step 2: Determine which agents to use
            if agents:
                agents_to_use = [self.agents[role] for role in agents if role in self.agents]
            else:
                agent_roles = [
                    AgentRole(role.lower())
                    for role in analysis.get("agents_needed", ["ARCHITECT", "DEVELOPER"])
                    if role.lower() in [r.value for r in AgentRole]
                ]
                agents_to_use = [
                    self.agents[role] for role in agent_roles if role in self.agents
                ]

            if not agents_to_use:
                # Fallback to all available agents
                agents_to_use = list(self.agents.values())

            # Step 3: Build context
            context = AgentContext(
                task=task,
                project_context=project_context,
                code_context=code_context,
            )

            # Step 4: Execute agents
            progress.add_task(
                f"Consulting {len(agents_to_use)} specialists...", total=None
            )

            execution_order = analysis.get("execution_order", "parallel")

            if self.enable_parallel and execution_order == "parallel":
                responses = await self._execute_parallel(agents_to_use, context)
            else:
                responses = await self._execute_sequential(agents_to_use, context)

            session.responses = responses

            # Step 5: Synthesize responses
            if len(responses) > 1:
                progress.add_task("Synthesizing recommendations...", total=None)
                session.synthesis = await self.synthesize_responses(task, responses)

        return session

    def display_session(self, session: CounselSession) -> None:
        """Display a counsel session's results."""
        self.console.print()
        self.console.print(
            Panel(f"[bold]Task:[/bold] {session.task}", title="AI Counsel Session")
        )

        for response in session.responses:
            self.console.print()
            self.console.print(
                Panel(
                    response.content,
                    title=f"[bold blue]{response.agent_role.value.upper()}[/bold blue] Agent",
                    border_style="blue",
                )
            )

        if session.synthesis:
            self.console.print()
            self.console.print(
                Panel(
                    session.synthesis,
                    title="[bold green]Synthesized Recommendation[/bold green]",
                    border_style="green",
                )
            )
