"""Configuration management for AI Counsel."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Configuration for AI models."""

    lead_model: str = Field(
        default="claude-sonnet-4-20250514",
        description="Model for the lead orchestrator agent",
    )
    agent_model: str = Field(
        default="claude-sonnet-4-20250514",
        description="Model for specialist agents",
    )
    max_tokens: int = Field(default=8192, description="Maximum tokens per response")
    temperature: float = Field(default=0.7, description="Temperature for responses")


class CounselConfig(BaseModel):
    """Configuration for the AI Counsel system."""

    enable_parallel: bool = Field(
        default=True, description="Enable parallel agent execution"
    )
    max_parallel_agents: int = Field(
        default=4, description="Maximum number of parallel agent calls"
    )
    enable_cross_validation: bool = Field(
        default=True, description="Enable agents to validate each other's work"
    )
    verbose: bool = Field(default=False, description="Enable verbose output")


class Config(BaseModel):
    """Main configuration for AI Counsel."""

    api_key: str = Field(..., description="Anthropic API key")
    model: ModelConfig = Field(default_factory=ModelConfig)
    counsel: CounselConfig = Field(default_factory=CounselConfig)
    working_directory: Path = Field(
        default_factory=lambda: Path.cwd(),
        description="Working directory for file operations",
    )

    @classmethod
    def from_env(cls, env_file: Optional[Path] = None) -> "Config":
        """Load configuration from environment variables."""
        if env_file and env_file.exists():
            load_dotenv(env_file)
        else:
            load_dotenv()

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required. "
                "Set it in your .env file or environment."
            )

        return cls(
            api_key=api_key,
            model=ModelConfig(
                lead_model=os.getenv("DEFAULT_LEAD_MODEL", "claude-sonnet-4-20250514"),
                agent_model=os.getenv("DEFAULT_AGENT_MODEL", "claude-sonnet-4-20250514"),
            ),
            counsel=CounselConfig(
                verbose=os.getenv("LOG_LEVEL", "INFO").upper() == "DEBUG",
            ),
        )
