# notionalpha-clarity

**Python SDK for NotionAlpha Clarity - AI Value Realization Platform**

## Features

- **Cost Tracking** - Track LLM costs across providers (OpenAI, Anthropic, Azure OpenAI)
- **Security Detection** - Detect threats like PII leakage and prompt injection
- **Outcome Tracking** - Link business outcomes to LLM calls
- **ROI Calculation** - Calculate return on investment for AI features
- **Forecasting** - Predict future costs and value
- **Recommendations** - Get optimization suggestions

## Installation

```bash
pip install notionalpha-clarity openai anthropic
```

## Quick Start

### 1. Get Your Configuration

1. Sign up at [notionalpha.com](https://notionalpha.com)
2. Create a provider (OpenAI, Anthropic, or Azure OpenAI)
3. Create a team for cost attribution
4. Copy your `org_id`, `team_id`, and `provider_id`

### 2. Initialize the Client

```python
from notionalpha import NotionAlphaClient
import os

clarity = NotionAlphaClient(
    org_id=os.getenv('NOTIONALPHA_ORG_ID'),
    team_id=os.getenv('NOTIONALPHA_TEAM_ID'),
    environment='production',
    provider={
        'type': 'openai',
        'provider_id': os.getenv('NOTIONALPHA_PROVIDER_ID')
    }
)
```

### 3. Make LLM Calls

```python
# OpenAI
response, transaction_id = clarity.chat.completions.create(
    model='gpt-4o-mini',
    messages=[{'role': 'user', 'content': 'Help me resolve this ticket'}]
)

print(response.choices[0].message.content)
# Cost and security are tracked automatically
```

### 4. Track Outcomes

```python
# Link business outcome to LLM call
clarity.track_outcome(
    transaction_id=transaction_id,
    type='customer_support',
    metadata={
        'ticket_id': 'TICKET-456',
        'resolution_time_seconds': 120,
        'customer_satisfaction': 5,
        'time_saved_minutes': 15
    }
)
```

### 5. View Value Realization

```python
# Get ROI summary
value = clarity.get_value_realization()

print(f"""
  Total Cost: ${value['total_cost']}
  Total Value: ${value['total_value']}
  ROI: {value['roi']}x
""")
```

## Complete Example: Customer Support Bot

```python
from notionalpha import NotionAlphaClient
import os

clarity = NotionAlphaClient(
    org_id=os.getenv('NOTIONALPHA_ORG_ID'),
    team_id=os.getenv('NOTIONALPHA_TEAM_ID'),
    environment='production',
    feature_id='customer-support-bot',
    provider={
        'type': 'openai',
        'provider_id': os.getenv('NOTIONALPHA_PROVIDER_ID')
    }
)

async def resolve_ticket(ticket_id: str, question: str):
    # Step 1: Make LLM call
    response, transaction_id = clarity.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': question}]
    )

    # Step 2: Track outcome
    clarity.track_outcome(
        transaction_id=transaction_id,
        type='customer_support',
        metadata={
            'ticket_id': ticket_id,
            'time_saved_minutes': 15,
            'customer_satisfaction': 5
        }
    )

    return response.choices[0].message.content

# Use it
await resolve_ticket('TICKET-123', 'How do I reset my password?')

# Later: View ROI
value = clarity.get_value_realization()
print(f"ROI: {value['roi']}x")  # e.g., "ROI: 25x"
```

## Supported Providers

### OpenAI

```python
clarity = NotionAlphaClient(
    org_id='org_xxx',
    team_id='team-uuid',
    provider={'type': 'openai', 'provider_id': 'provider-uuid'}
)

response, transaction_id = clarity.chat.completions.create(
    model='gpt-4o-mini',
    messages=[{'role': 'user', 'content': 'Hello!'}]
)
```

### Anthropic

```python
clarity = NotionAlphaClient(
    org_id='org_xxx',
    team_id='team-uuid',
    provider={'type': 'anthropic', 'provider_id': 'provider-uuid'}
)

response, transaction_id = clarity.messages.create(
    model='claude-3-5-sonnet-20241022',
    max_tokens=1024,
    messages=[{'role': 'user', 'content': 'Hello!'}]
)
```

### Azure OpenAI

```python
clarity = NotionAlphaClient(
    org_id='org_xxx',
    team_id='team-uuid',
    provider={
        'type': 'azure-openai',
        'provider_id': 'provider-uuid',
        'deployment_name': 'gpt-4o-mini'
    }
)

response, transaction_id = clarity.chat.completions.create(
    model='gpt-4o-mini',
    messages=[{'role': 'user', 'content': 'Hello!'}]
)
```

## API Reference

### NotionAlphaClient

Main client for interacting with NotionAlpha Clarity.

**Parameters:**
- `org_id` (str): Organization ID from NotionAlpha dashboard
- `team_id` (str): Team ID for cost attribution
- `environment` (str, optional): Environment name (default: 'production')
- `feature_id` (str, optional): Feature ID for granular tracking
- `provider` (dict): Provider configuration
- `api_base_url` (str, optional): Base URL for NotionAlpha API
- `proxy_base_url` (str, optional): Base URL for NotionAlpha proxy

### Methods

#### `chat.completions.create(**kwargs)`

Create a chat completion (OpenAI/Azure OpenAI).

**Returns:** `(response, transaction_id)`

#### `messages.create(**kwargs)`

Create a message (Anthropic).

**Returns:** `(response, transaction_id)`

#### `track_outcome(transaction_id, type, metadata, timestamp=None)`

Track a business outcome.

**Parameters:**
- `transaction_id` (str): Transaction ID from LLM response
- `type` (str): Outcome type (e.g., 'customer_support', 'code_generation')
- `metadata` (dict): Outcome-specific metadata
- `timestamp` (datetime, optional): Outcome timestamp (default: now)

#### `get_value_realization()`

Get value realization summary.

**Returns:** `dict` with `total_cost`, `total_value`, `roi`, etc.

## Development Status

🚧 **Python SDK is currently in development**

For now, you can use direct API integration. See the [API documentation](https://docs.notionalpha.com) for details.

## License

MIT

