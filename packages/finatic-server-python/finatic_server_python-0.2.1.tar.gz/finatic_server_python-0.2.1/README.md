# Finatic Server Python SDK

A comprehensive Python SDK for integrating with Finatic's server-side trading and portfolio management APIs.

## Installation

```bash
pip install finatic-server-python
```

## Quick Start

```python
import asyncio
from finatic_server import FinaticServerClient

async def main():
    # Initialize with API key
    client = FinaticServerClient("your-api-key")

    # Start session
    await client.start_session()

    # Get portal URL for user authentication
    portal_url = await client.get_portal_url()
    print(f"User should visit: {portal_url}")

    # After user completes authentication in portal
    # User is now authenticated
    print(f"Authenticated user: {client.get_user_id()}")

    # Get portfolio data
    brokers = await client.get_broker_list()
    print(f"Available brokers: {len(brokers)}")

    # Get all orders across all pages
    all_orders = await client.get_all_orders()
    print(f"Total orders: {len(all_orders)}")

# Run the example
asyncio.run(main())
```

## Authentication Flow

The SDK supports two authentication methods:

### 1. Portal Authentication (User completes auth in browser)

```python
client = FinaticServerClient("your-api-key")

# Start session
await client.start_session()

# Get portal URL for user authentication
portal_url = await client.get_portal_url()
print(f"User should visit: {portal_url}")

# After user completes authentication in portal
# User is now authenticated
print(f"User ID: {client.get_user_id()}")

# Now you can make authenticated requests
brokers = await client.get_broker_list()
```

### Server: Get one-time token for Client SDK (additive helper)

```python
async with FinaticServerClient("your-api-key") as client:
    # Fetch a fresh one-time token without modifying the current server session
    one_time_token = await client.get_token()

    # Pass this token to the Client SDK on the frontend to start its session
    # e.g., FinaticClient.init({ "token": one_time_token })
```

Notes:

- Requires the client to be initialized (use the async context manager or call **aenter**()).
- Does not call `/session/start` and does not change `session_id`/`company_id` state.
- Safe to call multiple times; each call returns a new short-lived token.

### 2. Direct Authentication (Server-side with known user ID)

```python
client = FinaticServerClient("your-api-key")

# Start session with user ID (automatically authenticates)
await client.start_session(user_id="user123")

# Now you can make authenticated requests immediately
brokers = await client.get_broker_list()
```

## Core Features

- **API Key Authentication**: Secure server-side authentication
- **Portal Integration**: Get portal URLs for user authentication with optional theming
- **Automatic Token Management**: Handles access/refresh tokens automatically
- **Pagination Support**: Built-in pagination for large datasets
- **Type-safe API**: Full Pydantic model support
- **Async/await Support**: Non-blocking operations
- **Comprehensive Error Handling**: Detailed error types
- **Convenience Methods**: Helper methods for common data filtering
- **Asset-Specific Orders**: Simplified order placement for different asset types

## API Reference

### Initialization

```python
client = FinaticServerClient(
    api_key="your-api-key",
    base_url="https://api.finatic.dev",  # Optional
    device_info={                        # Optional
        "ip_address": "192.168.1.100",
        "user_agent": "MyApp/1.0.0",
    },
    timeout=30                          # Optional
)
```

### Authentication

```python
# Start session
await client.start_session()

# Start session with user ID (direct auth)
await client.start_session(user_id="user123")

# Check authentication status
is_authenticated = client.is_authenticated()

# Get user information
user_id = client.get_user_id()
session_id = client.get_session_id()
company_id = client.get_company_id()
```

### Portal Management

```python
# Get basic portal URL
portal_url = await client.get_portal_url()

# Get portal URL with theming
portal_url = await client.get_portal_url(
    theme={"primary_color": "#007bff", "logo_url": "https://example.com/logo.png"},
    brokers=["robinhood", "tasty_trade"],
    email="user@example.com"
)
```

### Broker Data Access

```python
# Get broker information
brokers = await client.get_broker_list()
connections = await client.get_broker_connections()

# Get accounts with pagination
accounts = await client.get_accounts(page=1, per_page=100)
all_accounts = await client.get_all_accounts()

# Get orders with pagination
orders = await client.get_orders(page=1, per_page=100)
all_orders = await client.get_all_orders()

# Get positions with pagination
positions = await client.get_positions(page=1, per_page=100)
all_positions = await client.get_all_positions()

# Get balances with pagination
balances = await client.get_balances(page=1, per_page=100)
all_balances = await client.get_all_balances()
```

### Convenience Filter Methods

```python
# Get filtered data
open_positions = await client.get_open_positions()
filled_orders = await client.get_filled_orders()
pending_orders = await client.get_pending_orders()
active_accounts = await client.get_active_accounts()

# Get data by symbol
aapl_orders = await client.get_orders_by_symbol("AAPL")
aapl_positions = await client.get_positions_by_symbol("AAPL")

# Get data by broker
robinhood_orders = await client.get_orders_by_broker("robinhood")
robinhood_positions = await client.get_positions_by_broker("robinhood")
```

### Trading Operations

#### General Order Placement

```python
from finatic_server.types.orders import BrokerOrderParams

# Place a market order
order_params = BrokerOrderParams(
    broker="robinhood",
    order_type="Market",
    asset_type="equity",
    action="Buy",
    time_in_force="day",
    account_number="123456789",
    symbol="AAPL",
    order_qty=10
)

response = await client.place_order(order_params)
```

#### Asset-Specific Order Methods

##### Stock Orders

```python
# Stock market order
response = await client.place_stock_market_order(
    symbol="AAPL",
    quantity=10,
    side="buy",
    broker="robinhood",
    account_number="123456789"
)

# Stock limit order
response = await client.place_stock_limit_order(
    symbol="AAPL",
    quantity=10,
    side="buy",
    price=150.00,
    time_in_force="gtc",
    broker="robinhood",
    account_number="123456789"
)

# Stock stop order
response = await client.place_stock_stop_order(
    symbol="AAPL",
    quantity=10,
    side="sell",
    stop_price=140.00,
    time_in_force="gtc",
    broker="robinhood",
    account_number="123456789"
)
```

##### Crypto Orders

```python
# Crypto market order
response = await client.place_crypto_market_order(
    symbol="BTC-USD",
    quantity=0.1,
    side="buy",
    broker="coinbase",
    account_number="123456789"
)

# Crypto limit order
response = await client.place_crypto_limit_order(
    symbol="BTC-USD",
    quantity=0.1,
    side="buy",
    price=50000.00,
    time_in_force="gtc",
    broker="coinbase",
    account_number="123456789"
)
```

##### Options Orders

```python
# Options market order
response = await client.place_options_market_order(
    symbol="AAPL240315C00150000",
    quantity=1,
    side="buy",
    broker="tasty_trade",
    account_number="123456789"
)

# Options limit order
response = await client.place_options_limit_order(
    symbol="AAPL240315C00150000",
    quantity=1,
    side="buy",
    price=5.00,
    time_in_force="gtc",
    broker="tasty_trade",
    account_number="123456789"
)
```

##### Futures Orders

```python
# Futures market order
response = await client.place_futures_market_order(
    symbol="ES",
    quantity=1,
    side="buy",
    broker="ninja_trader",
    account_number="123456789"
)

# Futures limit order
response = await client.place_futures_limit_order(
    symbol="ES",
    quantity=1,
    side="buy",
    price=4500.00,
    time_in_force="gtc",
    broker="ninja_trader",
    account_number="123456789"
)
```

#### Order Management

```python
# Cancel an order
response = await client.cancel_order(
    order_id="order-123",
    broker="robinhood",
    connection_id="connection-456"
)

# Modify an order
response = await client.modify_order(
    order_id="order-123",
    modifications={"price": 155.00, "quantity": 5},
    broker="robinhood",
    connection_id="connection-456"
)
```

### Broker Management

```python
# Disconnect a company from broker
response = await client.disconnect_company("connection-123")
```

### Error Handling

```python
from finatic_server.utils.errors import AuthenticationError, ApiError, ValidationError

try:
    orders = await client.get_orders()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ValidationError as e:
    print(f"Invalid request: {e}")
except ApiError as e:
    print(f"API error: {e}")
```

### Context Manager Usage

```python
async with FinaticServerClient("your-api-key") as client:
    await client.start_session()
    brokers = await client.get_broker_list()
    # Client automatically closes when exiting context
```

### Cleanup

```python
# Close the client and cleanup resources
await client.close()
```

## Advanced Usage

### Custom Filters

```python
from finatic_server.types import BrokerDataOptions, OrdersFilter

# Get orders with custom filters
orders = await client.get_orders(
    page=1,
    per_page=50,
    options=BrokerDataOptions(
        broker_name="robinhood",
        account_id="123456789"
    ),
    filters=OrdersFilter(
        status="filled",
        symbol="AAPL"
    )
)
```

### Pagination Navigation

```python
# Get paginated results with navigation
orders_page = await client.get_orders(page=1, per_page=100)

# Navigate through pages
if orders_page.has_next:
    next_page = await orders_page.next_page()

if orders_page.has_previous:
    prev_page = await orders_page.previous_page()
```

## Type Definitions

The SDK includes comprehensive type definitions for all data structures:

- `BrokerOrder`: Order information
- `BrokerPosition`: Position information
- `BrokerAccount`: Account information
- `BrokerBalance`: Balance information
- `BrokerInfo`: Broker information
- `BrokerConnection`: Connection information
- `OrderResponse`: Order operation responses
- `PaginatedResult`: Paginated data responses

## Error Types

- `AuthenticationError`: Authentication failures
- `ApiError`: API request failures
- `ValidationError`: Invalid request parameters
- `ConnectionError`: Network connectivity issues

## Requirements

- Python 3.8+
- aiohttp
- pydantic

## License

MIT License
