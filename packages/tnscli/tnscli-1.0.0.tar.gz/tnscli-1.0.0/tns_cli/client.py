"""TNS API Client"""
import requests
from typing import Dict, List, Optional


class TNSClient:
    """Client for interacting with TNS REST API"""

    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip('/')

    def check_availability(self, name: str) -> Dict:
        """Check if a domain is available"""
        response = requests.get(f"{self.api_url}/available/{name}")
        response.raise_for_status()
        return response.json()

    def resolve(self, name: str) -> Dict:
        """Resolve a domain to addresses"""
        response = requests.get(f"{self.api_url}/resolve/{name}")
        response.raise_for_status()
        return response.json()

    def lookup_by_owner(self, address: str) -> List[Dict]:
        """Find domains by owner address"""
        response = requests.get(f"{self.api_url}/lookup/owner/{address}")
        response.raise_for_status()
        return response.json()

    def lookup_by_coldkey(self, address: str) -> List[Dict]:
        """Find domains by coldkey address"""
        response = requests.get(f"{self.api_url}/lookup/coldkey/{address}")
        response.raise_for_status()
        return response.json()

    def lookup_by_hotkey(self, address: str) -> List[Dict]:
        """Find domains by hotkey address"""
        response = requests.get(f"{self.api_url}/lookup/hotkey/{address}")
        response.raise_for_status()
        return response.json()

    def search(self, query: str, limit: int = 50) -> Dict:
        """Search for domains"""
        response = requests.get(f"{self.api_url}/search", params={"q": query, "limit": limit})
        response.raise_for_status()
        return response.json()

    def get_stats(self) -> Dict:
        """Get platform statistics"""
        response = requests.get(f"{self.api_url}/stats")
        response.raise_for_status()
        return response.json()

    def health(self) -> Dict:
        """Check API health"""
        response = requests.get(f"{self.api_url}/health")
        response.raise_for_status()
        return response.json()
