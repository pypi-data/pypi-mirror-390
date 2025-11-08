"""
Graceful cancellation for SafeSession.

Design: Signal handler for Ctrl+C (SIGINT) that saves state before exit.
Phase: Phase 4 - Enforcement layer
"""

import signal
import sys
from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from safety.safe_session import SafeSession


class CancellationHandler:
    """
    Handle graceful cancellation (Ctrl+C).

    Design Philosophy:
    - Catch SIGINT (Ctrl+C)
    - Request session stop
    - Perform cleanup
    - Save state
    - Exit gracefully

    Usage:
        session = SafeSession()
        handler = CancellationHandler(session)
        handler.install()  # Install signal handler

        # ... agency runs ...

        # On Ctrl+C, handler triggers cleanup
    """

    def __init__(self, session: 'SafeSession'):
        """
        Initialize cancellation handler.

        Args:
            session: SafeSession to manage
        """
        self.session = session
        self.cancellation_requested = False
        self._original_handler = None

    def install(self) -> None:
        """Install Ctrl+C signal handler"""
        self._original_handler = signal.signal(signal.SIGINT, self._signal_handler)

    def uninstall(self) -> None:
        """Restore original signal handler"""
        if self._original_handler:
            signal.signal(signal.SIGINT, self._original_handler)

    def _signal_handler(self, signum, frame):
        """Handle SIGINT (Ctrl+C)"""
        print("\n\n[STOP] Cancellation requested (Ctrl+C)")
        print("[...] Shutting down gracefully...")

        self.request_cancellation("User pressed Ctrl+C")

        # Perform cleanup
        result = self.cleanup()

        print(f"\n[OK] Session {result['session_id']} cancelled")
        print(f"   Duration: {result['duration']:.1f}s")
        print(f"   Tool calls: {result['tool_calls']}")
        print(f"   Reasoning steps: {result['reasoning_steps']}")

        sys.exit(0)

    def request_cancellation(self, reason: str = "") -> None:
        """Request session cancellation"""
        self.cancellation_requested = True
        self.session.request_stop(reason)
        if reason:
            print(f"   Reason: {reason}")

    def cleanup(self) -> Dict:
        """
        Perform cleanup and return session summary.

        Returns:
            Dict with session summary
        """
        try:
            summary = {
                "session_id": self.session.session_id,
                "duration": self.session.metrics.get_duration(),
                "tool_calls": len(self.session.metrics.tool_calls),
                "reasoning_steps": self.session.metrics.reasoning_steps,
                "handoffs": self.session.metrics.handoff_count,
                "status": self.session.status
            }

            return summary

        except Exception as e:
            print(f"Warning: Cleanup error: {e}")
            return {
                "session_id": self.session.session_id if self.session else "unknown",
                "error": str(e)
            }
