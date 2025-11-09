"""Conversion Progress model for tracking conversion progress."""

from dataclasses import dataclass
from typing import Optional, Callable
from datetime import datetime


@dataclass
class ConversionProgress:
    """Tracks progress during conversion process.
    
    Attributes:
        current_step: Current step number (0-based)
        total_steps: Total number of steps
        current_message: Current status message
        callback: Optional callback function for progress updates
        error_callback: Optional callback function for error reporting
        start_time: When processing started
    """
    
    current_step: int = 0
    total_steps: int = 0
    current_message: str = ""
    callback: Optional[Callable] = None
    error_callback: Optional[Callable] = None
    start_time: Optional[datetime] = None
    
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
    
    def get_processing_rate(self) -> Optional[float]:
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