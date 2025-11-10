"""Fermion Sandbox SDK for Python.

Secure isolated code execution in containerized environments.
"""

from .sandbox import Sandbox, CommandResult
from .types import (
    ContainerDetails,
    RunConfig,
    DsaExecutionResult,
    DsaCodeExecutionEntry,
    Language,
    RunStatus,
    ProgramRunData,
    RunResult,
    CodingTaskStatus,
)
from .utils import encode_base64url, decode_base64url

__version__ = "0.1.0"

__all__ = [
    # Main SDK class
    "Sandbox",
    "CommandResult",
    # Types for DSA execution
    "ContainerDetails",
    "RunConfig",
    "DsaExecutionResult",
    "DsaCodeExecutionEntry",
    "Language",
    "RunStatus",
    "ProgramRunData",
    "RunResult",
    "CodingTaskStatus",
    # Utility functions
    "encode_base64url",
    "decode_base64url",
]
