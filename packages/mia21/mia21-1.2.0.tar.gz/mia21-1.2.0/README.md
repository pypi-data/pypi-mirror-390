# 🐍 Mia21 Python SDK

Official Python client library for the Mia21 Chat API.

[![PyPI version](https://badge.fury.io/py/mia21.svg)](https://badge.fury.io/py/mia21)
[![Python](https://img.shields.io/pypi/pyversions/mia21.svg)](https://pypi.org/project/mia21/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🚀 Quick Start

### Installation

```bash
pip install mia21
```

### Basic Usage

```python
from mia21 import Mia21Client

# Initialize client
client = Mia21Client(api_key="your-api-key-here")

# Start chat session
client.initialize(space_id="customer_support")

# Send a message
response = client.chat("How do I reset my password?")
print(response.message)

# Close session
client.close()
```

### Streaming Chat

```python
from mia21 import Mia21Client

client = Mia21Client(api_key="your-api-key-here")
client.initialize()

# Stream response in real-time
print("AI: ", end='', flush=True)
for chunk in client.stream_chat("Tell me a story"):
    print(chunk, end='', flush=True)
print()  # New line

client.close()
```

### Context Manager (Auto-Close)

```python
from mia21 import Mia21Client

with Mia21Client(api_key="your-api-key") as client:
    client.initialize(space_id="sales_assistant")
    response = client.chat("What are your pricing plans?")
    print(response.message)
# Chat automatically closed
```

---

## 📚 API Reference

### `Mia21Client`

#### Constructor

```python
client = Mia21Client(
    api_key: str,              # Required: Your Mia21 API key
    base_url: str = "...",     # Optional: API base URL
    user_id: str = None,       # Optional: User ID (auto-generated if not provided)
    timeout: int = 90          # Optional: Request timeout in seconds
)
```

#### Methods

**`list_spaces()`**
```python
spaces = client.list_spaces()
# Returns: List[Space]

for space in spaces:
    print(f"{space.id}: {space.name} - {space.description}")
```

**`initialize()`**
```python
response = client.initialize(
    space_id="customer_support",    # Optional: Space to use
    llm_type="openai",              # Optional: "openai" or "gemini"
    user_name="John",               # Optional: User's name
    language="en",                  # Optional: Force language
    generate_first_message=True,    # Optional: Generate greeting
    incognito_mode=False            # Optional: Privacy mode
)
# Returns: InitializeResponse

print(response.message)  # AI's first message
```

**`chat()`**
```python
response = client.chat(
    message="Hello!",               # Required: User message
    space_id="customer_support",    # Optional: Which space
    temperature=0.7,                # Optional: 0.0-2.0
    max_tokens=1024                 # Optional: Max response length
)
# Returns: ChatResponse

print(response.message)  # AI's response
print(response.tool_calls)  # Tools executed (if any)
```

**`stream_chat()`**
```python
for chunk in client.stream_chat(
    message="Tell me a story",
    space_id="storyteller",
    temperature=0.9
):
    print(chunk, end='', flush=True)
# Yields: str (text chunks)
```

**`close()`**
```python
client.close(
    space_id="customer_support"     # Optional: Which space to close
)
# Saves conversation to database
```

---

## 🎯 Advanced Examples

### Multi-Space Conversation

```python
from mia21 import Mia21Client

client = Mia21Client(api_key="your-api-key")

# Initialize multiple spaces
client.initialize(space_id="support")
client.initialize(space_id="sales")
client.initialize(space_id="technical")

# Chat with different spaces independently
support_response = client.chat("I have a bug", space_id="support")
sales_response = client.chat("Pricing info?", space_id="sales")
tech_response = client.chat("API docs?", space_id="technical")

# Each space maintains separate conversation history
```

### Error Handling

```python
from mia21 import Mia21Client, ChatNotInitializedError, APIError

client = Mia21Client(api_key="your-api-key")

try:
    # This will raise ChatNotInitializedError
    client.chat("Hello")  # Forgot to initialize!
except ChatNotInitializedError as e:
    print(f"Error: {e}")
    client.initialize()  # Fix it
    client.chat("Hello")  # Now works

try:
    response = client.chat("What's the weather?")
except APIError as e:
    print(f"API Error: {e}")
```

### Async Integration (with asyncio)

```python
import asyncio
from mia21 import Mia21Client

async def chat_async():
    client = Mia21Client(api_key="your-api-key")
    client.initialize()
    
    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None, 
        client.chat, 
        "Hello from async!"
    )
    
    print(response.message)
    client.close()

asyncio.run(chat_async())
```

---

## 🛠️ Configuration

### Environment Variables

```bash
# Set API key via environment
export MIA21_API_KEY="your-api-key-here"
export MIA21_BASE_URL="https://mia-api-staging-795279012747.us-central1.run.app"
```

```python
import os
from mia21 import Mia21Client

# Reads from environment variables
client = Mia21Client(
    api_key=os.getenv("MIA21_API_KEY"),
    base_url=os.getenv("MIA21_BASE_URL")
)
```

---

## 🧪 Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=mia21 tests/
```

---

## 📄 License

MIT License - see LICENSE file for details.

---

## 🆘 Support

- **Documentation**: https://docs.mia21.com
- **API Reference**: https://docs.mia21.com/api
- **GitHub Issues**: https://github.com/mia21/python-sdk/issues
- **Email**: hello@mia21.com

---

## 🎉 Examples

See the `examples/` directory for complete working examples:
- `basic_chat.py` - Simple chat example
- `streaming_chat.py` - Streaming response example
- `multi_space.py` - Multiple spaces conversation
- `async_chat.py` - Asyncio integration

---

**Made with ❤️ by Mia21**



