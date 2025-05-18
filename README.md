# ProjectX / TopStepX API Python Wrapper

TopStepX/ProjectX has a new API and it's time we use it! This is a comprehensive Python wrapper for the ProjectX Gateway API that provides a simple and intuitive interface for interacting with the ProjectX trading platform. This wrapper handles authentication, session management, and provides methods for all major trading operations.

## Features

- **Authentication & Session Management**
  - Secure token storage and automatic refresh
  - Session validation
  - Error handling for authentication failures

- **Account Management**
  - Search for active trading accounts
  - Account status verification

- **Order Management**
  - Place new orders (Market, Limit, Stop, etc.)
  - Search and filter orders
  - Modify existing orders
  - Cancel orders
  - Track open orders

- **Position Management**
  - View open positions
  - Close positions
  - Partially close positions
  - Position tracking

- **Trade History**
  - Search trade history
  - Filter trades by date range
  - Trade analysis

- **Market Data**
  - OHLCV data retrieval
  - Customizable time frames
  - Historical data access

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from projectx_api import ProjectXAPI

# Initialize the API client
api = ProjectXAPI(
    username="your_username",
    api_key="your_api_key"
)

# Login and validate session
token = api.login()
if api.validate_session():
    print("Session is valid!")
```

## Detailed Usage Examples

### Authentication and Session Management

```python
# Login and get token
token = api.login()
print(f"Login successful! Token: {token[:50]}...")

# Validate the session
if api.validate_session():
    print("Session is valid!")
else:
    print("Session validation failed!")
```

### Account Management

```python
# Search for active accounts
accounts = api.search_accounts(only_active=True)
print("Accounts:", accounts)

# Get the first active account ID
if accounts.get('accounts'):
    account_id = accounts['accounts'][0]['id']
```

### Contract Management

```python
# Search for specific contracts (e.g., ES futures)
contracts = api.search_contracts(search_text="ES", live=False)
print("Contracts:", contracts)

# Get contract details
if contracts.get('contracts'):
    contract_id = contracts['contracts'][0]['id']
```

### Order Management

```python
# Place a market order
order = api.place_order(
    account_id=123,
    contract_id="CON.F.US.EP.M25",
    order_type=2,  # Market order
    side=1,        # Sell
    size=1
)

# Search for orders in a date range
orders = api.search_orders(
    account_id=123,
    start_timestamp="2024-01-01T00:00:00Z",
    end_timestamp="2024-12-31T23:59:59Z"
)

# Search for open orders
open_orders = api.search_open_orders(account_id=123)

# Modify an existing order
modified_order = api.modify_order(
    account_id=123,
    order_id=456,
    size=2,
    stop_price=1604.0
)

# Cancel an order
cancel_result = api.cancel_order(
    account_id=123,
    order_id=456
)
```

### Position Management

```python
# Search for open positions
positions = api.search_open_positions(account_id=123)

# Close a position completely
close_result = api.close_position(
    account_id=123,
    contract_id="CON.F.US.EP.M25"
)

# Partially close a position
partial_close_result = api.partial_close_position(
    account_id=123,
    contract_id="CON.F.US.EP.M25",
    size=1  # Close 1 contract
)
```

### Trade History

```python
# Search for trades in a date range
trades = api.search_trades(
    account_id=123,
    start_timestamp="2024-01-01T00:00:00Z",
    end_timestamp="2024-12-31T23:59:59Z"
)

# Process trade data
if trades.get('trades'):
    for trade in trades['trades']:
        print(f"Contract: {trade.get('contractId')}")
        print(f"Size: {trade.get('size')}")
        print(f"Price: {trade.get('price')}")
        print(f"Time: {trade.get('timestamp')}")
```

### Market Data

```python
# Get OHLCV data for analysis
ohlcv_data = api.get_ohlcv_data(
    contract_id="CON.F.US.EP.M25",
    start_time="2024-01-01T00:00:00Z",
    end_time="2024-12-31T23:59:59Z",
    unit=3,  # Hours
    unit_number=1,  # 1 hour bars
    limit=168,  # 7 days * 24 hours
    live=False,
    include_partial_bar=False
)
```

## API Reference

### Order Types
- 1 = Limit
- 2 = Market
- 4 = Stop
- 5 = TrailingStop
- 6 = JoinBid
- 7 = JoinAsk

### Order Sides
- 0 = Bid (buy)
- 1 = Ask (sell)

### Time Units for OHLCV Data
- 1 = Seconds
- 2 = Minutes
- 3 = Hours
- 4 = Days
- 5 = Weeks
- 6 = Months
- 7 = Years

## Error Handling

The wrapper includes comprehensive error handling for:
- Invalid API keys
- Network errors
- Invalid requests
- Rate limiting
- Session expiration
- Invalid order parameters
- Position management errors

## Token Management

The wrapper automatically handles:
- Secure token storage in a hidden directory
- Automatic token refresh when expired
- Token inclusion in all API requests
- Session validation
- Error handling for token-related issues

## Best Practices

1. **Error Handling**
   ```python
   try:
       result = api.place_order(...)
   except Exception as e:
       print(f"Error placing order: {e}")
   ```

2. **Session Management**
   ```python
   if not api.validate_session():
       api.login()  # Refresh session if needed
   ```

3. **Order Management**
   ```python
   # Always verify order parameters
   if size > 0 and contract_id:
       api.place_order(...)
   ```

## Contributing

Feel free to submit issues and enhancement requests! When contributing:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
