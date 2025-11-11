"""Augment SDK - Python client for Augment CLI agent"""

__version__ = "0.1.0"

from .agent import Agent, Model, VerificationResult
from .exceptions import (
    AugmentError,
    AugmentCLIError,
    AugmentJSONError,
    AugmentNotFoundError,
    AugmentParseError,
    AugmentWorkspaceError,
    AugmentVerificationError,
)
from .listener import AgentListener, LoggingAgentListener

__all__ = [
    "Agent",
    "Model",
    "VerificationResult",
    "AgentListener",
    "LoggingAgentListener",
    "AugmentError",
    "AugmentCLIError",
    "AugmentJSONError",
    "AugmentNotFoundError",
    "AugmentParseError",
    "AugmentWorkspaceError",
    "AugmentVerificationError",
]
