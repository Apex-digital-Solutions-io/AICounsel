"""CLI interface for AI Counsel."""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt

from .counsel import AICounsel
from .core.base_agent import AgentRole
from .core.config import Config
from .utils.display import CounselDisplay

app = typer.Typer(
    name="ai-counsel",
    help="AI Counsel - Your council of specialized AI agents for building applications",
    add_completion=False,
)
console = Console()


def get_counsel(verbose: bool = False) -> AICounsel:
    """Initialize the AI Counsel."""
    try:
        config = Config.from_env()
        config.counsel.verbose = verbose
        return AICounsel(config)
    except ValueError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def consult(
    task: Optional[str] = typer.Argument(None, help="The task to consult on"),
    agents: Optional[str] = typer.Option(
        None,
        "--agents",
        "-a",
        help="Comma-separated list of agents to consult (e.g., architect,developer,security)",
    ),
    file: Optional[Path] = typer.Option(
        None,
        "--file",
        "-f",
        help="File to include as context",
    ),
    project: Optional[Path] = typer.Option(
        None,
        "--project",
        "-p",
        help="Project directory for context gathering",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Enter interactive mode",
    ),
) -> None:
    """Consult the AI Counsel on a task or question."""
    display = CounselDisplay(verbose=verbose)

    if interactive:
        _interactive_mode(verbose)
        return

    if not task:
        task = Prompt.ask("[bold blue]What would you like to consult on?[/bold blue]")

    if not task:
        console.print("[yellow]No task provided. Exiting.[/yellow]")
        raise typer.Exit(0)

    counsel = get_counsel(verbose)

    # Parse agents if specified
    agent_roles = None
    if agents:
        agent_roles = []
        for agent_name in agents.split(","):
            agent_name = agent_name.strip().lower()
            try:
                agent_roles.append(AgentRole(agent_name))
            except ValueError:
                console.print(f"[yellow]Unknown agent: {agent_name}[/yellow]")

    # Read file context if provided
    code_context = None
    if file and file.exists():
        code_context = file.read_text()

    # Gather project context if provided
    project_context = None
    if project:
        from .utils.context import gather_project_context
        project_context = gather_project_context(project)

    display.print_header()
    display.print_task(task)

    # Run the consultation
    try:
        session = asyncio.run(
            counsel.consult(
                task=task,
                agents=agent_roles,
                project_context=project_context,
                code_context=code_context,
            )
        )

        # Display results
        if verbose and session.metadata.get("analysis"):
            display.print_analysis(session.metadata["analysis"])

        for response in session.responses:
            display.print_agent_response(response)

        if session.synthesis:
            display.print_synthesis(session.synthesis)

    except Exception as e:
        display.print_error(str(e))
        raise typer.Exit(1)


@app.command()
def agents() -> None:
    """List available counsel agents."""
    display = CounselDisplay()
    display.print_header()

    counsel = get_counsel()
    display.print_agents_table(list(counsel.orchestrator.agents.values()))


@app.command()
def interactive() -> None:
    """Start an interactive session with the AI Counsel."""
    _interactive_mode(verbose=False)


def _interactive_mode(verbose: bool = False) -> None:
    """Run the interactive counsel session."""
    display = CounselDisplay(verbose=verbose)
    display.print_header()

    counsel = get_counsel(verbose)
    display.print_agents_table(list(counsel.orchestrator.agents.values()))

    console.print("\n[bold]Interactive Mode[/bold]")
    console.print("Type your questions or tasks. Commands:")
    console.print("  [dim]/agents[/dim]  - List available agents")
    console.print("  [dim]/verbose[/dim] - Toggle verbose mode")
    console.print("  [dim]/quit[/dim]    - Exit")
    console.print()

    while True:
        try:
            task = Prompt.ask("[bold blue]You[/bold blue]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not task:
            continue

        if task.lower() in ["/quit", "/exit", "/q"]:
            console.print("[dim]Goodbye![/dim]")
            break

        if task.lower() == "/agents":
            display.print_agents_table(list(counsel.orchestrator.agents.values()))
            continue

        if task.lower() == "/verbose":
            display.verbose = not display.verbose
            console.print(f"[dim]Verbose mode: {'on' if display.verbose else 'off'}[/dim]")
            continue

        # Run consultation
        try:
            session = asyncio.run(counsel.consult(task=task))

            for response in session.responses:
                display.print_agent_response(response)

            if session.synthesis:
                display.print_synthesis(session.synthesis)

        except Exception as e:
            display.print_error(str(e))


if __name__ == "__main__":
    app()
