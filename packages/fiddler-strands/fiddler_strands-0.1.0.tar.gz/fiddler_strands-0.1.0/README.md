# Fiddler Strands SDK

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

OpenTelemetry instrumentation SDK for [Strands AI](https://strands.ai) agents, providing automatic observability and monitoring capabilities through Fiddler's platform.

## Features

- 🎯 **Automatic Instrumentation**: Zero-code instrumentation of Strands agents using OpenTelemetry
- 🔍 **Built-in Observability**: Automatic logging hooks for agent interactions
- 📊 **Fiddler Integration**: Custom span processors for enhanced trace analysis
- 🛠️ **Extensible**: Easy to add custom hooks and processors
- 🚀 **Production Ready**: Built on OpenTelemetry standards

## Installation

### Using uv (Recommended)

```bash
# Install the SDK
uv add fiddler-strands

# For development
uv add fiddler-strands[dev]

# For running examples
uv add fiddler-strands[examples]
```

### Using pip

```bash
pip install fiddler-strands
```

## Quick Start

### Basic Usage

```python
import os
from strands import Agent
from strands.models.openai import OpenAIModel
from strands.telemetry import StrandsTelemetry
from fiddler_strandsagents import StrandsAgentInstrumentor

strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_otlp_exporter()
strands_telemetry.setup_console_exporter()
# Enable automatic instrumentation
StrandsAgentInstrumentor(strands_telemetry).instrument()

# Create your agent as usual - LoggingHook will be automatically injected
model = OpenAIModel(api_key=os.getenv("OPENAI_API_KEY"))
agent = Agent(model=model, system_prompt="You are a helpful assistant")

# Use your agent - all interactions will be automatically instrumented
response = agent("Hello, how are you?")
```

## Examples

The `examples/` directory contains complete working examples:

- **`travel_agent.py`**: Complete travel booking agent with tools
- **`async_travel_agent.py`**: Async version of the travel booking agent

### Running Examples

```bash
# Clone the repository
git clone https://github.com/fiddler-labs/fiddler-strands-sdk
cd fiddler-strands-sdk

# Set up environment
export OPENAI_API_KEY="your-api-key-here"

# Install dependencies
uv sync --extra examples

# Run an example
uv run python examples/travel_agent.py
```

## API Reference

### StrandsAgentInstrumentor

The main instrumentor class for automatic agent instrumentation.

```python
from fiddler_strandsagents import StrandsAgentInstrumentor

instrumentor = StrandsAgentInstrumentor()

# Enable instrumentation
instrumentor.instrument()

# Check if instrumentation is active
is_active = instrumentor.is_instrumented_by_opentelemetry

# Disable instrumentation
instrumentor.uninstrument()
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/fiddler-labs/fiddler-strands-sdk
cd fiddler-strands-sdk

# Install with development dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run linting
uv run black fiddler_strandsagents/ examples/
uv run isort fiddler_strandsagents/ examples/
uv run flake8 fiddler_strandsagents/ examples/
```

### Project Structure

```
fiddler-strands-sdk/
├── fiddler_strandsagents/    # Main SDK package
│   ├── __init__.py             # Public API exports
│   ├── instrumentation.py      # OpenTelemetry instrumentor
│   ├── hooks.py                # Hook providers
│   └── span_processor.py       # Custom span processors
├── examples/                   # Usage examples
├── tests/                      # Test suite
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`uv run pytest && uv run black fiddler_strandsagents/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@fiddler.ai
- 📖 Documentation: https://docs.fiddler.ai/strands-sdk
- 🐛 Issues: https://github.com/fiddler-labs/fiddler-strands-sdk/issues
