# ask-pydantic

A CLI tool to ask questions about Pydantic AI and Logfire documentation using AI-powered search.

```bash
# run with uvx
uvx ask-pydantic
uvx ask-pydantic "How do I create an agent?"

# or use in your code
uv add ask-pydantic
```

```python
from ask_pydantic import agent

result = agent.run_sync("How do I create an agent?")
print(result.output)
```

https://github.com/user-attachments/assets/f2ab1dfc-f90c-4311-a04c-c41b82eb3052


## Installation

```bash
# install globally
uv tool install ask-pydantic
```

## Requirements

You need an API key from at least one supported LLM provider:

- **Anthropic (Claude)** - Recommended
  ```bash
  export ANTHROPIC_API_KEY="your-key-here"
  ```

- **OpenAI (GPT)**
  ```bash
  export OPENAI_API_KEY="your-key-here"
  ```

- **Google (Gemini)**
  ```bash
  export GOOGLE_API_KEY="your-key-here"
  ```

- **Mistral**
  ```bash
  export MISTRAL_API_KEY="your-key-here"
  ```

- **Groq**
  ```bash
  export GROQ_API_KEY="your-key-here"
  ```

**Tip:** Add your API key to a `.env` file and source it:

```bash
echo 'export ANTHROPIC_API_KEY="your-key-here"' > .env
source .env && ask-pydantic "your question"
```

## Usage

### CLI Usage

Ask questions directly from the command line:

```bash
ask-pydantic "How do I create a Pydantic AI agent? Format your response nicely for a CLI."
ask-pydantic "What is Logfire?"
ask-pydantic "How do I use tools with agents?"
```

On first run, the tool will ask permission to download documentation (~20MB) from the Pydantic AI and Logfire repositories.

### Programmatic Usage

Use the agent in your Python code:

```python
from ask_pydantic import agent

result = agent.run_sync("How do I create an agent?")
print(result.output)
```

Or run inline with `uv`:

```bash
uv run --with ask-pydantic python - <<'EOF'
from ask_pydantic import agent

result = agent.run_sync("How do I use tools with Pydantic AI?")
print(result.output)
EOF
```

## How It Works

1. **Documentation Download:** On first run, the tool downloads documentation from the Pydantic AI and Logfire repositories to `~/.ask-pydantic/docs/`
2. **Vector Database:** Creates a searchable vector database using LanceDB and sentence transformers
3. **Hybrid Search:** Uses both semantic and keyword search to find relevant documentation
4. **AI-Powered Answers:** Uses your preferred LLM to generate comprehensive answers with links to source documentation

## Examples

```bash
# Get started with Pydantic AI
ask-pydantic "How do I get started with Pydantic AI?"

# Learn about tools
ask-pydantic "What are tools and how do I use them?"

# Logfire queries
ask-pydantic "How do I set up Logfire for my application?"

# Specific features
ask-pydantic "How do I stream responses from an agent?"
```

## Configuration

- Documentation: `~/.ask-pydantic/docs/`
- Vector Database: `/tmp/lancedb-pydantic-ai-chat`

## Development

You may use this as a tempalte for distributing your own Pydantic AI agents as packages so your users can import them in their code. Just expose your own agent object and adjust the [ask-pydantic/cli.py](./ask_pydantic/cli.py) to your needs.

```bash
# Clone the repository
git clone https://github.com/dsfaccini/ask-pydantic.git
cd ask-pydantic

# Install dependencies
uv sync

# Run locally
uv run ask-pydantic "your question"
```

## Links

- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [Logfire Documentation](https://logfire.pydantic.dev/)
- [Pydantic](https://docs.pydantic.dev/)

## License

MIT
