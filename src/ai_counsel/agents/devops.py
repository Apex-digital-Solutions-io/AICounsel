"""DevOps Agent - CI/CD and infrastructure specialist."""

import anthropic

from ..core.base_agent import AgentRole, BaseAgent


class DevOpsAgent(BaseAgent):
    """
    DevOps Agent specializes in CI/CD, deployment, and infrastructure.

    Expertise:
    - CI/CD pipeline design
    - Container orchestration (Docker, Kubernetes)
    - Cloud infrastructure (AWS, GCP, Azure)
    - Infrastructure as Code (Terraform, Pulumi)
    - Monitoring and observability
    - Deployment strategies
    - Configuration management
    """

    def __init__(
        self,
        client: anthropic.Anthropic,
        model: str = "claude-sonnet-4-20250514",
        **kwargs,
    ):
        super().__init__(
            role=AgentRole.DEVOPS,
            client=client,
            model=model,
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        return """You are the DevOps Agent in an AI Counsel - a specialized expert in CI/CD, deployment, and infrastructure.

Your expertise includes:
- CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins, CircleCI)
- Container technologies (Docker, containerd)
- Container orchestration (Kubernetes, ECS, Cloud Run)
- Cloud platforms (AWS, GCP, Azure)
- Infrastructure as Code (Terraform, Pulumi, CloudFormation)
- Configuration management (Ansible, Chef, Puppet)
- Monitoring and observability (Prometheus, Grafana, DataDog)
- Logging (ELK stack, CloudWatch, Loki)
- Deployment strategies (blue-green, canary, rolling)
- GitOps and ArgoCD
- Security in DevOps (DevSecOps)
- Cost optimization

When providing DevOps recommendations:
1. Consider operational complexity and team skills
2. Balance automation with maintainability
3. Include monitoring and rollback strategies
4. Consider cost implications
5. Prioritize reliability and observability

Format your response with:
- **Infrastructure Recommendation**: Proposed setup
- **CI/CD Pipeline**: Build and deployment workflow
- **Deployment Strategy**: How to safely deploy
- **Monitoring & Alerting**: Observability setup
- **Configuration**: IaC and config examples
- **Cost Considerations**: Resource and cost notes
"""

    @property
    def expertise(self) -> list[str]:
        return [
            "CI/CD",
            "Docker",
            "Kubernetes",
            "cloud infrastructure",
            "Terraform",
            "monitoring",
            "deployment",
            "DevSecOps",
        ]

    @property
    def description(self) -> str:
        return "CI/CD & Infrastructure Specialist"
