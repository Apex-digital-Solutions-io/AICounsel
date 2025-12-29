"""Security Agent - Security analysis specialist."""

import anthropic

from ..core.base_agent import AgentRole, BaseAgent


class SecurityAgent(BaseAgent):
    """
    Security Agent specializes in security analysis and vulnerability assessment.

    Expertise:
    - OWASP Top 10 vulnerabilities
    - Authentication and authorization patterns
    - Input validation and sanitization
    - Cryptography best practices
    - Security headers and configurations
    - Secrets management
    - Compliance considerations
    """

    def __init__(
        self,
        client: anthropic.Anthropic,
        model: str = "claude-sonnet-4-20250514",
        **kwargs,
    ):
        super().__init__(
            role=AgentRole.SECURITY,
            client=client,
            model=model,
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        return """You are the Security Agent in an AI Counsel - a specialized expert in application security and vulnerability assessment.

Your expertise includes:
- OWASP Top 10 vulnerabilities (XSS, SQL injection, CSRF, etc.)
- Authentication patterns (OAuth, JWT, session management)
- Authorization and access control (RBAC, ABAC)
- Input validation and output encoding
- Cryptography (hashing, encryption, key management)
- Secure API design
- Security headers and CORS
- Secrets management and environment security
- Compliance (GDPR, SOC2, PCI-DSS awareness)
- Dependency security and supply chain risks

When analyzing security:
1. Identify potential vulnerabilities with specific examples
2. Rate severity using CVSS-like scale (Critical, High, Medium, Low)
3. Provide concrete remediation steps
4. Consider both immediate fixes and long-term security posture
5. Reference industry standards and best practices

Format your response with:
- **Security Assessment**: Overall security posture
- **Vulnerabilities Found**: Specific issues identified
  - Severity, description, location, remediation
- **Security Recommendations**: Proactive improvements
- **Compliance Notes**: Relevant compliance considerations
- **Secure Implementation**: Code examples for fixes
"""

    @property
    def expertise(self) -> list[str]:
        return [
            "security analysis",
            "vulnerability assessment",
            "OWASP",
            "authentication",
            "authorization",
            "cryptography",
            "compliance",
            "secure coding",
        ]

    @property
    def description(self) -> str:
        return "Security Analysis Specialist"
