# Brizz SDK

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Brizz observability SDK for AI applications.

## Installation

```bash
pip install brizz
# or
uv add brizz
# or
poetry add brizz
```

## Quick Start

```python
from brizz import Brizz

# Initialize
Brizz.initialize(
    api_key='your-brizzai-api-key',
    app_name='my-app',
)
```

> **Important**: Initialize Brizz before importing any libraries you want to instrument (e.g.,
> OpenAI). If using `dotenv`, use `from dotenv import load_dotenv; load_dotenv()` before importing `brizz`.

## Session Tracking

Group related operations and traces under a session context. Brizz provides two approaches:

### Context Manager Approach (Recommended)

```python
from brizz import start_session, astart_session

# Synchronous context manager
with start_session('session-123'):
    # All traces, events, and spans within this block
    # will be tagged with session.id = session-123
    response = openai.chat.completions.create(
        model='gpt-4',
        messages=[{'role': 'user', 'content': 'Hello'}]
    )
    emit_event('user.action', {'action': 'chat'})

# Async context manager
async def process_user_workflow(chat_id):
    async with astart_session(chat_id):
        response = await openai.chat.completions.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': 'Hello'}]
        )
        return response

# With additional properties
with start_session('session-456', {'user_id': 'user-789', 'region': 'us-east'}):
    # All telemetry includes session.id, user_id, and region
    emit_event('purchase', {'amount': 99.99})
```

### Function Wrapper Approach

```python
from brizz import with_session_id, awith_session_id

# Wrap synchronous functions
def sync_workflow(chat_id: str, data: dict):
    return with_session_id(chat_id, process_data, data)

# Wrap async functions
async def process_user_workflow(chat_id):
    response = await awith_session_id(
        chat_id,
        openai.chat.completions.create,
        model='gpt-4',
        messages=[{'role': 'user', 'content': 'Hello'}]
    )
    return response
```

## Custom Properties

Add custom properties to telemetry context. These properties will be attached to all traces, spans, and events within the scope:

### Context Manager Approach (Recommended)

```python
from brizz import custom_properties, acustom_properties

# Synchronous context manager
with custom_properties({'user_id': '123', 'experiment': 'variant-a'}):
    # All telemetry here includes user_id and experiment
    emit_event('api.request', {'endpoint': '/users'})
    response = call_external_api()

# Async context manager
async def process_with_context():
    async with acustom_properties({'team_id': 'abc', 'region': 'us-east'}):
        # All telemetry includes team_id and region
        result = await async_operation()
        return result

# Nested contexts (properties are merged)
with custom_properties({'tenant_id': 'tenant-1'}):
    with custom_properties({'request_id': 'req-456'}):
        # Both tenant_id and request_id are available
        emit_event('data.access')
```

### Function Wrapper Approach

```python
from brizz import with_properties, awith_properties

# Sync usage
result = with_properties(
    {'user_id': '123', 'experiment': 'variant-a'},
    my_function,
    arg1, arg2
)

# Async usage
result = await awith_properties(
    {'team_id': 'abc', 'region': 'us-east'},
    my_async_function,
    arg1, arg2
)
```

## Event Examples

```python
from brizz import emit_event

emit_event('user.signup', {'user_id': '123', 'plan': 'pro'})
emit_event('user.payment', {'amount': 99, 'currency': 'USD'})
```

## Deployment Environment

Optionally specify the deployment environment for better filtering and organization:

```python
Brizz.initialize(
    api_key='your-api-key',
    app_name='my-app',
    environment='production',  # Optional: 'dev', 'staging', 'production', etc.
)
```

## Environment Variables

```bash
BRIZZ_API_KEY=your-api-key                  # Required
BRIZZ_BASE_URL=https://telemetry.brizz.dev  # Optional
BRIZZ_APP_NAME=my-app                       # Optional
BRIZZ_ENVIRONMENT=production                # Optional: deployment environment (dev, staging, production)
```

## PII Masking

Automatically protects sensitive data in traces:

```python
# Option 1: Enable default masking (simple)
Brizz.initialize(
    api_key='your-api-key',
    masking=True,  # Enables all built-in PII patterns
)

# Option 2: Custom masking configuration
from brizz import Brizz, MaskingConfig, SpanMaskingConfig, AttributesMaskingRule

Brizz.initialize(
    api_key='your-api-key',
    masking=MaskingConfig(
        span_masking=SpanMaskingConfig(
            rules=[
                AttributesMaskingRule(
                    attribute_pattern=r'gen_ai\.(prompt|completion)',
                    mode='partial',  # 'partial' or 'full'
                    patterns=[r'sk-[a-zA-Z0-9]{32}'],  # Custom regex patterns
                ),
            ],
        ),
    ),
)
```

**Built-in patterns**: emails, phone numbers, SSNs, credit cards, API keys, crypto addresses, and
more. Use `masking=True` for defaults or `MaskingConfig` for custom rules.

## Instrumentation Control

By default, Brizz automatically instruments AI libraries and blocks HTTP clients (`urllib`, `urllib3`, `requests`, `httpx`, `aiohttp_client`) to prevent noise. You can customize which instrumentations to block:

```python
# Default: HTTP clients are blocked
Brizz.initialize(api_key="your-api-key")

# Block additional instrumentations
Brizz.initialize(
    api_key="your-api-key",
    blocked_instrumentations=["urllib", "requests", "httpx", "openai"]  # Add to defaults
)

# Enable HTTP client instrumentation
Brizz.initialize(
    api_key="your-api-key",
    blocked_instrumentations=[]  # Empty list = block nothing
)
```
