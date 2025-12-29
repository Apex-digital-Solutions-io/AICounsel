"""Core components for AI Counsel."""

from .config import Config
from .base_agent import BaseAgent, AgentRole, AgentResponse
from .orchestrator import Orchestrator

__all__ = ["Config", "BaseAgent", "AgentRole", "AgentResponse", "Orchestrator"]
