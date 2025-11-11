"""ask-pydantic: CLI tool to ask questions about Pydantic AI and Logfire documentation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic_ai import Agent

__all__ = ['agent']


def __getattr__(name: str) -> Agent:
    """Lazy import of agent to avoid requiring API keys at import time."""
    if name == 'agent':
        from ask_pydantic.agent import agent
        return agent
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

