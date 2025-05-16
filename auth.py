import json
import os
from typing import Dict, Optional
from pathlib import Path
import requests
from datetime import datetime, timedelta

class ProjectXAuth:
    """Handles authentication and token management for ProjectX API."""
    
    def __init__(self, username: str, api_key: str, base_url: str = "https://gateway-api-demo.s2f.projectx.com"):
        """
        Initialize the authentication handler.
        
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
            
    def get_token(self) -> str:
        """
        Get a valid session token, refreshing if necessary.
        
        Returns:
            str: Valid session token
        """
        if not self.token or (self.token_expiry and datetime.now() >= self.token_expiry):
            return self.login()
        return self.token 