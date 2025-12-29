"""Reviewer Agent - Code review and quality specialist."""

import anthropic

from ..core.base_agent import AgentRole, BaseAgent


class ReviewerAgent(BaseAgent):
    """
    Reviewer Agent specializes in code review and quality improvement.

    Expertise:
    - Code review best practices
    - Identifying code smells and anti-patterns
    - Refactoring recommendations
    - Code quality metrics
    - Technical debt assessment
    - Consistency and style enforcement
    """

    def __init__(
        self,
        client: anthropic.Anthropic,
        model: str = "claude-sonnet-4-20250514",
        **kwargs,
    ):
        super().__init__(
            role=AgentRole.REVIEWER,
            client=client,
            model=model,
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        return """You are the Reviewer Agent in an AI Counsel - a specialized expert in code review and quality improvement.

Your expertise includes:
- Identifying code smells and anti-patterns
- Suggesting refactoring improvements
- Evaluating code maintainability and readability
- Checking for common bugs and issues
- Assessing code organization and structure
- Reviewing naming conventions and documentation
- Evaluating test coverage and quality
- Identifying technical debt

When reviewing code or designs:
1. Be constructive and specific in feedback
2. Prioritize issues by severity (critical, major, minor, suggestion)
3. Provide concrete improvement suggestions
4. Explain the "why" behind recommendations
5. Acknowledge good practices when present

Format your response with:
- **Summary**: Overall assessment
- **Critical Issues**: Must-fix problems
- **Major Improvements**: Strongly recommended changes
- **Minor Suggestions**: Nice-to-have improvements
- **Good Practices**: What's done well
- **Refactoring Opportunities**: Areas for improvement
"""

    @property
    def expertise(self) -> list[str]:
        return [
            "code review",
            "refactoring",
            "code quality",
            "anti-patterns",
            "technical debt",
            "maintainability",
            "best practices",
        ]

    @property
    def description(self) -> str:
        return "Code Review & Quality Specialist"
