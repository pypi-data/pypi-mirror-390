import os

from shared.utils import silence_warnings_and_logs

silence_warnings_and_logs()

import litellm  # noqa: E402 - must import after warning suppression
from agency_swarm import Agency  # noqa: E402 - must import after warning suppression
from agency_swarm.tools import (
    SendMessageHandoff,  # noqa: E402 - must import after warning suppression
)
from dotenv import load_dotenv  # noqa: E402 - must import after warning suppression

from agency_code_agent.agency_code_agent import (  # noqa: E402 - must import after warning suppression
    create_agency_code_agent,
)
from planner_agent.planner_agent import (  # noqa: E402 - must import after warning suppression
    create_planner_agent,
)
from subagent_example.subagent_example import (  # noqa: E402 - must import after warning suppression
    create_subagent_example,
)

load_dotenv()


def main():
    """Main entry point for the aria CLI command."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    litellm.modify_params = True

    # switch between models here
    # model = "anthropic/claude-sonnet-4-20250514"
    model = "anthropic/claude-haiku-4-5-20251001"  # Cost-efficient Claude Haiku 4.5

    # SafeSession tracking (optional - can be disabled via env var)
    USE_SAFE_SESSION = os.getenv("USE_SAFE_SESSION", "true").lower() == "true"

    if USE_SAFE_SESSION:
        from safety.safe_session import SafeSession
        session = SafeSession()
        print(f"\n[SafeSession] [OK] Session tracking enabled")
        print(f"[SafeSession] Session ID: {session.session_id}\n")
    else:
        session = None
        print("\n[SafeSession] [WARN] Session tracking disabled\n")

    # create agents (pass session if enabled)
    planner = create_planner_agent(
        model=model, reasoning_effort="low", session=session
    )
    # coder = create_agency_code_agent(model="gpt-5", reasoning_effort="high")
    coder = create_agency_code_agent(
        model=model, reasoning_effort="high", session=session
    )
    subagent_example = create_subagent_example(
        model=model, reasoning_effort="high"
    )

    agency = Agency(
        coder, planner,
        name="AgencyCode",
        communication_flows=[
            (coder, planner, SendMessageHandoff),
            (planner, coder, SendMessageHandoff),
            # (coder, subagent_example) # example for how to add a subagent
        ],
        shared_instructions="./project-overview.md",
    )

    # Display session info if enabled
    if USE_SAFE_SESSION and session:
        print(f"[SafeSession] [TRACKING] Session: {session.session_id}")
        print(f"[SafeSession] Status: {session.status}\n")

    agency.terminal_demo(show_reasoning=False if model.startswith("anthropic") else True)
    # agency.visualize()


if __name__ == "__main__":
    main()
