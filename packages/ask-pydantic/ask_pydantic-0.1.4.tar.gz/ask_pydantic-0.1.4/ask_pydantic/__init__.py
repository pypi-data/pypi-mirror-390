"""ask-pydantic: CLI tool to ask questions about Pydantic AI and Logfire documentation."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pydantic_ai import Agent

__all__ = ['agent']


class _LazyAgentLoader:
    """Lazy loader for the agent to avoid requiring API keys at import time."""

    _agent: Agent | None = None

    def __getattr__(self, name: str) -> Any:
        """Load the actual agent on first access."""
        if self._agent is None:
            from ask_pydantic._agent import agent as _agent_instance
            self._agent = _agent_instance
        return getattr(self._agent, name)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Support calling methods on the agent."""
        if self._agent is None:
            from ask_pydantic._agent import agent as _agent_instance
            self._agent = _agent_instance
        return self._agent(*args, **kwargs)


# Replace the agent module with our lazy loader in sys.modules
# This makes "from ask_pydantic import agent" work correctly
_lazy_agent = _LazyAgentLoader()
sys.modules['ask_pydantic'].agent = _lazy_agent  # type: ignore

