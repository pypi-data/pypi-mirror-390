# Halfred Python SDK

A Python SDK for consuming the Halfred service API. The API is fully compatible with the OpenAI API standard.

## Installation

```bash
pip install halfred
```

Or install from source:

```bash
pip install -e .
```

## Quick Start

```python
from halfred import HalfredClient

# Initialize the client with your API key
client = HalfredClient(api_key="halfred_xxxxxxxxxxxxxxxx")

# List available models
models = client.models.list()
print(models)

# Create a chat completion
completion = client.chat.completions.create(
    model="lite",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)
print(completion["choices"][0]["message"]["content"])
```

## Usage

### List Models

Get a list of available models:

```python
from halfred import HalfredClient

client = HalfredClient(api_key="halfred_xxxxxxxxxxxxxxxxx")
models = client.models.list()

# Access the list of models
for model in models["data"]:
    print(f"Model ID: {model['id']}")
```

### Create Chat Completions

Create a chat completion:

```python
from halfred import HalfredClient

client = HalfredClient(api_key="halfred_xxxxxxxxxxxxxxxxx")

completion = client.chat.completions.create(
    model="lite",
    messages=[
        {"role": "user", "content": "What is Python?"}
    ]
)

print(completion["choices"][0]["message"]["content"])
```

#### Chat Completion Parameters

```python
completion = client.chat.completions.create(
    model="lite",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7,              # Sampling temperature (0-2)
    max_tokens=100,              # Maximum tokens to generate
    max_completion_tokens=50,     # Maximum completion tokens
    response_format={"type": "json_object"},  # Response format (optional)
    stream=False                 # Whether to stream the response
)
```

### Error Handling

```python
from halfred import HalfredClient, HalfredAPIError, HalfredAuthenticationError

client = HalfredClient(api_key="halfred_xxxxxxxxxxxxxxxxx")

try:
    completion = client.chat.completions.create(
        model="dev",
        messages=[{"role": "user", "content": "Hello"}]
    )
except HalfredAuthenticationError:
    print("Authentication failed. Check your API key.")
except HalfredAPIError as e:
    print(f"API error: {e}")
    print(f"Status code: {e.status_code}")
```

### Custom Configuration

```python
from halfred import HalfredClient

# Custom base URL and timeout
client = HalfredClient(
    api_key="halfred_xxxxxxxxxxxxxxxxx",
    base_url="https://api.halfred.com",  # Optional, defaults to production
    timeout=30  # Optional, defaults to 30 seconds
)
```

## Development

### Setup

```bash
# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black halfred/
```

## API Compatibility

This SDK is designed to be compatible with the OpenAI API standard. The API endpoints and request/response formats follow the same structure as OpenAI's API, making it easy to switch between providers.

## License

MIT
