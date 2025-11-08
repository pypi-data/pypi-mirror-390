"""
Background monitoring for SafeSession enforcement.

Design: Separate thread that periodically checks timeout/runaway status.
Phase: Phase 4 - Active enforcement (can trigger termination)
"""

import threading
import time
from dataclasses import dataclass
from typing import Optional, Callable, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from safety.safe_session import SafeSession
    from safety.timeout_monitor import TimeoutConfig


class EventType(Enum):
    """Monitor event types"""
    TIMEOUT = "timeout"
    RUNAWAY = "runaway"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class MonitorEvent:
    """Event emitted by background monitor"""
    event_type: str
    message: str
    severity: str  # "low", "medium", "high"
    data: dict


class BackgroundMonitor:
    """
    Background monitoring task for SafeSession.

    Design Philosophy:
    - Runs in separate thread (doesn't block main)
    - Checks timeout/runaway periodically
    - Emits events (doesn't enforce directly)
    - Clean shutdown (no thread leaks)
    - Graceful error handling

    Usage:
        session = SafeSession()
        config = TimeoutConfig()
        monitor = BackgroundMonitor(session, config)

        def on_event(event: MonitorEvent):
            print(f"Event: {event.event_type} - {event.message}")

        monitor.on_event = on_event
        monitor.start()

        # ... agency.terminal_demo() runs ...

        monitor.stop()
    """

    def __init__(
        self,
        session: 'SafeSession',
        config: 'TimeoutConfig',
        check_interval: float = 5.0,
        auto_terminate: bool = False
    ):
        """
        Initialize background monitor.

        Args:
            session: SafeSession to monitor
            config: TimeoutConfig for timeout thresholds
            check_interval: Seconds between checks (default 5.0)
            auto_terminate: If True, automatically terminate on timeout (default False)
        """
        self.session = session
        self.config = config
        self.check_interval = check_interval
        self.auto_terminate = auto_terminate

        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Event callback (set by user)
        self.on_event: Optional[Callable[[MonitorEvent], None]] = None

    def start(self) -> None:
        """Start background monitoring"""
        if self.is_running:
            return

        self.is_running = True
        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="SafeSessionMonitor"
        )
        self._thread.start()

    def stop(self) -> None:
        """Stop background monitoring"""
        if not self.is_running:
            return

        self.is_running = False
        self._stop_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def _monitor_loop(self) -> None:
        """Main monitoring loop (runs in separate thread)"""
        try:
            while not self._stop_event.is_set():
                self._check_session()

                # Sleep with ability to wake on stop
                self._stop_event.wait(self.check_interval)

        except Exception as e:
            # Graceful degradation - don't crash monitor
            self._emit_event(MonitorEvent(
                event_type=EventType.ERROR.value,
                message=f"Monitor loop error: {e}",
                severity="high",
                data={"error": str(e)}
            ))

    def _check_session(self) -> None:
        """Check session for timeout/runaway conditions"""
        try:
            from safety.timeout_monitor import TimeoutMonitor
            from safety.runaway_detector import RunawayDetector

            # Check timeout
            timeout_monitor = TimeoutMonitor(self.session, self.config)
            warning = timeout_monitor.check_timeout()
            if warning:
                severity = "high" if "TIMEOUT" in warning else "medium"
                self._emit_event(MonitorEvent(
                    event_type=EventType.TIMEOUT.value,
                    message=warning,
                    severity=severity,
                    data={
                        "elapsed": self.session.metrics.get_duration(),
                        "max_duration": self.config.max_session_duration
                    }
                ))

                # Auto-terminate if enabled and timeout exceeded
                if self.auto_terminate and "TIMEOUT" in warning:
                    self.session.terminate("Session timeout exceeded")

            # Check runaway patterns
            runaway_detector = RunawayDetector(self.session)
            pattern = runaway_detector.detect_pattern()
            if pattern:
                message = runaway_detector.get_detection_message(pattern)
                self._emit_event(MonitorEvent(
                    event_type=EventType.RUNAWAY.value,
                    message=message,
                    severity="high",
                    data={
                        "pattern": pattern.value,
                        "details": runaway_detector.get_pattern_details()
                    }
                ))

                # Auto-terminate if enabled and runaway detected
                if self.auto_terminate:
                    self.session.terminate(f"Runaway pattern detected: {pattern.value}")

        except Exception as e:
            # Graceful degradation
            self._emit_event(MonitorEvent(
                event_type=EventType.ERROR.value,
                message=f"Check session error: {e}",
                severity="low",
                data={"error": str(e)}
            ))

    def _emit_event(self, event: MonitorEvent) -> None:
        """Emit event to callback"""
        try:
            if self.on_event:
                self.on_event(event)
        except Exception as e:
            # Don't let callback errors crash monitor
            print(f"Warning: Event callback error: {e}")
