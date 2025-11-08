"""
Session Metrics - Passive Observer of Agent Activity

This module provides SessionMetrics, a dataclass that tracks
agent activity without interfering with execution.

Design Pattern: Observer (passive monitoring)
SOLID: Single Responsibility (only tracks metrics)
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Any
import time


@dataclass
class SessionMetrics:
    """
    Passive observer of session activity.

    Tracks metrics without interfering with agent execution.
    Can be removed without breaking the system.

    Attributes:
        tool_calls: List of (tool_name, args, timestamp) tuples
        reasoning_steps: Count of reasoning iterations
        handoff_count: Number of agent-to-agent handoffs
        memory_peak: Peak memory usage in bytes
        disk_used: Disk space used in bytes
        started_at: Unix timestamp when session started
    """

    tool_calls: List[Tuple[str, dict, float]] = field(default_factory=list)
    reasoning_steps: int = 0
    handoff_count: int = 0
    memory_peak: int = 0
    disk_used: int = 0
    started_at: float = field(default_factory=time.time)

    def record_tool_call(self, tool_name: str, args: dict) -> None:
        """
        Record a tool execution.

        Args:
            tool_name: Name of the tool executed
            args: Arguments passed to the tool
        """
        timestamp = time.time()
        self.tool_calls.append((tool_name, args, timestamp))

    def get_duration(self) -> float:
        """
        Get session duration in seconds.

        Returns:
            Number of seconds since session started
        """
        return time.time() - self.started_at

    def increment_reasoning_steps(self) -> None:
        """Increment reasoning step counter."""
        self.reasoning_steps += 1

    def record_handoff(self, from_agent: str, to_agent: str) -> None:
        """
        Record agent-to-agent handoff.

        Args:
            from_agent: Agent initiating handoff
            to_agent: Agent receiving handoff
        """
        self.handoff_count += 1
        # Future: Track handoff chain
