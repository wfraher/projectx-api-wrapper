import requests
import json
from typing import Dict, Any, Optional
from urllib.parse import urljoin
from datetime import datetime, timedelta
from pathlib import Path
import os

class ProjectXAPI:
    """Python wrapper for ProjectX Gateway API."""
    
    def __init__(self, username: str, api_key: str, base_url: str = "https://api.topstepx.com"):
        """
        Initialize the ProjectX API client.
        
        Args:
            username (str): ProjectX username
            api_key (str): ProjectX API key
            base_url (str): Base URL for the API
        """
        self.username = username
        self.api_key = api_key
        self.base_url = base_url
        self.token = None
        self.token_expiry = None
        self.token_file = Path.home() / ".projectx" / "token.json"
        self.session = requests.Session()
        
    def _load_cached_token(self) -> Optional[Dict]:
        """Load cached token from file if it exists and is still valid."""
        try:
            if not self.token_file.exists():
                return None
                
            with open(self.token_file, 'r') as f:
                data = json.load(f)
                
            # Check if token is expired
            expiry = datetime.fromisoformat(data['expiry'])
            if datetime.now() >= expiry:
                return None
                
            return data
        except Exception:
            return None
            
    def _save_token(self, token: str, expiry: datetime):
        """Save token to file."""
        try:
            # Create directory if it doesn't exist
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'token': token,
                'expiry': expiry.isoformat()
            }
            
            with open(self.token_file, 'w') as f:
                json.dump(data, f)
                
            # Set restrictive permissions on the token file
            os.chmod(self.token_file, 0o600)
        except Exception as e:
            print(f"Warning: Could not save token to file: {e}")
    
    def login(self) -> str:
        """
        Authenticate with ProjectX API and get a session token.
        
        Returns:
            str: Session token
            
        Raises:
            Exception: If authentication fails
        """
        # Try to load cached token first
        cached = self._load_cached_token()
        if cached:
            self.token = cached['token']
            self.token_expiry = datetime.fromisoformat(cached['expiry'])
            return self.token
            
        # If no valid cached token, perform login
        url = f"{self.base_url}/api/Auth/loginKey"
        payload = {
            "userName": self.username,
            "apiKey": self.api_key
        }
        headers = {
            "accept": "text/plain",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('success'):
                error_msg = data.get('errorMessage', 'Unknown error')
                raise Exception(f"Authentication failed: {error_msg}")
                
            self.token = data['token']
            # Set token expiry to 24 hours from now
            self.token_expiry = datetime.now() + timedelta(hours=24)
            
            # Save token to file
            self._save_token(self.token, self.token_expiry)
            
            return self.token
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Authentication request failed: {str(e)}")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request to the ProjectX API.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Dict[str, Any]: API response as dictionary
        """
        # Ensure we have a valid token
        if not self.token or (self.token_expiry and datetime.now() >= self.token_expiry):
            self.login()
        
        # Update session headers with current token
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        url = urljoin(self.base_url, endpoint)
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information."""
        return self._make_request("GET", "/api/Account")
    
    def get_trading_history(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get trading history.
        
        Args:
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
        """
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self._make_request("GET", "/api/Trading/History", params=params)
    
    def place_order(self, account_id: int, contract_id: str, order_type: int, side: int, 
                   size: int, limit_price: Optional[float] = None, 
                   stop_price: Optional[float] = None, trail_price: Optional[float] = None,
                   custom_tag: Optional[str] = None, linked_order_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Place a new order.
        
        Args:
            account_id (int): The account ID
            contract_id (str): The contract ID (e.g., "CON.F.US.EP.M25")
            order_type (int): The order type:
                1 = Limit
                2 = Market
                4 = Stop
                5 = TrailingStop
                6 = JoinBid
                7 = JoinAsk
            side (int): The side of the order:
                0 = Bid (buy)
                1 = Ask (sell)
            size (int): The size of the order
            limit_price (float, optional): The limit price for the order
            stop_price (float, optional): The stop price for the order
            trail_price (float, optional): The trail price for the order
            custom_tag (str, optional): An optional custom tag for the order
            linked_order_id (int, optional): The linked order id
            
        Returns:
            Dict[str, Any]: Order placement response
        """
        data = {
            "accountId": account_id,
            "contractId": contract_id,
            "type": order_type,
            "side": side,
            "size": size,
            "limitPrice": limit_price,
            "stopPrice": stop_price,
            "trailPrice": trail_price,
            "customTag": custom_tag,
            "linkedOrderId": linked_order_id
        }
        return self._make_request("POST", "/api/Order/place", json=data)
    
    def get_open_orders(self) -> Dict[str, Any]:
        """Get all open orders."""
        return self._make_request("GET", "/api/Orders/Open")
    
    def cancel_order(self, account_id: int, order_id: int) -> Dict[str, Any]:
        """
        Cancel an existing order.
        
        Args:
            account_id (int): The account ID that the order belongs to
            order_id (int): The ID of the order to cancel
            
        Returns:
            Dict[str, Any]: Response indicating success or failure of the cancellation
        """
        data = {
            "accountId": account_id,
            "orderId": order_id
        }
        return self._make_request("POST", "/api/Order/cancel", json=data)
    
    def get_positions(self) -> Dict[str, Any]:
        """Get current positions."""
        return self._make_request("GET", "/api/Positions")
    
    def validate_session(self) -> bool:
        """
        Validate the current session token.
        
        Returns:
            bool: True if session is valid, False otherwise
            
        Raises:
            Exception: If validation request fails
        """
        try:
            response = self._make_request("POST", "/api/Auth/validate")
            return response.get('success', False)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Session validation failed: {str(e)}")
    
    def search_accounts(self, only_active: bool = True) -> Dict[str, Any]:
        """
        Search for accounts.
        
        Args:
            only_active (bool): If True, only return active accounts
            
        Returns:
            Dict[str, Any]: List of accounts matching the search criteria
        """
        data = {
            "onlyActiveAccounts": only_active
        }
        return self._make_request("POST", "/api/Account/search", json=data)
    
    def search_contracts(self, search_text: str, live: bool = False) -> Dict[str, Any]:
        """
        Search for contracts by symbol. ProjectX gives you longer IDs than the symbol names we're used to like NQM5.
        They also don't align with the purely numeric IDs we have from the CME, they're formatted like "CON.F.US.ENQ.H25" for March 2025 E-Mini Nasdaq 100.
        
        Args:
            search_text (str): The symbol to search for (e.g., "ES", "NQ")
            live (bool): If True, search for live contracts only
            
        Returns:
            Dict[str, Any]: List of contracts matching the search criteria
        """
        data = {
            "live": live,
            "searchText": search_text
        }
        return self._make_request("POST", "/api/Contract/search", json=data)
    
    def get_ohlcv_data(self, contract_id: str, start_time: str, end_time: str, 
                       unit: int = 3, unit_number: int = 1, limit: int = 7,
                       live: bool = False, include_partial_bar: bool = False) -> Dict[str, Any]:
        """
        Retrieve OHLCV candle data for a contract.
        
        Args:
            contract_id (str): The contract ID (e.g., "CON.F.US.EP.M25")
            start_time (str): Start time in ISO format (e.g., "2024-12-01T00:00:00Z")
            end_time (str): End time in ISO format (e.g., "2024-12-31T21:00:00Z")
            unit (int): Time unit for the bars:
                1 = Seconds
                2 = Minutes
                3 = Hours
                4 = Days
                5 = Weeks
                6 = Months
                7 = Years
            unit_number (int): Number of units per bar
            limit (int): Maximum number of bars to return
            live (bool): If True, get live data
            include_partial_bar (bool): If True, include the current partial bar
            
        Returns:
            Dict[str, Any]: OHLCV data response
        """
        data = {
            "contractId": contract_id,
            "live": live,
            "startTime": start_time,
            "endTime": end_time,
            "unit": unit,
            "unitNumber": unit_number,
            "limit": limit,
            "includePartialBar": include_partial_bar
        }
        return self._make_request("POST", "/api/History/retrieveBars", json=data)
    
    def search_orders(self, account_id: int, start_timestamp: str, end_timestamp: str) -> Dict[str, Any]:
        """
        Search for orders within a specific time range.
        
        Args:
            account_id (int): The account ID to search orders for
            start_timestamp (str): Start time in ISO format (e.g., "2024-12-30T16:48:16.003Z")
            end_timestamp (str): End time in ISO format (e.g., "2025-12-30T16:48:16.003Z")
            
        Returns:
            Dict[str, Any]: List of orders matching the search criteria
        """
        data = {
            "accountId": account_id,
            "startTimestamp": start_timestamp,
            "endTimestamp": end_timestamp
        }
        return self._make_request("POST", "/api/Order/search", json=data)
    
    def search_open_orders(self, account_id: int) -> Dict[str, Any]:
        """
        Search for open orders for a specific account.
        
        Args:
            account_id (int): The account ID to search open orders for
            
        Returns:
            Dict[str, Any]: List of open orders for the account
        """
        data = {
            "accountId": account_id
        }
        return self._make_request("POST", "/api/Order/searchOpen", json=data)
    
    def modify_order(self, account_id: int, order_id: int, size: Optional[int] = None,
                    limit_price: Optional[float] = None, stop_price: Optional[float] = None,
                    trail_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Modify an existing order.
        
        Args:
            account_id (int): The account ID that the order belongs to
            order_id (int): The ID of the order to modify
            size (int, optional): New size for the order
            limit_price (float, optional): New limit price for the order
            stop_price (float, optional): New stop price for the order
            trail_price (float, optional): New trail price for the order
            
        Returns:
            Dict[str, Any]: Response indicating success or failure of the modification
        """
        data = {
            "accountId": account_id,
            "orderId": order_id,
            "size": size,
            "limitPrice": limit_price,
            "stopPrice": stop_price,
            "trailPrice": trail_price
        }
        # Remove None values from the data
        data = {k: v for k, v in data.items() if v is not None}
        return self._make_request("POST", "/api/Order/modify", json=data)
    
    def close_position(self, account_id: int, contract_id: str) -> Dict[str, Any]:
        """
        Close a position for a specific contract.
        
        Args:
            account_id (int): The account ID that the position belongs to
            contract_id (str): The contract ID to close the position for
            
        Returns:
            Dict[str, Any]: Response indicating success or failure of the position closure
        """
        data = {
            "accountId": account_id,
            "contractId": contract_id
        }
        return self._make_request("POST", "/api/Position/closeContract", json=data)
    
    def partial_close_position(self, account_id: int, contract_id: str, size: int) -> Dict[str, Any]:
        """
        Partially close a position for a specific contract.
        
        Args:
            account_id (int): The account ID that the position belongs to
            contract_id (str): The contract ID to partially close the position for
            size (int): The number of contracts to close
            
        Returns:
            Dict[str, Any]: Response indicating success or failure of the partial position closure
        """
        data = {
            "accountId": account_id,
            "contractId": contract_id,
            "size": size
        }
        return self._make_request("POST", "/api/Position/partialCloseContract", json=data)
    
    def search_open_positions(self, account_id: int) -> Dict[str, Any]:
        """
        Search for open positions for a specific account.
        
        Args:
            account_id (int): The account ID to search open positions for
            
        Returns:
            Dict[str, Any]: List of open positions for the account
        """
        data = {
            "accountId": account_id
        }
        return self._make_request("POST", "/api/Position/searchOpen", json=data)
    
    def search_trades(self, account_id: int, start_timestamp: str, end_timestamp: str) -> Dict[str, Any]:
        """
        Search for trades within a specific time range.
        
        Args:
            account_id (int): The account ID to search trades for
            start_timestamp (str): Start time in ISO format (e.g., "2025-01-20T15:47:39.882Z")
            end_timestamp (str): End time in ISO format (e.g., "2025-01-30T15:47:39.882Z")
            
        Returns:
            Dict[str, Any]: List of trades matching the search criteria
        """
        data = {
            "accountId": account_id,
            "startTimestamp": start_timestamp,
            "endTimestamp": end_timestamp
        }
        return self._make_request("POST", "/api/Trade/search", json=data)
    