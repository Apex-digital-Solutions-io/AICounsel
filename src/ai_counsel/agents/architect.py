"""Architect Agent - System design and architecture specialist."""

import anthropic

from ..core.base_agent import AgentRole, BaseAgent


class ArchitectAgent(BaseAgent):
    """
    Architect Agent specializes in system design and architecture decisions.

    Expertise:
    - System architecture and design patterns
    - Technology stack selection
    - Scalability and performance considerations
    - API design and contracts
    - Database schema design
    - Microservices vs monolith decisions
    """

    def __init__(
        self,
        client: anthropic.Anthropic,
        model: str = "claude-sonnet-4-20250514",
        **kwargs,
    ):
        super().__init__(
            role=AgentRole.ARCHITECT,
            client=client,
            model=model,
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        return """You are the Architect Agent in an AI Counsel - a specialized expert in software architecture and system design.

Your expertise includes:
- System architecture patterns (microservices, monolith, event-driven, etc.)
- Design patterns (SOLID, DDD, CQRS, etc.)
- Technology stack evaluation and selection
- Scalability, performance, and reliability considerations
- API design (REST, GraphQL, gRPC)
- Database design (SQL, NoSQL, schema optimization)
- Cloud architecture (AWS, GCP, Azure patterns)
- Integration patterns and middleware

When providing recommendations:
1. Consider both immediate needs and future scalability
2. Evaluate trade-offs between different approaches
3. Provide clear rationale for architectural decisions
4. Consider operational complexity and team capabilities
5. Highlight potential risks and mitigation strategies

Format your response with:
- **Recommendation**: Your primary architectural recommendation
- **Rationale**: Why this approach is suitable
- **Trade-offs**: Pros and cons to consider
- **Alternatives**: Other viable approaches
- **Implementation Notes**: Key considerations for implementation
"""

    @property
    def expertise(self) -> list[str]:
        return [
            "system architecture",
            "design patterns",
            "technology selection",
            "scalability",
            "API design",
            "database design",
            "cloud architecture",
            "microservices",
        ]

    @property
    def description(self) -> str:
        return "System Design & Architecture Specialist"
