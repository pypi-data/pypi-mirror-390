"""Volume Mount model for Docker volume mounting configuration."""

from dataclasses import dataclass


@dataclass
class VolumeMount:
    """Represents a Docker volume mount configuration.
    
    Attributes:
        host_path: Path on the host system
        container_path: Path inside the container
        mode: Mount mode ("ro" for read-only, "rw" for read-write)
    """
    
    host_path: str
    container_path: str
    mode: str = "ro"
    
    def __post_init__(self):
        """Validate volume mount configuration."""
        if not self.host_path:
            raise ValueError("host_path cannot be empty")
        
        if not self.container_path:
            raise ValueError("container_path cannot be empty")
        
        if self.mode not in ("ro", "rw"):
            raise ValueError("mode must be 'ro' or 'rw'")
        
        # Normalize container path
        self.container_path = self.container_path.replace("//", "/").rstrip("/")
        if not self.container_path.startswith("/"):
            self.container_path = "/" + self.container_path
    
    def to_docker_arg(self) -> str:
        """Convert to Docker -v argument format."""
        return f"{self.host_path}:{self.container_path}:{self.mode}"