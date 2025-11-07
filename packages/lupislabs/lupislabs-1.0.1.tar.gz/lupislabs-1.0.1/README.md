# Lupis Labs Python SDK

Python SDK for LupisLabs with OpenTelemetry tracing and custom event tracking.

## Installation

```bash
pip install lupislabs
```

For async support (recommended):

```bash
pip install lupislabs[async]
```

## Features

- 🔍 **Automatic HTTP Tracing**: Captures requests from `requests`, `http.client`, `urllib3`, `httpx`, and `aiohttp`
- 📊 **Custom Event Tracking**: Track custom events with properties and metadata
- 💬 **Chat ID Support**: Group traces by conversation/chat ID
- ⚡ **Batching**: Automatically batches events for efficient transmission
- 🐍 **Python Support**: Full Python 3.8+ support with async/await
- 🔒 **Privacy-First**: Never collects request/response bodies, only analytics data

## Quick Start

```python
from lupislabs import LupisSDK, LupisConfig

lupis = LupisSDK.init(LupisConfig(
    project_id="your-project-id",
))

# Supported HTTP clients are instrumented automatically.
# Make your AI/HTTP calls here and traces will appear in the Lupis desktop app.
```

## Supported HTTP Clients

The SDK automatically captures outbound calls made with:

- `requests.Session`
- `http.client.HTTPConnection` / `HTTPSConnection`
- `urllib3` connection pools
- `httpx.Client` and `httpx.AsyncClient`
- `aiohttp.ClientSession`

Nested client usage (for example `requests` → `urllib3` → `http.client`) is deduplicated so only a single trace is emitted per HTTP call.

Once configured, the SDK stores the instance globally. Calling `LupisSDK.init(...)` again returns the existing instance, and you can retrieve it from anywhere with `LupisSDK.get_instance()`.

```python
# In another module
from lupislabs import LupisSDK

lupis = LupisSDK.get_instance()
if lupis and lupis.is_enabled():
    lupis.track_event("button_click", {"button_name": "submit"})
```

## Configuration

```python
from lupislabs import LupisConfig

config = LupisConfig(
    project_id="your-project-id",  # Required
    ue,                   # Optional, default: True
    service_name="lupis-sdk",       # Optional, default: "lupis-sdk"
    service_version="1.0.0",        # Optional, default: "1.0.0"
    filter_sensitive_data=True,     # Optional, default: True
    sensitive_data_patterns=[       # Optional, default: common patterns
        "sk-[a-zA-Z0-9]{20,}",
        "Bearer [a-zA-Z0-9._-]+",
    ],
    redaction_mode="mask",          # Optional: "mask", "remove", "hash"
)
```

> ℹ️ The traces endpoint defaults to the desktop collector at `http://127.0.0.1:9009/api/traces`. Override it by setting `otlp_endpoint` if you need to forward telemetry elsewhere.

## Event Tracking

### Basic Event Tracking

```python
lupis.track_event("button_click", {
    "button_name": "submit",
    "page": "/dashboard",
})
```

### Event with User Context

```python
from lupislabs import LupisMetadata

lupis.track_event("feature_used", {
    "feature": "export_data",
    "format": "csv",
}, metadata=LupisMetadata(
    user_id="user_123",
    session_id="browser_session_456",
    organization_id="org_789",
))
```

## Conversation Grouping

Group traces by conversation/thread using `chat_id`:

```python
# Set global chat ID for all subsequent traces
lupis.set_chat_id("conversation_123")

# Or set per-operation chat ID
await lupis.run(async def my_ai_function():
    # Your AI conversation code here
    pass
, options=LupisBlockOptions(chat_id="conversation_123"))

lupis.clear_chat_id()
```

## Metadata Types

### sessionId vs chatId

- **`session_id`**: Browser/app session identifier that persists across conversations
  - Used for analytics and user journey tracking
  - Example: `"browser_session_abc123"`
  
- **`chat_id`**: Individual conversation/thread identifier
  - Used for grouping related traces within a conversation
  - Changes for each new conversation
  - Example: `"chat_thread_xyz789"`

### Example Usage

```python
from lupislabs import LupisMetadata, LupisBlockOptions

# Set user context (persists across conversations)
lupis.set_metadata(LupisMetadata(
    user_id="user_123",
    organization_id="org_456",
    session_id="browser_session_abc123",  # Same across conversations
))

# Start a new conversation
lupis.set_chat_id("conversation_1")

await lupis.run(async def ai_conversation_1():
    # AI conversation code
    pass
, options=LupisBlockOptions(chat_id="conversation_1"))

# Start another conversation (same session, different chat)
lupis.set_chat_id("conversation_2")

await lupis.run(async def ai_conversation_2():
    # Another AI conversation code
    pass
, options=LupisBlockOptions(chat_id="conversation_2"))
```

## Event Batching

Events are automatically batched and sent to the server:

- **Batch Size**: Up to 50 events per batch
- **Flush Interval**: Every 5 seconds
- **Auto-flush**: Background worker + process exit hook

## OpenTelemetry Integration

The SDK automatically instruments HTTP requests and creates traces. Access the tracer:

```python
tracer = lupis.get_tracer()

with lupis.create_span("custom-operation", {
    "custom.attribute": "value",
}) as span:
    # Your code here
    pass
```

## Data Collection

The SDK collects only analytics-focused data while protecting sensitive information:

### ✅ **Collected Data**

- **HTTP Metadata**: URL, method, status code, duration, headers (filtered)
- **Token Usage**: Input/output/cache tokens from AI providers
- **Cost Analytics**: Calculated costs based on token usage and provider pricing
- **Model Information**: AI model used for requests
- **User Context**: User ID, organization ID, session ID, chat ID
- **Custom Events**: Manually tracked events with properties
- **Performance Metrics**: Response times, error rates, success/failure status

### ❌ **Never Collected**

- **Request Bodies**: Full request payloads are never captured
- **Response Bodies**: Full response content is never captured
- **Sensitive Data**: API keys, tokens, passwords (filtered by default)
- **Personal Information**: PII is not collected by default

### 🔒 **Privacy Protection**

- Sensitive data filtering enabled by default
- Request/response bodies skipped to reduce span size
- Focus on analytics and cost tracking only
- User-controlled data collection

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
lupis = LupisSDK.init(LupisConfig(
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
lupis = LupisSDK.init(LupisConfig(
    project_id="your-project-id",
    redaction_mode="remove",
))

# Examples:
# sk-1234567890abcdef1234567890abcdef12345678 → [REDACTED]
# password: 'secret-password' → password: [REDACTED]
```

#### Hash Mode

```python
lupis = LupisSDK.init(LupisConfig(
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
lupis = LupisSDK.init(LupisConfig(
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
lupis = LupisSDK.init(LupisConfig(
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

## Shutdown (optional)

The SDK flushes pending work on a timer and registers an `atexit` hook so traces are sent during normal process shutdown—no manual shutdown call is required for typical apps. Call `await lupis.shutdown()` only when you need to force an immediate flush (for example, in short-lived scripts or tests).

## Examples

See the `examples/` directory for more usage examples:

- `event_tracking_example.py` - Custom event tracking
- `anthropic_example.py` - Anthropic API integration
- `openai_example.py` - OpenAI API integration
- `langchain_example.py` - LangChain integration
- `streaming_example.py` - Streaming responses

## Requirements

- Python 3.8+
- requests
- opentelemetry-api
- opentelemetry-sdk
- opentelemetry-exporter-otlp-proto-http
- opentelemetry-instrumentation-requests

## License

### Made with ❤️ by the Lupis team
