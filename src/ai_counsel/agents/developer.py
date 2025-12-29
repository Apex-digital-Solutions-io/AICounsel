"""Developer Agent - Code implementation specialist."""

import anthropic

from ..core.base_agent import AgentRole, BaseAgent


class DeveloperAgent(BaseAgent):
    """
    Developer Agent specializes in code implementation and best practices.

    Expertise:
    - Code implementation across multiple languages
    - Clean code principles
    - Performance optimization
    - Error handling patterns
    - Code organization and structure
    - Library and framework usage
    """

    def __init__(
        self,
        client: anthropic.Anthropic,
        model: str = "claude-sonnet-4-20250514",
        **kwargs,
    ):
        super().__init__(
            role=AgentRole.DEVELOPER,
            client=client,
            model=model,
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        return """You are the Developer Agent in an AI Counsel - a specialized expert in code implementation and software development best practices.

Your expertise includes:
- Writing clean, maintainable, and efficient code
- Multiple programming languages (Python, JavaScript/TypeScript, Go, Rust, etc.)
- Framework expertise (React, FastAPI, Django, Express, etc.)
- Design patterns and SOLID principles
- Performance optimization techniques
- Error handling and edge cases
- Code organization and modularization
- Dependency management

When providing code or recommendations:
1. Write clean, readable, and well-documented code
2. Follow language-specific conventions and idioms
3. Consider edge cases and error handling
4. Optimize for maintainability first, performance second
5. Provide working, tested code examples when applicable

Format your response with:
- **Approach**: Your recommended implementation approach
- **Code**: Implementation with clear comments
- **Explanation**: How the code works
- **Considerations**: Edge cases, error handling, performance notes
- **Dependencies**: Required libraries or frameworks
"""

    @property
    def expertise(self) -> list[str]:
        return [
            "code implementation",
            "clean code",
            "multiple languages",
            "frameworks",
            "performance",
            "error handling",
            "best practices",
        ]

    @property
    def description(self) -> str:
        return "Code Implementation Specialist"
