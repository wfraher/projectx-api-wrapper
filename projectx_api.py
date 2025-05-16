import requests
from typing import Dict, Any, Optional
from urllib.parse import urljoin
from auth import ProjectXAuth

class ProjectXAPI:
    """Python wrapper for ProjectX Gateway API."""
    
    def __init__(self, username: str, api_key: str, base_url: str = "https://gateway-api-demo.s2f.projectx.com"):
        """
        Initialize the ProjectX API client.
        
        Args:
            username (str): ProjectX username
            api_key (str): ProjectX API key
            base_url (str): Base URL for the API
        """
        self.base_url = base_url
        self.auth = ProjectXAuth(username, api_key, base_url)
        self.session = requests.Session()
    
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
        # Get fresh token for each request
        token = self.auth.get_token()
        
        # Update session headers with current token
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        url = urljoin(self.base_url, endpoint)
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information."""
        return self._make_request("GET", "/account")
    
    def get_trading_history(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get trading history.
        
        Args:
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._make_request("GET", "/trading/history", params=params)
    
    def place_order(self, symbol: str, side: str, quantity: float, order_type: str = "MARKET", **kwargs) -> Dict[str, Any]:
        """
        Place a new order.
        
        Args:
            symbol (str): Trading symbol
            side (str): Order side (BUY/SELL)
            quantity (float): Order quantity
            order_type (str): Order type (MARKET/LIMIT)
            **kwargs: Additional order parameters
        """
        data = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "type": order_type,
            **kwargs
        }
        return self._make_request("POST", "/orders", json=data)
    
    def get_open_orders(self) -> Dict[str, Any]:
        """Get all open orders."""
        return self._make_request("GET", "/orders/open")
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an existing order.
        
        Args:
            order_id (str): ID of the order to cancel
        """
        return self._make_request("DELETE", f"/orders/{order_id}")
    
    def get_positions(self) -> Dict[str, Any]:
        """Get current positions."""
        return self._make_request("GET", "/positions") 