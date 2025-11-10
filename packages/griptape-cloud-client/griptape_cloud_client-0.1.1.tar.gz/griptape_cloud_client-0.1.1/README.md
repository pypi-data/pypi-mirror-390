# Griptape Cloud Python Client

Auto-generated Python client for the [Griptape Cloud API](https://docs.griptape.ai/stable/griptape-cloud/).

## About Griptape Cloud

Griptape Cloud is a managed platform for building and scaling AI applications, providing:

- **RAG Pipelines**: Connect data sources, manage data lakes, and build knowledge bases
- **Code Hosting**: Deploy Python code from Griptape Framework or other LLM frameworks as "Structures"
- **Agent Tools**: Extend agent capabilities with custom tools for service calls and logic
- **Configuration Management**: Control LLM behavior with Rules, Rulesets, and persistent conversation Threads
- **Full API Access**: Comprehensive REST API for all platform features

## Installation

### Using uv

Add to your `pyproject.toml`:

```toml
[tool.uv.sources]
griptape-cloud-client = { git = "https://github.com/griptape-ai/griptape-cloud-python-client", rev = "main" }
```

### Using pip

```bash
pip install git+https://github.com/griptape-ai/griptape-cloud-python-client.git@main
```

## Usage

```python
from griptape_cloud_python_client import AuthenticatedClient

client = AuthenticatedClient(base_url="https://cloud.griptape.ai/api", token="<your_api_key>")

# Use the client to interact with Griptape Cloud APIs
# See API Reference for available endpoints
```

## Documentation

- [Griptape Cloud Documentation](https://docs.griptape.ai/stable/griptape-cloud/)
- [API Reference](https://docs.griptape.ai/stable/griptape-cloud/api/api-reference/)

## Development

This client is automatically generated from the Griptape Cloud OpenAPI specification.

### Regenerating the Client

```bash
make gen/sdk
```

## License

See [LICENSE](LICENSE) file for details.
