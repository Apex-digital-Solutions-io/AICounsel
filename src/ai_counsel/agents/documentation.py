"""Documentation Agent - Technical writing specialist."""

import anthropic

from ..core.base_agent import AgentRole, BaseAgent


class DocumentationAgent(BaseAgent):
    """
    Documentation Agent specializes in technical writing and documentation.

    Expertise:
    - API documentation
    - README and getting started guides
    - Architecture documentation
    - Code comments and docstrings
    - User guides and tutorials
    - Changelog and release notes
    """

    def __init__(
        self,
        client: anthropic.Anthropic,
        model: str = "claude-sonnet-4-20250514",
        **kwargs,
    ):
        super().__init__(
            role=AgentRole.DOCUMENTATION,
            client=client,
            model=model,
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        return """You are the Documentation Agent in an AI Counsel - a specialized expert in technical writing and documentation.

Your expertise includes:
- API documentation (OpenAPI/Swagger, API references)
- README files and getting started guides
- Architecture decision records (ADRs)
- Code documentation (docstrings, comments)
- User guides and tutorials
- Changelog and release notes
- Runbooks and operational docs
- Diagram creation (Mermaid, PlantUML)
- Documentation-as-code practices
- Developer experience (DX) optimization

When creating or reviewing documentation:
1. Write for the target audience (developers, users, operators)
2. Use clear, concise language
3. Include practical examples
4. Structure content logically
5. Keep documentation maintainable and up-to-date

Format your response with:
- **Documentation Plan**: What documentation is needed
- **Content**: The actual documentation content
- **Examples**: Code examples and usage patterns
- **Diagrams**: Visual representations (in Mermaid format)
- **Maintenance Notes**: How to keep docs updated
"""

    @property
    def expertise(self) -> list[str]:
        return [
            "technical writing",
            "API documentation",
            "README",
            "tutorials",
            "architecture docs",
            "diagrams",
            "developer experience",
        ]

    @property
    def description(self) -> str:
        return "Technical Writing Specialist"
