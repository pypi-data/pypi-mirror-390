"""
Safe Session - Transparent Wrapper for Agent Safety Tracking

This module provides SafeSession, a transparent wrapper that adds
safety tracking to agents without modifying their behavior.

Design Pattern: Transparent Wrapper / Decorator
SOLID: Open/Closed (extends without modifying)
"""

from dataclasses import dataclass, field
from typing import Any, Optional
import uuid
from safety.session_metrics import SessionMetrics


@dataclass
class SafeSession:
    """
    Transparent wrapper adding safety tracking to agents.

    Key Properties:
    - Does NOT modify agent behavior
    - Can be removed without breaking system
    - Passively observes and records metrics
    - Follows observer pattern

    Usage:
        session = SafeSession()
        session.set_agent(my_agent)
        # Agent works exactly as before, but now tracked

    Attributes:
        session_id: Unique identifier for this session
        metrics: Session metrics observer
        stop_requested: Whether stop has been requested
        status: Current session status
    """

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metrics: SessionMetrics = field(default_factory=SessionMetrics)
    stop_requested: bool = False
    status: str = "initializing"
    _agent: Optional[Any] = field(default=None, init=False, repr=False)

    def set_agent(self, agent: Any) -> None:
        """
        Wrap an existing agent without modifying it.

        Args:
            agent: The agent to wrap and track
        """
        self._agent = agent
        self.status = "active"

    def record_tool_call(self, tool_name: str, args: dict) -> None:
        """
        Record a tool call (passive observation).

        Args:
            tool_name: Name of tool executed
            args: Arguments passed to tool
        """
        self.metrics.record_tool_call(tool_name, args)

    def request_stop(self, reason: str = "") -> None:
        """
        Request graceful session stop.

        Args:
            reason: Optional reason for stopping
        """
        self.stop_requested = True
        self.status = "stopping"
        # Future: Log reason, create checkpoint

    def get_duration(self) -> float:
        """Get session duration in seconds."""
        return self.metrics.get_duration()

    def is_active(self) -> bool:
        """Check if session is active."""
        return self.status == "active" and not self.stop_requested

    def terminate(self, reason: str = "Timeout exceeded") -> None:
        """
        Terminate session execution.

        This is the enforcement mechanism - sets flags to stop execution.

        Args:
            reason: Reason for termination
        """
        print(f"\n[STOP] TERMINATING SESSION: {reason}")
        print(f"   Session ID: {self.session_id}")
        print(f"   Duration: {self.metrics.get_duration():.1f}s")
        print(f"   Tool calls: {len(self.metrics.tool_calls)}")

        self.status = "terminated"
        self.stop_requested = True
