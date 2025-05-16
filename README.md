# ProjectX API Python Wrapper

A Python wrapper for the ProjectX Gateway API that provides a simple interface for interacting with the ProjectX trading platform.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from projectx_api import ProjectXAPI

# Initialize the API client
api = ProjectXAPI(api_key="your_api_key_here")

# Get account information
account_info = api.get_account_info()

# Place an order
order = api.place_order(
    symbol="BTC/USD",
    side="BUY",
    quantity=0.1,
    order_type="MARKET"
)

# Get open orders
open_orders = api.get_open_orders()

# Cancel an order
api.cancel_order(order_id="order_123")

# Get trading history
history = api.get_trading_history(
    start_date="2024-01-01",
    end_date="2024-03-20"
)
```

## Features

- Account information retrieval
- Order placement and management
- Position tracking
- Trading history
- Error handling
- Type hints for better IDE support

## Error Handling

The wrapper includes built-in error handling and will raise appropriate exceptions for:
- Invalid API keys
- Network errors
- Invalid requests
- Rate limiting

## Contributing

Feel free to submit issues and enhancement requests! 