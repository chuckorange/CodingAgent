# DevAgent

Local AI coding agent for understanding codebases and making code changes.

## Features

- **Conversational Interface**: Chat with your codebase naturally
- **Code Understanding**: Analyze project structure and explain code
- **Feature Development**: Add new features with tests
- **Bug Fixing**: Debug issues and fix failing tests  
- **GitHub Integration**: Create PRs with explanations
- **Sandbox Execution**: Safe testing in Docker containers

## Installation

```bash
# Clone the repository
git clone https://github.com/chuckorange/CodingAgent.git
cd CodingAgent

# Install dependencies
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Usage

Start the conversational interface:

```bash
devagent
```

Then chat naturally:
- "What does this project do?"
- "Explain src/auth.py" 
- "Add a GET /users/:id endpoint"
- "Fix the failing tests"
- "Create a PR for these changes"

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black src tests
ruff check src tests
```

## Architecture

DevAgent uses a multi-agent architecture with LangGraph:

- **Dispatcher**: Classifies intent and creates execution plans
- **Retriever**: Searches codebase and gathers context
- **Editor**: Generates code changes and diffs  
- **Executor**: Runs tests in Docker sandbox
- **Verifier**: Analyzes results and handles retries
- **PR Bot**: Creates GitHub PRs with explanations

See [SPEC.md](SPEC.md) for detailed technical specification.

## Status

🚧 **Under Development** - MVP implementation in progress

## License

MIT License - see [LICENSE](LICENSE) for details.