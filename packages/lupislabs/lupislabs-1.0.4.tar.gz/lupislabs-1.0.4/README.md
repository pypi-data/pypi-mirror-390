# LupisLabs Labs Python SDK

Spin up tracing for any Python workflow in minutes.

## Installation

```bash
pip install --upgrade lupislabs
```

Download the LupisLabs desktop app for [macOS](https://download.lupislabs.com/latest/latest-mac.dmg) or [Windows](https://download.lupislabs.com/latest/latest-win-x64.msi). No separate CLI authentication is required—once the app is running you are ready to stream traces.

## Features

- 🔍 **Automatic HTTP Tracing**: Captures requests from `requests`, `http.client`, `urllib3`, `httpx`, and `aiohttp`
- 💬 **Session Support**: Group traces by conversation/session
- ⚡ **Batching**: Automatically batches events for efficient transmission
- 🐍 **Python Support**: Full Python 3.8+ support with async/await
- 🔒 **Privacy-First**: Never collects request/response bodies, only analytics data

## Quick Start

### 1. Initialize a global LupisLabs client

Create a single `LupisLabs` instance when your app boots and reuse it everywhere:

```python
# lupis_client.py
from lupislabs import LupisLabs

lupis = LupisLabs(workspace="local-dev")
```

### 2. Enable the SDK

The SDK is **disabled by default**. You must explicitly enable it to start collecting traces:

```bash
# Enable the SDK
export LUPIS_SDK_ENABLED=true

# Or in your .env file
LUPIS_SDK_ENABLED=true
```

This opt-in approach ensures no unexpected data collection occurs. When disabled, the SDK will not instrument HTTP clients, collect traces, or send data to the collector.

### 3. Use in your code

Import that module anywhere you need to record sessions:

```python
# agent.py
from lupis_client import lupis

def summarize():
    with lupis.session("summarize") as session:
        session.log_input(prompt="Summarize the latest run logs")
        result = agent.run()
        session.log_output(result)
        return result
```

### 4. Open the desktop app and Session Monitor

Start the LupisLabs desktop app and switch to **Session Monitor**. Keep it open while you develop—every `session.log_*` call will stream into that view immediately.

### 5. Run your agent and inspect traces

Execute your script or service normally (`python app.py`, `uvicorn main:app`, notebooks, etc.). As soon as the global client records a session you will see:

- Prompts and model outputs
- Tool invocations and latency
- Custom metrics or artifacts

## Supported HTTP Clients

The SDK automatically captures outbound calls made with:

- `requests.Session`
- `http.client.HTTPConnection` / `HTTPSConnection`
- `urllib3` connection pools
- `httpx.Client` and `httpx.AsyncClient`
- `aiohttp.ClientSession`

Nested client usage (for example `requests` → `urllib3` → `http.client`) is deduplicated so only a single trace is emitted per HTTP call.

## Advanced Configuration

The SDK automatically connects to the LupisLabs desktop app at `http://127.0.0.1:9009`. For advanced use cases, you can customize the configuration:

```python
from lupislabs import LupisLabs

lupis = LupisLabs(
    workspace="local-dev",             # Required: workspace identifier
    enabled=True,                       # Optional: enable/disable tracking
    service_name="my-service",          # Optional: service name for traces
    service_version="1.0.0",            # Optional: service version
    filter_sensitive_data=True,         # Optional: enable sensitive data filtering
    sensitive_data_patterns=[...],      # Optional: custom regex patterns to filter
    redaction_mode="mask",              # Optional: 'mask', 'remove', or 'hash'
)
```

Or enable via configuration:

```python
from lupislabs import LupisLabs

lupis = LupisLabs(
    workspace="local-dev",
    enabled=True,  # SDK will start collecting data
)
```

When disabled, the SDK will not instrument HTTP clients, collect traces, or send data to the collector.

## Event Batching

Events are automatically batched and sent to the server:

- **Batch Size**: Up to 50 events per batch
- **Flush Interval**: Every 5 seconds
- **Auto-flush**: Background worker + process exit hook

## Sensitive Data Filtering

The SDK automatically filters sensitive data in production to protect API keys, tokens, and other sensitive information. This feature is **enabled by default** for security.

### Default Filtering

The SDK automatically filters these common sensitive patterns:

#### API Keys & Tokens

- `sk-[a-zA-Z0-9]{20,}` - OpenAI API keys
- `pk_[a-zA-Z0-9]{20,}` - Paddle API keys  
- `ak-[a-zA-Z0-9]{20,}` - Anthropic API keys
- `Bearer [a-zA-Z0-9._-]+` - Bearer tokens
- `x-api-key`, `authorization` - API key headers

#### Authentication

- `password`, `passwd`, `pwd` - Password fields
- `token`, `access_token`, `refresh_token`, `session_token` - Various tokens
- `secret`, `private_key`, `api_secret` - Secret fields

#### Personal Data

- `ssn`, `social_security` - Social Security Numbers
- `credit_card`, `card_number` - Credit card numbers
- `cvv`, `cvc` - Security codes

### Redaction Modes

Choose how sensitive data is replaced when initializing the SDK:

#### Mask Mode (Default)

```python
lupis = LupisLabs.init(LupisConfig(
    project_id="your-project-id",
    redaction_mode="mask",  # Default
))

# Examples:
# sk-1234567890abcdef1234567890abcdef12345678 → sk-1***5678
# Bearer sk-1234567890abcdef1234567890abcdef12345678 → Bear***5678
# password: 'secret-password' → password: '***'
```

#### Remove Mode

```python
lupis = LupisLabs.init(LupisConfig(
    project_id="your-project-id",
    redaction_mode="remove",
))

# Examples:
# sk-1234567890abcdef1234567890abcdef12345678 → [REDACTED]
# password: 'secret-password' → password: [REDACTED]
```

#### Hash Mode

```python
lupis = LupisLabs.init(LupisConfig(
    project_id="your-project-id",
    redaction_mode="hash",
))

# Examples:
# sk-1234567890abcdef1234567890abcdef12345678 → [HASH:2dd0e9d5]
# password: 'secret-password' → password: [HASHED]
```

### Custom Patterns

Add your own sensitive data patterns during initialization:

```python
lupis = LupisLabs.init(LupisConfig(
    project_id="your-project-id",
    filter_sensitive_data=True,
    sensitive_data_patterns=[
        "sk-[a-zA-Z0-9]{20,}",  # OpenAI API keys
        "Bearer [a-zA-Z0-9._-]+",  # Bearer tokens
        "custom_secret",  # Your custom field
        "my_api_key",  # Your custom field
        "email",  # Email addresses
    ],
    redaction_mode="mask",
))
```

### What Gets Filtered

The SDK filters sensitive data in:

- **Request Headers**: Authorization, API keys, tokens
- **Span Attributes**: All OpenTelemetry span attributes
- **Custom Events**: Event properties containing sensitive data

**Note**: Request and response bodies are never collected, so no filtering is needed for them.

### Disable Filtering (Development Only)

⚠️ **Warning**: Only disable filtering in development environments:

```python
lupis = LupisLabs.init(LupisConfig(
    project_id="your-project-id",
    filter_sensitive_data=False,  # ⚠️ Sensitive data will be exposed!
))
```

### Production Security

- ✅ **Enabled by default** - No configuration needed
- ✅ **Comprehensive coverage** - Common sensitive patterns included
- ✅ **Configurable** - Add custom patterns as needed
- ✅ **Performance optimized** - Minimal impact when enabled
- ✅ **Debugging friendly** - Mask mode preserves partial data for debugging

## Examples

See the `examples/` directory for more usage examples:

- `anthropic_example.py` - Anthropic API integration
- `openai_example.py` - OpenAI API integration
- `streaming_example.py` - Streaming responses
- `comprehensive_tracking.py` - Complete workflow demonstration
- `sensitive_data_example.py` - Sensitive data filtering examples

## Requirements

- Python 3.8+
- requests
- opentelemetry-api
- opentelemetry-sdk
- opentelemetry-exporter-otlp-proto-http
- opentelemetry-instrumentation-requests

## License

### Made with ❤️ by the LupisLabs team
