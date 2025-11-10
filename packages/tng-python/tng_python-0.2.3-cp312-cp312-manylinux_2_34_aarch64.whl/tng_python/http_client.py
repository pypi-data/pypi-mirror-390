import json
import os
from typing import Dict, Optional

import requests

from .config import get_base_url, get_api_key

DEBUG = os.getenv('DEBUG') == '1'


class TngHttpClient:
    """HTTP client for TNG API communication"""

    def __init__(self):
        self.base_url = get_base_url()
        self.api_key = get_api_key()

    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to TNG API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            from .version import __version__
            version = __version__
        except ImportError:
            version = "0.1.0"  # fallback

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': f'TNG-Python/{version}'
        }

        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key[:20]}...' if DEBUG else f'Bearer {self.api_key}'

        if DEBUG:
            print(f"\n[DEBUG] HTTP {method} {url}")
            print(f"[DEBUG] Headers: {headers}")
            if data:
                print(f"[DEBUG] Request data: {json.dumps(data, indent=2)[:500]}...")

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers={k: v if k != 'Authorization' else f'Bearer {self.api_key}' for k, v in headers.items()}, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, headers={k: v if k != 'Authorization' else f'Bearer {self.api_key}' for k, v in headers.items()}, json=data, timeout=10)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers={k: v if k != 'Authorization' else f'Bearer {self.api_key}' for k, v in headers.items()}, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if DEBUG:
                print(f"[DEBUG] Response status: {response.status_code}")
                try:
                    resp_json = response.json()
                    print(f"[DEBUG] Response data: {json.dumps(resp_json, indent=2)[:1000]}...")
                except:
                    print(f"[DEBUG] Response text: {response.text[:500]}...")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            if DEBUG:
                print(f"[DEBUG] HTTP request failed: {e}")
            print(f"HTTP request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            if DEBUG:
                print(f"[DEBUG] Failed to decode JSON response: {e}")
            print(f"Failed to decode JSON response: {e}")
            return None

    def ping(self) -> Optional[Dict]:
        """Call the ping endpoint to get version information"""
        return self._make_request('ping')

    def get_api_version(self) -> Optional[str]:
        """Get the API version from ping endpoint"""
        ping_response = self.ping()
        if ping_response and 'current_version' in ping_response:
            return ping_response['current_version'].get('pip_version')
        return None

    def validate_api_key(self) -> bool:
        """Validate API key by making an authenticated request"""
        if not self.api_key:
            return False

        response = self._make_request('ping')
        return response is not None

    def get_user_stats(self) -> Optional[Dict]:
        """Get user statistics from API"""
        return self._make_request('cli/tng_python/stats', method='GET')


def get_http_client() -> TngHttpClient:
    """Get HTTP client instance"""
    return TngHttpClient()
