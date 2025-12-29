"""Context gathering utilities for AI Counsel."""

import os
from pathlib import Path
from typing import Optional


def gather_project_context(
    project_path: Optional[Path] = None,
    include_structure: bool = True,
    include_readme: bool = True,
    max_depth: int = 3,
) -> str:
    """
    Gather context about a project for the AI Counsel.

    Args:
        project_path: Path to the project (defaults to cwd)
        include_structure: Include directory structure
        include_readme: Include README content
        max_depth: Maximum depth for directory tree

    Returns:
        String containing project context
    """
    if project_path is None:
        project_path = Path.cwd()

    context_parts = []

    # Project name
    context_parts.append(f"# Project: {project_path.name}")

    # Directory structure
    if include_structure:
        structure = _get_directory_structure(project_path, max_depth)
        context_parts.append(f"\n## Directory Structure\n```\n{structure}\n```")

    # README content
    if include_readme:
        readme_content = _get_readme_content(project_path)
        if readme_content:
            context_parts.append(f"\n## README\n{readme_content}")

    # Package files
    package_info = _get_package_info(project_path)
    if package_info:
        context_parts.append(f"\n## Package Configuration\n{package_info}")

    return "\n".join(context_parts)


def _get_directory_structure(path: Path, max_depth: int, prefix: str = "") -> str:
    """Generate a tree-like directory structure."""
    if max_depth <= 0:
        return ""

    # Directories and files to skip
    skip = {
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "dist",
        "build",
        "*.egg-info",
    }

    lines = []

    try:
        entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        return ""

    # Filter entries
    entries = [e for e in entries if e.name not in skip and not e.name.startswith(".")]

    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")

        if entry.is_dir():
            extension = "    " if is_last else "│   "
            sub_structure = _get_directory_structure(
                entry, max_depth - 1, prefix + extension
            )
            if sub_structure:
                lines.append(sub_structure)

    return "\n".join(lines)


def _get_readme_content(path: Path) -> Optional[str]:
    """Get README content if available."""
    readme_names = ["README.md", "README.rst", "README.txt", "README"]

    for name in readme_names:
        readme_path = path / name
        if readme_path.exists():
            try:
                content = readme_path.read_text()
                # Truncate if too long
                if len(content) > 2000:
                    content = content[:2000] + "\n\n... (truncated)"
                return content
            except Exception:
                pass

    return None


def _get_package_info(path: Path) -> Optional[str]:
    """Get package configuration info."""
    info_parts = []

    # Python: pyproject.toml or setup.py
    pyproject = path / "pyproject.toml"
    if pyproject.exists():
        info_parts.append("- Python project (pyproject.toml)")

    setup_py = path / "setup.py"
    if setup_py.exists():
        info_parts.append("- Python project (setup.py)")

    # Node.js: package.json
    package_json = path / "package.json"
    if package_json.exists():
        info_parts.append("- Node.js project (package.json)")

    # Go: go.mod
    go_mod = path / "go.mod"
    if go_mod.exists():
        info_parts.append("- Go project (go.mod)")

    # Rust: Cargo.toml
    cargo = path / "Cargo.toml"
    if cargo.exists():
        info_parts.append("- Rust project (Cargo.toml)")

    # Docker
    dockerfile = path / "Dockerfile"
    if dockerfile.exists():
        info_parts.append("- Docker support (Dockerfile)")

    docker_compose = path / "docker-compose.yml"
    if docker_compose.exists():
        info_parts.append("- Docker Compose (docker-compose.yml)")

    return "\n".join(info_parts) if info_parts else None


def read_file_context(file_path: Path, max_lines: int = 200) -> Optional[str]:
    """Read file content for context."""
    try:
        content = file_path.read_text()
        lines = content.split("\n")

        if len(lines) > max_lines:
            half = max_lines // 2
            content = "\n".join(lines[:half]) + "\n\n... (truncated) ...\n\n" + "\n".join(lines[-half:])

        return content
    except Exception:
        return None
