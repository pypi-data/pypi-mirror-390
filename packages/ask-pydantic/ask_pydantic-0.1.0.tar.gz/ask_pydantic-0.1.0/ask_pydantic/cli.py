"""CLI entry point for ask-pydantic."""

from __future__ import annotations as _annotations

import argparse
import asyncio
import os
import sys

from ask_pydantic.data import prompt_and_clone_docs


def check_api_keys() -> tuple[bool, str | None]:
    """
    Check if any supported API keys are set.
    Returns (has_key, provider_name).
    """
    supported_keys = {
        'ANTHROPIC_API_KEY': 'Anthropic (Claude)',
        'OPENAI_API_KEY': 'OpenAI (GPT)',
        'GOOGLE_API_KEY': 'Google (Gemini)',
        'MISTRAL_API_KEY': 'Mistral',
        'GROQ_API_KEY': 'Groq',
    }

    # Check which keys are set
    for key, provider in supported_keys.items():
        if os.getenv(key):
            return True, provider

    return False, None


def print_api_key_error():
    """Print helpful error message about missing API keys."""
    print('\n❌ No API keys found!')
    print('\nask-pydantic requires at least one LLM API key to be set.')
    print('Supported providers:\n')

    supported_keys = {
        'ANTHROPIC_API_KEY': 'Anthropic (Claude)',
        'OPENAI_API_KEY': 'OpenAI (GPT)',
        'GOOGLE_API_KEY': 'Google (Gemini)',
        'MISTRAL_API_KEY': 'Mistral',
        'GROQ_API_KEY': 'Groq',
    }

    for key, provider in supported_keys.items():
        print(f'  {provider}:')
        print(f'    export {key}="your-key-here"')
        print()

    print('💡 Tip: Add your API key to a .env file and run:')
    print('   source .env && ask-pydantic "your question"')


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Ask questions about Pydantic AI and Logfire documentation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ask-pydantic "How do I create an agent?"
  ask-pydantic "What is Logfire?"
  ask-pydantic "How do I use tools with Pydantic AI?"
        """,
    )
    parser.add_argument(
        'question',
        nargs='?',
        help='Your question about Pydantic AI or Logfire',
    )

    args = parser.parse_args()

    # Show help if no question provided
    if not args.question:
        parser.print_help()
        sys.exit(0)

    # Check for API keys
    has_key, provider = check_api_keys()
    if not has_key:
        print_api_key_error()
        sys.exit(1)

    print(f'🔑 Using {provider}')

    # Check if docs exist, prompt to download if needed
    if not prompt_and_clone_docs():
        sys.exit(1)

    # Import agent here (after docs are ready) to avoid initialization errors
    try:
        from ask_pydantic.agent import agent
    except Exception as e:
        print(f'\n❌ Failed to load agent: {e}')
        sys.exit(1)

    # Run the agent with the question
    print(f'\n🤔 Question: {args.question}')
    print('\n💬 Answer:\n')

    async def run_agent():
        """Run the agent with proper streaming including tool calls."""
        from pydantic_ai.messages import (
            PartStartEvent,
            PartDeltaEvent,
            TextPart,
            TextPartDelta,
        )

        async for event in agent.run_stream_events(args.question):
            # Handle initial text chunks (PartStartEvent with TextPart)
            if isinstance(event, PartStartEvent):
                if isinstance(event.part, TextPart):
                    print(event.part.content, end='', flush=True)
            # Handle subsequent text chunks (PartDeltaEvent with TextPartDelta)
            elif isinstance(event, PartDeltaEvent):
                if isinstance(event.delta, TextPartDelta):
                    print(event.delta.content_delta, end='', flush=True)
        print('\n')

    try:
        # Stream the response for better UX using event streaming
        asyncio.run(run_agent())
    except Exception as e:
        print(f'\n❌ Error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
