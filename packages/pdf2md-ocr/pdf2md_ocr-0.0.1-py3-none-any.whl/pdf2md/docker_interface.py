"""Docker interface for PDF2MD container operations.

This module provides Docker integration functionality including volume mounting,
command generation, and container execution management.
"""

import subprocess
import time
from pathlib import Path

from .exceptions import docker_not_available
from .models import ConversionResult, DockerConfig, VolumeMount


class DockerInterface:
    """Interface for Docker container operations."""

    def __init__(self):
        """Initialize Docker interface."""
        self.validate_docker_available()

    def validate_docker_available(self):
        """Validate that Docker is available and running."""
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                raise docker_not_available()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            raise docker_not_available()

    def create_volume_mount(
        self, host_path: str, container_path: str, mode: str = "ro"
    ) -> VolumeMount:
        """Create a volume mount configuration.

        Args:
            host_path: Path on the host system
            container_path: Path inside the container
            mode: Mount mode ("ro" for read-only, "rw" for read-write)

        Returns:
            VolumeMount configuration

        Raises:
            FileNotFoundError: If host path doesn't exist
            ValueError: If mount configuration is invalid
        """
        # Validate host path exists
        host_path_obj = Path(host_path)
        if not host_path_obj.exists():
            raise FileNotFoundError(f"Host path does not exist: {host_path}")

        # Convert to absolute path
        abs_host_path = str(host_path_obj.resolve())

        return VolumeMount(
            host_path=abs_host_path, container_path=container_path, mode=mode
        )

    def build_run_command(
        self,
        image: str,
        volume_mounts: list[VolumeMount],
        args: list[str],
        user_id: int | None = None,
        environment: dict[str, str] | None = None,
        memory_limit: str | None = None,
        cpu_limit: str | None = None,
        workdir: str | None = None,
        security_opts: list[str] | None = None,
    ) -> list[str]:
        """Build Docker run command with all options.

        Args:
            image: Docker image name
            volume_mounts: List of volume mount configurations
            args: Command arguments to pass to container
            user_id: User ID for container execution
            environment: Environment variables
            memory_limit: Memory limit (e.g., "1g", "512m")
            cpu_limit: CPU limit (e.g., "2", "0.5")
            workdir: Working directory inside container
            security_opts: Security options

        Returns:
            Complete Docker command as list of strings
        """
        command = ["docker", "run", "--rm"]

        # User ID mapping
        if user_id is not None:
            command.extend(["--user", f"{user_id}:{user_id}"])

        # Working directory
        if workdir:
            command.extend(["--workdir", workdir])

        # Security options
        if security_opts:
            for opt in security_opts:
                command.extend(["--security-opt", opt])

        # Resource limits
        if memory_limit:
            command.extend(["--memory", memory_limit])

        if cpu_limit:
            command.extend(["--cpus", cpu_limit])

        # Environment variables
        if environment:
            for key, value in environment.items():
                command.extend(["-e", f"{key}={value}"])

        # Volume mounts
        for mount in volume_mounts:
            command.extend(["-v", mount.to_docker_arg()])

        # Image name
        command.append(image)

        # Command arguments
        command.extend(args)

        return command

    def execute_conversion(
        self,
        image: str,
        input_mount: VolumeMount,
        output_mount: VolumeMount,
        pdf_filename: str,
        **kwargs,
    ) -> ConversionResult:
        """Execute PDF conversion in Docker container.

        Args:
            image: Docker image name
            input_mount: Input volume mount
            output_mount: Output volume mount
            pdf_filename: Name of PDF file to convert
            **kwargs: Additional Docker options

        Returns:
            ConversionResult with execution details
        """
        start_time = time.time()

        # Build conversion arguments
        container_input_path = f"{input_mount.container_path}/{pdf_filename}"
        container_output_path = output_mount.container_path

        conversion_args = [
            "--input",
            container_input_path,
            "--output",
            container_output_path,
        ]

        # Add optional arguments
        if kwargs.get("progress"):
            conversion_args.append("--progress")

        if kwargs.get("format"):
            conversion_args.extend(["--format", kwargs["format"]])

        if kwargs.get("max_pages"):
            conversion_args.extend(["--max-pages", str(kwargs["max_pages"])])

        if kwargs.get("quiet"):
            conversion_args.append("--quiet")

        # Build Docker command
        docker_command = self.build_run_command(
            image=image,
            volume_mounts=[input_mount, output_mount],
            args=conversion_args,
            user_id=kwargs.get("user_id", 1000),
            environment=kwargs.get("environment"),
            memory_limit=kwargs.get("memory_limit"),
            cpu_limit=kwargs.get("cpu_limit"),
            workdir=kwargs.get("workdir", "/app"),
            security_opts=kwargs.get("security_opts", ["no-new-privileges"]),
        )

        # Execute Docker command
        try:
            result = subprocess.run(
                docker_command,
                capture_output=True,
                text=True,
                timeout=kwargs.get("timeout", 1800),  # 30 minute default timeout
            )

            execution_time = time.time() - start_time

            # Create result
            conversion_result = ConversionResult(
                success=(result.returncode == 0),
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                docker_command=docker_command,
            )

            # Set error message if failed
            if not conversion_result.success:
                conversion_result.error_message = self._parse_error_message(result)

            return conversion_result

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return ConversionResult(
                success=False,
                exit_code=124,  # Timeout exit code
                execution_time=execution_time,
                error_message="Container execution timed out",
                docker_command=docker_command,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return ConversionResult(
                success=False,
                exit_code=1,
                execution_time=execution_time,
                error_message=f"Docker execution failed: {str(e)}",
                docker_command=docker_command,
            )

    def _parse_error_message(self, result: subprocess.CompletedProcess) -> str:
        """Parse error message from Docker execution result."""
        if result.stderr:
            error_msg = result.stderr.strip()

            # Extract meaningful error messages
            if "No such file or directory" in error_msg:
                return "Input file not found or output directory not accessible"
            elif "Permission denied" in error_msg:
                return "Permission denied accessing files or directories"
            elif "No space left on device" in error_msg:
                return "Insufficient disk space for output files"
            elif "PDF is encrypted" in error_msg:
                return "PDF is encrypted and requires a password"
            elif "Out of memory" in error_msg or "MemoryError" in error_msg:
                return "Insufficient memory to process PDF"
            else:
                return error_msg

        elif result.stdout:
            return result.stdout.strip()

        else:
            return f"Container exited with code {result.returncode}"

    def pull_image(self, image: str) -> bool:
        """Pull Docker image if not available locally.

        Args:
            image: Docker image name to pull

        Returns:
            True if image is available, False otherwise
        """
        try:
            # Check if image exists locally
            result = subprocess.run(
                ["docker", "image", "inspect", image], capture_output=True, timeout=10
            )

            if result.returncode == 0:
                return True  # Image exists locally

            # Try to pull image
            result = subprocess.run(
                ["docker", "pull", image],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout for pulling
            )

            return result.returncode == 0

        except (subprocess.TimeoutExpired, Exception):
            return False

    def get_image_info(self, image: str) -> dict[str, str] | None:
        """Get information about Docker image.

        Args:
            image: Docker image name

        Returns:
            Dictionary with image information or None if not found
        """
        try:
            result = subprocess.run(
                [
                    "docker",
                    "image",
                    "inspect",
                    image,
                    "--format",
                    "{{.Id}};{{.Created}};{{.Size}};{{.Architecture}}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                parts = result.stdout.strip().split(";")
                if len(parts) >= 4:
                    return {
                        "id": parts[0],
                        "created": parts[1],
                        "size": parts[2],
                        "architecture": parts[3],
                    }

            return None

        except (subprocess.TimeoutExpired, Exception):
            return None


class ContainerManager:
    """Manager for Docker container lifecycle operations."""

    def __init__(self, docker_interface: DockerInterface):
        """Initialize container manager.

        Args:
            docker_interface: Docker interface to use
        """
        self.docker = docker_interface
        self.running_containers: list[str] = []

    def create_conversion_container(
        self, image: str, input_path: str, output_path: str, **options
    ) -> DockerConfig:
        """Create Docker configuration for PDF conversion.

        Args:
            image: Docker image name
            input_path: Host path for input files
            output_path: Host path for output files
            **options: Additional configuration options

        Returns:
            DockerConfig for the conversion
        """
        config = DockerConfig(image=image)

        # Add volume mounts
        input_mount = self.docker.create_volume_mount(
            host_path=input_path, container_path="/app/input", mode="ro"
        )
        output_mount = self.docker.create_volume_mount(
            host_path=output_path, container_path="/app/output", mode="rw"
        )

        config.volume_mounts = [input_mount, output_mount]

        # Apply options
        config.user_id = options.get("user_id", 1000)
        config.memory_limit = options.get("memory_limit")
        config.cpu_limit = options.get("cpu_limit")
        config.workdir = options.get("workdir", "/app")

        # Environment variables
        if options.get("environment"):
            config.environment.update(options["environment"])

        return config

    def cleanup_containers(self):
        """Clean up any running containers."""
        for container_id in self.running_containers:
            try:
                subprocess.run(
                    ["docker", "stop", container_id], capture_output=True, timeout=30
                )
            except Exception:
                pass  # Best effort cleanup

        self.running_containers.clear()


# Global Docker interface instance
_docker_interface = None


def get_docker_interface() -> DockerInterface:
    """Get global Docker interface instance."""
    global _docker_interface
    if _docker_interface is None:
        _docker_interface = DockerInterface()
    return _docker_interface
