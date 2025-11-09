"""Docker Configuration model for container execution settings."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from .volume_mount import VolumeMount


@dataclass
class DockerConfig:
    """Configuration for Docker container execution.
    
    Attributes:
        image: Docker image name and tag
        volume_mounts: List of volume mounts
        environment: Environment variables
        user_id: User ID for non-root execution
        memory_limit: Memory limit (e.g., "1g", "512m")
        cpu_limit: CPU limit (e.g., "2", "0.5")
        workdir: Working directory inside container
        security_opts: Security options
        remove_after_run: Whether to remove container after execution
    """
    
    image: str
    volume_mounts: List[VolumeMount] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    user_id: int = 1000
    memory_limit: Optional[str] = None
    cpu_limit: Optional[str] = None
    workdir: str = "/app"
    security_opts: List[str] = field(default_factory=lambda: ["no-new-privileges"])
    remove_after_run: bool = True
    
    def __post_init__(self):
        """Validate Docker configuration."""
        if not self.image:
            raise ValueError("image cannot be empty")
    
    def add_volume_mount(self, host_path: str, container_path: str, mode: str = "ro"):
        """Add a volume mount to the configuration."""
        mount = VolumeMount(host_path, container_path, mode)
        self.volume_mounts.append(mount)
    
    def to_docker_args(self) -> List[str]:
        """Convert configuration to Docker command arguments."""
        args = ["docker", "run"]
        
        if self.remove_after_run:
            args.append("--rm")
        
        # User ID
        args.extend(["--user", f"{self.user_id}:{self.user_id}"])
        
        # Working directory
        args.extend(["--workdir", self.workdir])
        
        # Security options
        for opt in self.security_opts:
            args.extend(["--security-opt", opt])
        
        # Resource limits
        if self.memory_limit:
            args.extend(["--memory", self.memory_limit])
        
        if self.cpu_limit:
            args.extend(["--cpus", self.cpu_limit])
        
        # Environment variables
        for key, value in self.environment.items():
            args.extend(["-e", f"{key}={value}"])
        
        # Volume mounts
        for mount in self.volume_mounts:
            args.extend(["-v", mount.to_docker_arg()])
        
        # Image name
        args.append(self.image)
        
        return args