# Bigconsole Sdk-python

A Python SDK bigconsole for building GraphQL-based API clients quickly. This SDK provides a structured foundation for creating Python SDKs that interact with GraphQL APIs, similar to the Node.js workspace SDK but adapted for Python.

## Features

- 🚀 **Async/await support** - Built with modern Python async patterns
- 🔐 **Authentication handling** - Token management and refresh logic
- 📦 **Modular architecture** - Organized by feature modules
- 🔧 **Type hints** - Full typing support with mypy
- 🧪 **Testing ready** - Pytest configuration included
- 📚 **Documentation** - Sphinx-ready documentation setup
- 🛠️ **Development tools** - Code formatting, linting, and pre-commit hooks

## Installation

```bash
# Install from PyPI (when published)
pip install bigconsole-sdk

# Or install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

```python
import asyncio
from bigconsole_sdk import BigconsoleSDK, BigconsoleSDKConfig
from bigconsole_sdk.types.common import UserRegisterInput

async def main():
    # Initialize the SDK
    config = BigconsoleSDKConfig(
        endpoint="https://api.example.com/graphql",
        api_key="your-api-key"  # Optional
    )

    sdk = BigconsoleSDK(config)
    
    try:
        # Register a new user
        user_input = UserRegisterInput(
            email="user@example.com",
            name="John Doe",
            password="secure_password"
        )
        
        user = await sdk.auth.register(user_input)
        print(f"User registered: {user.name}")
        
        # Set authentication tokens
        sdk.set_tokens(
            access_token="your-access-token",
            refresh_token="your-refresh-token"
        )
        
        # Get current user
        current_user = await sdk.users.get_current_user()
        print(f"Current user: {current_user.name}")
        
    finally:
        await sdk.client.close()

# Run the example
asyncio.run(main())
```

## Configuration

The SDK is configured using the `BigconsoleSDKConfig` class:

```python
from bigconsole_sdk import BigconsoleSDKConfig

config = BigconsoleSDKConfig(
    endpoint="https://api.example.com/graphql",  # Required
    api_key="your-api-key",                      # Optional
    access_token="your-access-token",            # Optional
    refresh_token="your-refresh-token",          # Optional
    timeout=30.0                                 # Optional, default: 30.0
)
```

## Available Modules

The SDK is organized into the following modules:

- **auth** - Authentication operations (register, login, logout, etc.)
- **user** - User management operations
- **workspace** - Workspace operations (TODO)
- **rbac** - Role-based access control (TODO)
- **team** - Team management (TODO)
- **project** - Project operations (TODO)
- **resources** - Resource management (TODO)
- **billing** - Billing operations (TODO)
- **organization** - Organization management (TODO)
- **payment** - Payment processing (TODO)
- **quota** - Quota management (TODO)
- **store** - Store operations (TODO)
- **support** - Support ticket management (TODO)
- **usage** - Usage analytics (TODO)
- **utils** - Utility functions (TODO)
- **addon** - Add-on management (TODO)
- **plan** - Plan management (TODO)
- **product** - Product management (TODO)
- **config** - Configuration management (TODO)

## Examples

See the `examples/` directory for more detailed usage examples:

- `basic_usage.py` - Basic SDK operations
- `advanced_usage.py` - Advanced features and error handling

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd bigconsole-sdk-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
black src/ tests/ examples/
isort src/ tests/ examples/

# Lint code
flake8 src/ tests/ examples/
mypy src/

# Run tests
pytest

# Run tests with coverage
pytest --cov=bigconsole_sdk --cov-report=html
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=bigconsole_sdk

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

## Project Structure

```
bigconsole-sdk-python/
├── src/
│   └── bigconsole_sdk/
│       ├── __init__.py           # Main SDK class
│       ├── client/               # HTTP/GraphQL client
│       ├── auth/                 # Authentication module
│       ├── user/                 # User management
│       ├── workspace/            # Workspace operations
│       ├── types/                # Type definitions
│       └── ...                   # Other modules
├── tests/                        # Test files
├── examples/                     # Usage examples
├── docs/                         # Documentation
├── pyproject.toml               # Package configuration
├── requirements.txt             # Production dependencies
└── requirements-dev.txt         # Development dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Create a Pull Request

## Type Hints

This SDK is fully typed and supports mypy type checking:

```bash
mypy src/bigconsole_sdk
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## Support

- 📖 **Documentation**: [docs.algoshred.com/sdk/python](https://docs.algoshred.com/sdk/python)
- 🐛 **Issues**: [GitHub Issues](https://github.com/algoshred/bigconsole-sdk-python/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/algoshred/bigconsole-sdk-python/discussions)

## Related Projects

- [Workspaces SDK Node.js](../workspaces-sdk-node) - The Node.js version this SDK is based on
- [Bigconsole Frontend](../bigconsole-frontend) - Frontend bigconsole
- [Bigconsole Backend](../bigconsole-python-be-graphql) - Python GraphQL backend bigconsole
- test