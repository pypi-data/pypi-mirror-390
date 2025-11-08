"""
Runaway pattern detection for SafeSession.

Design: Passive observer - detects patterns but doesn't intervene.
Phase: Phase 3 - Observation only (intervention in future phase)
"""

from enum import Enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from safety.safe_session import SafeSession


class RunawayPattern(Enum):
    """Detected runaway patterns"""
    INFINITE_TOOL_LOOP = "infinite_tool_loop"
    EXCESSIVE_REASONING = "excessive_reasoning"
    ESCALATION_SPIRAL = "escalation_spiral"


class RunawayDetector:
    """
    Detect runaway patterns in agent execution.

    Design Philosophy:
    - OBSERVE patterns, don't intervene (yet)
    - Return pattern enum if detected
    - Don't modify session state
    - No false positives on normal complex tasks
    - Graceful degradation on errors

    Patterns Detected:
    1. Infinite Tool Loop: Same tool called N+ times in a row
    2. Excessive Reasoning: Too many reasoning steps without tool calls
    3. Escalation Spiral: Too many agent handoffs

    Usage:
        session = SafeSession()
        detector = RunawayDetector(session)

        # Periodically check
        pattern = detector.detect_pattern()
        if pattern:
            print(f"Detected: {detector.get_detection_message(pattern)}")
    """

    def __init__(
        self,
        session: 'SafeSession',
        same_tool_threshold: int = 5,
        reasoning_threshold: int = 50,
        handoff_threshold: int = 10
    ):
        """
        Initialize runaway detector.

        Args:
            session: SafeSession to monitor
            same_tool_threshold: How many same tool calls = runaway (default 5)
            reasoning_threshold: How many reasoning steps = excessive (default 50)
            handoff_threshold: How many handoffs = spiral (default 10)
        """
        self.session = session
        self.same_tool_threshold = same_tool_threshold
        self.reasoning_threshold = reasoning_threshold
        self.handoff_threshold = handoff_threshold

    def detect_pattern(self) -> Optional[RunawayPattern]:
        """
        Detect runaway patterns from session metrics.

        Returns:
            RunawayPattern enum if detected, None otherwise
        """
        try:
            metrics = self.session.metrics

            # Pattern 1: Infinite Tool Loop
            # Same tool called N+ times in a row
            if len(metrics.tool_calls) >= self.same_tool_threshold:
                recent_calls = metrics.tool_calls[-self.same_tool_threshold:]
                # Check if all recent calls are the same tool
                first_tool = recent_calls[0][0]
                if all(call[0] == first_tool for call in recent_calls):
                    return RunawayPattern.INFINITE_TOOL_LOOP

            # Pattern 2: Excessive Reasoning
            # Too many reasoning steps without progress
            if metrics.reasoning_steps > self.reasoning_threshold:
                return RunawayPattern.EXCESSIVE_REASONING

            # Pattern 3: Escalation Spiral
            # Too many agent handoffs
            if metrics.handoff_count > self.handoff_threshold:
                return RunawayPattern.ESCALATION_SPIRAL

            return None

        except Exception as e:
            # Graceful degradation
            print(f"Warning: RunawayDetector.detect_pattern() failed: {e}")
            return None

    def get_detection_message(self, pattern: Optional[RunawayPattern]) -> str:
        """
        Get human-readable message for detected pattern.

        Args:
            pattern: Detected pattern (or None)

        Returns:
            Human-readable message string
        """
        if pattern is None:
            return "No runaway pattern detected"

        messages = {
            RunawayPattern.INFINITE_TOOL_LOOP:
                f"Same tool called {self.same_tool_threshold}+ times in a row",
            RunawayPattern.EXCESSIVE_REASONING:
                f"More than {self.reasoning_threshold} reasoning steps without progress",
            RunawayPattern.ESCALATION_SPIRAL:
                f"More than {self.handoff_threshold} agent handoffs detected"
        }

        return messages.get(pattern, "Unknown runaway pattern")

    def get_pattern_details(self) -> dict:
        """
        Get detailed information about current session state.

        Returns:
            Dict with pattern detection details
        """
        try:
            metrics = self.session.metrics

            # Analyze tool call patterns
            recent_tool_pattern = None
            if len(metrics.tool_calls) >= self.same_tool_threshold:
                recent_calls = metrics.tool_calls[-self.same_tool_threshold:]
                recent_tool_pattern = [call[0] for call in recent_calls]

            return {
                "total_tool_calls": len(metrics.tool_calls),
                "recent_tool_pattern": recent_tool_pattern,
                "reasoning_steps": metrics.reasoning_steps,
                "handoff_count": metrics.handoff_count,
                "thresholds": {
                    "same_tool": self.same_tool_threshold,
                    "reasoning": self.reasoning_threshold,
                    "handoffs": self.handoff_threshold
                }
            }
        except Exception as e:
            print(f"Warning: RunawayDetector.get_pattern_details() failed: {e}")
            return {}
