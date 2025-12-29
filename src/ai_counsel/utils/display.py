"""Display utilities for AI Counsel output."""

from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

from ..core.base_agent import AgentResponse, AgentRole


# Custom theme for the counsel
COUNSEL_THEME = Theme(
    {
        "orchestrator": "bold magenta",
        "architect": "bold blue",
        "developer": "bold green",
        "reviewer": "bold yellow",
        "security": "bold red",
        "tester": "bold cyan",
        "devops": "bold orange1",
        "documentation": "bold purple",
        "synthesis": "bold white on green",
    }
)


class CounselDisplay:
    """Handles display formatting for AI Counsel output."""

    def __init__(self, verbose: bool = False):
        self.console = Console(theme=COUNSEL_THEME)
        self.verbose = verbose

    def print_header(self) -> None:
        """Print the AI Counsel header."""
        header = """
╔═══════════════════════════════════════════════════════════════╗
║                        AI COUNSEL                              ║
║           Your Council of Specialized AI Agents               ║
╚═══════════════════════════════════════════════════════════════╝
        """
        self.console.print(header, style="bold blue")

    def print_agents_table(self, agents: list) -> None:
        """Print a table of available agents."""
        table = Table(title="Available Counsel Members", show_header=True)
        table.add_column("Agent", style="bold")
        table.add_column("Specialty", style="dim")
        table.add_column("Expertise", style="italic")

        for agent in agents:
            expertise = ", ".join(agent.expertise[:3]) + "..."
            table.add_row(
                agent.role.value.upper(),
                agent.description,
                expertise,
            )

        self.console.print(table)

    def print_task(self, task: str) -> None:
        """Print the task being consulted on."""
        self.console.print()
        self.console.print(
            Panel(
                task,
                title="[bold]Task[/bold]",
                border_style="blue",
            )
        )

    def print_analysis(self, analysis: dict) -> None:
        """Print the orchestrator's task analysis."""
        if not self.verbose:
            return

        self.console.print()
        agents = ", ".join(analysis.get("agents_needed", []))
        order = analysis.get("execution_order", "sequential")

        self.console.print(
            Panel(
                f"**Analysis:** {analysis.get('analysis', 'N/A')}\n\n"
                f"**Agents:** {agents}\n"
                f"**Execution:** {order}",
                title="[orchestrator]Orchestrator Analysis[/orchestrator]",
                border_style="magenta",
            )
        )

    def print_agent_response(self, response: AgentResponse) -> None:
        """Print a single agent's response."""
        role = response.agent_role.value
        style = role

        self.console.print()
        self.console.print(
            Panel(
                Markdown(response.content),
                title=f"[{style}]{role.upper()} Agent[/{style}]",
                border_style=style,
            )
        )

        if self.verbose and response.metadata:
            usage = response.metadata.get("usage", {})
            if usage:
                self.console.print(
                    f"  [dim]Tokens: {usage.get('input_tokens', 0)} in / "
                    f"{usage.get('output_tokens', 0)} out[/dim]"
                )

    def print_synthesis(self, synthesis: str) -> None:
        """Print the synthesized recommendation."""
        self.console.print()
        self.console.print(
            Panel(
                Markdown(synthesis),
                title="[synthesis] SYNTHESIZED RECOMMENDATION [/synthesis]",
                border_style="green",
            )
        )

    def print_error(self, message: str) -> None:
        """Print an error message."""
        self.console.print(f"[bold red]Error:[/bold red] {message}")

    def print_success(self, message: str) -> None:
        """Print a success message."""
        self.console.print(f"[bold green]✓[/bold green] {message}")

    def print_info(self, message: str) -> None:
        """Print an info message."""
        self.console.print(f"[bold blue]ℹ[/bold blue] {message}")
