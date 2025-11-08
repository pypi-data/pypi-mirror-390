import os
from typing import Optional, TYPE_CHECKING

from agency_swarm import Agent

if TYPE_CHECKING:
    from safety.safe_session import SafeSession
from agents import (
    WebSearchTool,
)
from shared.agent_utils import (
    detect_model_type,
    select_instructions_file,
    create_model_settings,
    get_model_instance,
)
from shared.system_hooks import create_message_filter_hook
from tools import (
    LS,
    Bash,
    Edit,
    ExitPlanMode,
    Git,
    Glob,
    Grep,
    MultiEdit,
    NotebookEdit,
    NotebookRead,
    Read,
    TodoWrite,
    Write,
    ClaudeWebSearch,
    WebFetch,
)

# Get the absolute path to the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

def create_planner_agent(
    model: str = "gpt-5",
    reasoning_effort: str = "low",
    session: Optional['SafeSession'] = None
) -> Agent:
    """Factory that returns a fresh PlannerAgent instance.
    Use this in tests to avoid reusing a singleton across multiple agencies.

    Args:
        model: Model name to use
        reasoning_effort: Reasoning effort level
        session: Optional SafeSession for tracking (backward compatible)
    """
    is_openai, is_claude, _ = detect_model_type(model)

    # Create message filter hook
    filter_hook = create_message_filter_hook()

    # Add SafeSessionHook if session provided (backward compatible)
    if session is not None:
        from shared.system_hooks import create_safe_session_hook, CombinedHook
        safe_hook = create_safe_session_hook(session)
        # Combine hooks using CombinedHook wrapper
        hooks = CombinedHook([filter_hook, safe_hook])
    else:
        # Just filter hook (backward compatible)
        hooks = filter_hook

    return Agent(
        name="PlannerAgent",
        description=(
            "A strategic planning and task breakdown specialist that helps organize "
            "and structure software development projects into manageable, actionable tasks. "
            "Provides clear project roadmaps and coordinates with the AgencyCodeAgent for execution."
        ),
        instructions=select_instructions_file(current_dir, model),
        model=get_model_instance(model),
        hooks=hooks,
        tools=[
            Bash,
            Glob,
            Grep,
            LS,
            ExitPlanMode,
            Read,
            Edit,
            MultiEdit,
            Write,
            NotebookRead,
            NotebookEdit,
            TodoWrite,
            Git,
            WebFetch,
        ]
        + ([WebSearchTool()] if is_openai else [])
        + ([ClaudeWebSearch] if is_claude else []),
        model_settings=create_model_settings(model, reasoning_effort),
    )


# Note: We don't create a singleton at module level to avoid circular imports.
# Use create_planner_agent() directly or import and call when needed.
