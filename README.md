# AI Counsel

A council of specialized AI agents that collaborate to help you build applications. Powered by Claude.

## Overview

AI Counsel provides a team of specialized AI agents, each with distinct expertise, that work together to provide comprehensive guidance for software development tasks:

| Agent | Specialty |
|-------|-----------|
| **Architect** | System design, patterns, architecture decisions |
| **Developer** | Code implementation, best practices |
| **Reviewer** | Code quality, refactoring, improvements |
| **Security** | Vulnerability analysis, secure coding |
| **Tester** | Test strategies, test cases, QA |
| **DevOps** | CI/CD, deployment, infrastructure |
| **Documentation** | Technical writing, API docs |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Task                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Lead Orchestrator                         │
│  • Analyzes task                                            │
│  • Selects relevant agents                                  │
│  • Coordinates execution                                    │
│  • Synthesizes recommendations                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │Architect │   │Developer │   │ Security │  ... (parallel)
    └──────────┘   └──────────┘   └──────────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│               Synthesized Recommendation                     │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/AICounsel.git
cd AICounsel

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your-api-key-here
```

## Usage

### Command Line Interface

```bash
# Consult on a task (auto-selects relevant agents)
ai-counsel consult "Design a REST API for a todo application"

# Specify which agents to consult
ai-counsel consult "Review this authentication flow" --agents architect,security,reviewer

# Include a file for context
ai-counsel consult "How can I improve this code?" --file src/main.py

# Include project context
ai-counsel consult "Add caching to this service" --project ./my-project

# Interactive mode
ai-counsel interactive

# List available agents
ai-counsel agents
```

### Python API

```python
import asyncio
from ai_counsel import AICounsel
from ai_counsel.core.config import Config
from ai_counsel.core.base_agent import AgentRole

# Initialize
config = Config.from_env()
counsel = AICounsel(config)

# Consult the counsel
async def main():
    session = await counsel.consult(
        task="Design a microservices architecture for an e-commerce platform",
        agents=[AgentRole.ARCHITECT, AgentRole.DEVELOPER, AgentRole.DEVOPS]
    )

    # Access individual responses
    for response in session.responses:
        print(f"\n=== {response.agent_role.value.upper()} ===")
        print(response.content)

    # Get synthesized recommendation
    if session.synthesis:
        print("\n=== SYNTHESIS ===")
        print(session.synthesis)

asyncio.run(main())
```

### Consulting Specific Agents

```python
# Get a specific agent for direct interaction
architect = counsel.get_agent(AgentRole.ARCHITECT)

# List all available agents
for agent_info in counsel.list_agents():
    print(f"{agent_info['role']}: {agent_info['description']}")
```

## How It Works

1. **Task Analysis**: The Lead Orchestrator analyzes your task and determines which specialist agents are most relevant.

2. **Parallel Execution**: Selected agents work in parallel (or sequentially if dependencies exist) to provide their specialized perspective.

3. **Cross-Validation**: Agents can review each other's recommendations, improving accuracy through collaborative validation.

4. **Synthesis**: The Orchestrator synthesizes all agent responses into a cohesive, actionable recommendation.

## Agent Specialties

### Architect Agent
- System architecture patterns
- Technology stack selection
- Scalability considerations
- API design (REST, GraphQL, gRPC)
- Database schema design

### Developer Agent
- Clean code implementation
- Multiple language expertise
- Framework best practices
- Performance optimization
- Error handling patterns

### Reviewer Agent
- Code review best practices
- Identifying anti-patterns
- Refactoring recommendations
- Technical debt assessment
- Quality metrics

### Security Agent
- OWASP Top 10 vulnerabilities
- Authentication/authorization
- Input validation
- Cryptography best practices
- Compliance considerations

### Tester Agent
- Test strategy planning
- Unit/integration/e2e testing
- Edge case identification
- TDD/BDD approaches
- Test automation

### DevOps Agent
- CI/CD pipeline design
- Container orchestration
- Infrastructure as Code
- Monitoring & observability
- Deployment strategies

### Documentation Agent
- API documentation
- Architecture decision records
- README creation
- Code documentation
- Technical tutorials

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Lint
ruff check src/
```

## License

MIT License - see LICENSE file for details.
