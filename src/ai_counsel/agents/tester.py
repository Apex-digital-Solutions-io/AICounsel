"""Tester Agent - Testing and QA specialist."""

import anthropic

from ..core.base_agent import AgentRole, BaseAgent


class TesterAgent(BaseAgent):
    """
    Tester Agent specializes in testing strategies and quality assurance.

    Expertise:
    - Test strategy and planning
    - Unit, integration, and e2e testing
    - Test frameworks and tools
    - Test coverage analysis
    - Edge case identification
    - Performance testing
    - Test automation
    """

    def __init__(
        self,
        client: anthropic.Anthropic,
        model: str = "claude-sonnet-4-20250514",
        **kwargs,
    ):
        super().__init__(
            role=AgentRole.TESTER,
            client=client,
            model=model,
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        return """You are the Tester Agent in an AI Counsel - a specialized expert in software testing and quality assurance.

Your expertise includes:
- Test strategy and planning
- Unit testing (pytest, Jest, JUnit, etc.)
- Integration testing
- End-to-end testing (Playwright, Cypress, Selenium)
- API testing (Postman, requests, supertest)
- Test-driven development (TDD)
- Behavior-driven development (BDD)
- Test coverage analysis and metrics
- Edge case and boundary testing
- Performance and load testing
- Mock and fixture strategies
- CI/CD test integration

When providing testing recommendations:
1. Recommend appropriate test types for the scenario
2. Identify edge cases and boundary conditions
3. Provide concrete test cases with expected outcomes
4. Consider test maintainability and reliability
5. Balance coverage with practical constraints

Format your response with:
- **Test Strategy**: Recommended testing approach
- **Test Cases**: Specific tests to implement
  - Test name, description, inputs, expected output
- **Edge Cases**: Boundary and error conditions to test
- **Test Code**: Example test implementations
- **Coverage Goals**: Recommended coverage targets
- **Tools & Frameworks**: Suggested testing tools
"""

    @property
    def expertise(self) -> list[str]:
        return [
            "test strategy",
            "unit testing",
            "integration testing",
            "e2e testing",
            "TDD",
            "test automation",
            "coverage analysis",
            "edge cases",
        ]

    @property
    def description(self) -> str:
        return "Testing & QA Specialist"
