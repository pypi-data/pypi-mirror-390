"""Progress indication and feedback functionality for PDF conversion.

This module provides various progress indicators for different environments
and user preferences.
"""

import sys
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime
from typing import Optional


class ProgressIndicator(ABC):
    """Abstract base class for progress indicators."""

    @abstractmethod
    def update(self, current: int, total: int, message: str):
        """Update progress with current status.

        Args:
            current: Current progress value
            total: Total progress value
            message: Status message to display
        """
        pass

    @abstractmethod
    def finish(self, message: str = "Complete"):
        """Finish progress indication with final message.

        Args:
            message: Final completion message
        """
        pass

    @abstractmethod
    def cleanup(self):
        """Clean up progress display."""
        pass

    @staticmethod
    def create(
        show_progress: bool = True, quiet: bool = False
    ) -> Optional["ProgressIndicator"]:
        """Create appropriate progress indicator based on environment.

        Args:
            show_progress: Whether to show progress feedback
            quiet: Whether to suppress all output

        Returns:
            ProgressIndicator instance or None if disabled
        """
        if quiet or not show_progress:
            return None

        # Detect TTY for appropriate progress type
        if sys.stderr.isatty():
            return ProgressBar()
        else:
            return Spinner()


class ProgressBar(ProgressIndicator):
    """Progress bar with percentage and visual bar display."""

    def __init__(
        self, width: int = 50, show_timing: bool = True, use_unicode: bool = True
    ):
        """Initialize progress bar.

        Args:
            width: Width of progress bar in characters
            show_timing: Whether to show timing information
            use_unicode: Whether to use Unicode characters for bar
        """
        self.width = width
        self.show_timing = show_timing
        self.use_unicode = use_unicode
        self.start_time = time.time()
        self.last_update = 0.0
        self.output = sys.stderr

        # Unicode or ASCII characters for progress bar
        if use_unicode:
            self.fill_char = "█"
            self.partial_char = "▌"
            self.empty_char = "░"
        else:
            self.fill_char = "="
            self.partial_char = ">"
            self.empty_char = " "

    def update(self, current: int, total: int, message: str):
        """Update progress bar display."""
        # Throttle updates to avoid flickering
        now = time.time()
        if now - self.last_update < 0.1:  # Update max 10 times per second
            return
        self.last_update = now

        # Calculate percentage
        if total > 0:
            percentage = min(100, (current * 100) // total)
            filled_width = (current * self.width) // total
        else:
            percentage = 0
            filled_width = 0

        # Build progress bar
        filled = self.fill_char * filled_width
        empty = self.empty_char * (self.width - filled_width)
        bar = f"[{filled}{empty}]"

        # Build complete line
        line_parts = [f"\r{message}"]
        line_parts.append(f" {bar}")
        line_parts.append(f" {percentage}%")

        if total > 0:
            line_parts.append(f" ({current}/{total})")

        # Add timing information
        if self.show_timing:
            elapsed = now - self.start_time
            if elapsed > 0 and current > 0:
                rate = current / elapsed
                if rate > 0 and total > current:
                    eta = (total - current) / rate
                    line_parts.append(f" ETA: {self._format_time(eta)}")
                else:
                    line_parts.append(f" Elapsed: {self._format_time(elapsed)}")

        # Write and flush
        line = "".join(line_parts)
        self.output.write(line)
        self.output.flush()

    def finish(self, message: str = "Complete"):
        """Finish progress bar with completion message."""
        self.output.write(f"\r✓ {message}\n")
        self.output.flush()

    def cleanup(self):
        """Clean up progress bar display."""
        self.output.write("\n")
        self.output.flush()

    def _format_time(self, seconds: float) -> str:
        """Format time duration in human-readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m{secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h{minutes}m"


class Spinner(ProgressIndicator):
    """Spinning progress indicator for non-TTY environments."""

    def __init__(self):
        """Initialize spinner."""
        self.chars = ["|", "/", "-", "\\"]
        self.index = 0
        self.output = sys.stderr
        self.last_message = ""
        self.spinning = False
        self.thread = None
        self.stop_event = threading.Event()

    def update(self, current: int, total: int, message: str):
        """Update spinner with new message."""
        self.last_message = message

        if not self.spinning:
            self._start_spinning()

        # Show static progress for non-TTY
        if total > 0:
            percentage = (current * 100) // total
            self.output.write(
                f"\r{message} {self.chars[self.index]} {percentage}% ({current}/{total})"
            )
        else:
            self.output.write(f"\r{message} {self.chars[self.index]}")

        self.output.flush()
        self.index = (self.index + 1) % len(self.chars)

    def finish(self, message: str = "Done!"):
        """Finish spinner with completion message."""
        self._stop_spinning()
        self.output.write(f"\r✓ {message}\n")
        self.output.flush()

    def cleanup(self):
        """Clean up spinner display."""
        self._stop_spinning()
        self.output.write("\n")
        self.output.flush()

    def _start_spinning(self):
        """Start background spinning animation."""
        if self.spinning:
            return

        self.spinning = True
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._spin_loop, daemon=True)
        self.thread.start()

    def _stop_spinning(self):
        """Stop background spinning animation."""
        if not self.spinning:
            return

        self.spinning = False
        self.stop_event.set()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)

    def _spin_loop(self):
        """Background spinning animation loop."""
        while not self.stop_event.wait(0.2):  # Update every 200ms
            if self.last_message:
                self.output.write(f"\r{self.last_message} {self.chars[self.index]}")
                self.output.flush()
                self.index = (self.index + 1) % len(self.chars)


class ConversionProgress:
    """Tracks progress during conversion process with callback support."""

    def __init__(
        self,
        callback: Callable[[int, int, str], None] | None = None,
        error_callback: Callable[[str], None] | None = None,
    ):
        """Initialize conversion progress tracker.

        Args:
            callback: Optional callback function for progress updates (current, total, message)
            error_callback: Optional callback function for error reporting (message)
        """
        self.current_step = 0
        self.total_steps = 0
        self.current_message = ""
        self.callback = callback
        self.error_callback = error_callback
        self.start_time: datetime | None = None

    def set_total_steps(self, total: int):
        """Set the total number of steps."""
        self.total_steps = total
        if self.start_time is None:
            self.start_time = datetime.now()

    def advance_step(self, message: str):
        """Advance to the next step with a status message."""
        self.current_step += 1
        self.current_message = message

        if self.callback:
            self.callback(self.current_step, self.total_steps, message)

    def update_progress(self, current: int, message: str):
        """Update progress with specific step number."""
        self.current_step = current
        self.current_message = message

        if self.callback:
            self.callback(current, self.total_steps, message)

    def report_error(self, message: str):
        """Report an error during processing."""
        if self.error_callback:
            self.error_callback(message)

    def start_timing(self):
        """Start timing the process."""
        self.start_time = datetime.now()

    def get_processing_rate(self) -> float | None:
        """Get processing rate in items per second."""
        if not self.start_time or self.current_step == 0:
            return None

        elapsed = (datetime.now() - self.start_time).total_seconds()
        if elapsed == 0:
            return None

        return self.current_step / elapsed

    def is_complete(self) -> bool:
        """Check if processing is complete."""
        return self.current_step >= self.total_steps


class QuietProgress(ProgressIndicator):
    """No-op progress indicator for quiet mode."""

    def update(self, current: int, total: int, message: str):
        """No-op update."""
        pass

    def finish(self, message: str = "Complete"):
        """No-op finish."""
        pass

    def cleanup(self):
        """No-op cleanup."""
        pass


# Backwards compatibility
def create_progress_indicator(
    show_progress: bool = True, quiet: bool = False
) -> ProgressIndicator | None:
    """Create appropriate progress indicator (backwards compatibility function)."""
    return ProgressIndicator.create(show_progress, quiet)
