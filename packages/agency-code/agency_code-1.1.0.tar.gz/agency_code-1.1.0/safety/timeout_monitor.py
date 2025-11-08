"""
Timeout monitoring for SafeSession.

Design: Passive observer pattern - monitors timeouts but doesn't kill processes.
Phase: Phase 3 - Observation only (enforcement in future phase)
"""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from safety.safe_session import SafeSession


@dataclass
class TimeoutConfig:
    """
    Configuration for timeout monitoring.

    Default values are conservative to avoid false positives.
    """
    # Session-level timeout (30 minutes default)
    max_session_duration: int = 1800  # seconds

    # Turn-level timeout (5 minutes default)
    turn_timeout: int = 300  # seconds

    # Tool-level timeout (2 minutes default)
    tool_timeout: int = 120  # seconds

    # Warning thresholds (percentages)
    warning_threshold_75: float = 0.75
    warning_threshold_90: float = 0.90


class TimeoutMonitor:
    """
    Passive timeout observer for SafeSession.

    Design Philosophy:
    - OBSERVE timeout status, don't enforce (yet)
    - Return warnings as strings
    - Don't modify session state
    - Don't kill processes
    - Graceful degradation on errors

    Usage:
        session = SafeSession()
        config = TimeoutConfig()
        monitor = TimeoutMonitor(session, config)

        # Periodically check
        warning = monitor.check_timeout()
        if warning:
            print(f"Warning: {warning}")
    """

    def __init__(self, session: 'SafeSession', config: TimeoutConfig):
        """
        Initialize timeout monitor.

        Args:
            session: SafeSession to monitor
            config: Timeout configuration
        """
        self.session = session
        self.config = config
        self.warnings_sent: list[str] = []

    def check_timeout(self) -> Optional[str]:
        """
        Check if session approaching or exceeded timeout.

        Returns:
            Warning string if approaching/exceeded, None otherwise
        """
        try:
            elapsed = self.session.metrics.get_duration()
            max_duration = self.config.max_session_duration

            # Check if exceeded
            if elapsed > max_duration:
                return self._format_timeout_exceeded(elapsed, max_duration)

            # Check 90% threshold
            threshold_90 = max_duration * self.config.warning_threshold_90
            if elapsed > threshold_90:
                if "90%" not in self.warnings_sent:
                    self.warnings_sent.append("90%")
                    return self._format_warning(elapsed, max_duration, 90)

            # Check 75% threshold
            threshold_75 = max_duration * self.config.warning_threshold_75
            if elapsed > threshold_75:
                if "75%" not in self.warnings_sent:
                    self.warnings_sent.append("75%")
                    return self._format_warning(elapsed, max_duration, 75)

            return None

        except Exception as e:
            # Graceful degradation - don't break execution
            print(f"Warning: TimeoutMonitor.check_timeout() failed: {e}")
            return None

    def _format_warning(self, elapsed: float, max_duration: int, percent: int) -> str:
        """Format warning message for threshold"""
        return (
            f"WARNING: Session at {percent}% of timeout "
            f"({elapsed:.0f}s / {max_duration}s)"
        )

    def _format_timeout_exceeded(self, elapsed: float, max_duration: int) -> str:
        """Format timeout exceeded message"""
        return (
            f"TIMEOUT: Session exceeded maximum duration "
            f"({elapsed:.0f}s / {max_duration}s)"
        )

    def get_time_remaining(self) -> float:
        """
        Get time remaining before timeout.

        Returns:
            Seconds remaining (negative if exceeded)
        """
        try:
            elapsed = self.session.metrics.get_duration()
            return self.config.max_session_duration - elapsed
        except Exception as e:
            print(f"Warning: TimeoutMonitor.get_time_remaining() failed: {e}")
            return 0.0

    def reset_warnings(self) -> None:
        """Reset warning state (useful for testing or session restart)"""
        self.warnings_sent = []
