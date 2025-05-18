import os
from projectx_api import ProjectXAPI
from datetime import datetime, timedelta

def main():
    # Get credentials from environment variables
    username = os.getenv('PROJECTX_USERNAME')
    api_key = os.getenv('PROJECTX_API_KEY')
    
    if not username or not api_key:
        print("Please set PROJECTX_USERNAME and PROJECTX_API_KEY environment variables")
        return

    # --- 1. Initialize API Client and Authenticate ---
    api = ProjectXAPI(
        username=username,
        api_key=api_key
    )
    print("Logging in...")
    token = api.login()
    print(f"Login successful! Token: {token[:8]}...")

    # --- 2. Validate Session ---
    print("\nValidating session...")
    if api.validate_session():
        print("Session is valid!")
    else:
        print("Session validation failed!")
        return

    # --- 3. Discover Active Accounts ---
    print("\nSearching for active accounts...")
    accounts = api.search_accounts(only_active=True)
    print("Accounts:", accounts)
    if not accounts.get('accounts'):
        print("No active accounts found!")
        return
    account_id = accounts['accounts'][0]['id']
    print(f"Using account ID: {account_id}")

    # --- 4. Discover Contracts (e.g., ES futures) ---
    print("\nSearching for ES futures contracts...")
    contracts = api.search_contracts(search_text="ES", live=False)
    print("Contracts:", contracts)
    if not contracts.get('contracts'):
        print("No ES contracts found!")
        return
    contract_id = contracts['contracts'][0]['id']
    print(f"Using contract ID: {contract_id}")

    # --- 5. Discover Open Positions ---
    print("\nSearching for open positions...")
    open_positions = api.search_open_positions(account_id=account_id)
    print("Open Positions:", open_positions)
    if open_positions.get('positions'):
        for pos in open_positions['positions']:
            print(f"Open position: {pos['contractId']} size={pos['size']} avgPrice={pos['averagePrice']}")
    else:
        print("No open positions found.")

    # --- 6. Place a Market Order ---
    print("\nPlacing a market order to SELL 1 contract...")
    order = api.place_order(
        account_id=account_id,
        contract_id=contract_id,
        order_type=2,  # Market
        side=1,        # Sell
        size=1
    )
    print("Order placed:", order)

    # --- 7. Search for Orders (last 10 days) ---
    print("\nSearching for orders in the last 10 days...")
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=10)
    orders = api.search_orders(
        account_id=account_id,
        start_timestamp=start_time.isoformat() + "Z",
        end_timestamp=end_time.isoformat() + "Z"
    )
    print("Orders:", orders)

    # --- 8. Search for Open Orders ---
    print("\nSearching for open orders...")
    open_orders = api.search_open_orders(account_id=account_id)
    print("Open Orders:", open_orders)
    if open_orders.get('orders'):
        order_id = open_orders['orders'][0]['orderId']
        print(f"Using open order ID: {order_id}")

        # --- 9. Modify the First Open Order ---
        print(f"\nModifying open order {order_id} (set stop price to 1604)...")
        modify_result = api.modify_order(
            account_id=account_id,
            order_id=order_id,
            stop_price=1604.0
        )
        print("Modify result:", modify_result)

        # --- 10. Cancel the First Open Order ---
        print(f"\nCancelling open order {order_id}...")
        cancel_result = api.cancel_order(
            account_id=account_id,
            order_id=order_id
        )
        print("Cancel result:", cancel_result)
    else:
        print("No open orders to modify or cancel.")

    # --- 11. Market Data: Fetch OHLCV Data ---
    print("\nFetching OHLCV data for the contract (last 7 days, 1h bars)...")
    ohlcv_data = api.get_ohlcv_data(
        contract_id=contract_id,
        start_time=(end_time - timedelta(days=7)).isoformat() + "Z",
        end_time=end_time.isoformat() + "Z",
        unit=3,  # Hours
        unit_number=1,
        limit=168,
        live=False,
        include_partial_bar=False
    )
    print("OHLCV Data:", ohlcv_data)

    # --- 12. Trade History: Fetch Trades (last 10 days) ---
    print("\nSearching for trades in the last 10 days...")
    trades = api.search_trades(
        account_id=account_id,
        start_timestamp=start_time.isoformat() + "Z",
        end_timestamp=end_time.isoformat() + "Z"
    )
    print("Trades:", trades)

    # --- 13. Position Management: Close and Partial Close ---
    if open_positions.get('positions'):
        pos_contract_id = open_positions['positions'][0]['contractId']
        print(f"\nClosing position for contract {pos_contract_id}...")
        close_result = api.close_position(
            account_id=account_id,
            contract_id=pos_contract_id
        )
        print("Close position result:", close_result)

        print(f"\nPartially closing position for contract {pos_contract_id} (size=1)...")
        partial_close_result = api.partial_close_position(
            account_id=account_id,
            contract_id=pos_contract_id,
            size=1
        )
        print("Partial close result:", partial_close_result)
    else:
        print("No open positions to close or partially close.")

if __name__ == "__main__":
    main() 