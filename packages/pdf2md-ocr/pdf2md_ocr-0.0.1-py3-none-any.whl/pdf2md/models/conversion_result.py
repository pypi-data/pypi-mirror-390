"""Conversion Result model for Docker execution results."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ConversionResult:
    """Result of a Docker-based conversion operation.
    
    Attributes:
        success: Whether the conversion succeeded
        exit_code: Exit code from Docker container
        stdout: Standard output from container
        stderr: Standard error from container
        execution_time: Time taken for execution
        error_message: Human-readable error message
        docker_command: Docker command that was executed
    """
    
    success: bool
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    error_message: str = ""
    docker_command: List[str] = field(default_factory=list)