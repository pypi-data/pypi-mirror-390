"""
HTTP client wrapper with session management, rate limiting, and error handling.
"""

import time
import requests
import aiohttp
from typing import Optional, Dict, Any, Union
from .exceptions import APIError, RateLimitError, AuthenticationError
from .auth import AuthManager


class HTTPClient:
    """
    Synchronous HTTP client for Interpals API.
    """
    
    BASE_URL = "https://api.interpals.net"
    
    def __init__(self, auth_manager: AuthManager, max_retries: int = 3):
        """
        Initialize HTTP client.
        
        Args:
            auth_manager: Authentication manager instance
            max_retries: Maximum number of retry attempts
        """
        self.auth = auth_manager
        self.max_retries = max_retries
        self.session = requests.Session()
        self._last_request_time = 0
        self._min_request_interval = 1.0  # 1 second between requests (rate limiting)
    
    def _wait_for_rate_limit(self):
        """Implement rate limiting by waiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last)
        
        self._last_request_time = time.time()
    
    def _handle_response(self, response: requests.Response) -> Any:
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response: Response object from requests
            
        Returns:
            Parsed JSON data or None
            
        Raises:
            AuthenticationError: For 401 status
            RateLimitError: For 429 status
            APIError: For other error statuses
        """
        if response.status_code == 200 or response.status_code == 201:
            try:
                return response.json()
            except ValueError:
                return None
        
        elif response.status_code == 204:
            return None
        
        elif response.status_code == 401:
            raise AuthenticationError("Unauthorized - invalid or expired session", status_code=401)
        
        elif response.status_code == 403:
            raise APIError("Forbidden - insufficient permissions", status_code=403)
        
        elif response.status_code == 404:
            raise APIError("Resource not found", status_code=404)
        
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After", 60)
            raise RateLimitError("Rate limit exceeded", retry_after=int(retry_after))
        
        else:
            error_msg = f"API request failed with status {response.status_code}"
            try:
                error_data = response.json()
                error_msg = error_data.get("error", error_data.get("message", error_msg))
            except Exception:
                pass
            
            raise APIError(error_msg, status_code=response.status_code, response=response)
    
    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., "/v1/account/self")
            data: Form data for the request
            json: JSON data for the request
            params: Query parameters
            files: Files to upload
            headers: Additional headers
            
        Returns:
            Parsed response data
            
        Raises:
            APIError: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        # Merge auth headers with custom headers
        req_headers = self.auth.get_headers()
        if headers:
            req_headers.update(headers)
        
        # Rate limiting
        self._wait_for_rate_limit()
        
        # Retry logic
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    data=data,
                    json=json,
                    params=params,
                    files=files,
                    headers=req_headers,
                    timeout=30,
                )
                
                return self._handle_response(response)
            
            except RateLimitError:
                # Don't retry rate limit errors
                raise
            
            except requests.RequestException as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    time.sleep(2 ** attempt)
                    continue
        
        raise APIError(f"Request failed after {self.max_retries} attempts: {str(last_exception)}")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a GET request."""
        return self.request("GET", endpoint, params=params)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Make a POST request."""
        return self.request("POST", endpoint, data=data, json=json, files=files, headers=headers)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a PUT request."""
        return self.request("PUT", endpoint, data=data, json=json)
    
    def delete(self, endpoint: str) -> Any:
        """Make a DELETE request."""
        return self.request("DELETE", endpoint)
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()


class AsyncHTTPClient:
    """
    Asynchronous HTTP client for Interpals API.
    """
    
    BASE_URL = "https://api.interpals.net"
    
    def __init__(self, auth_manager: AuthManager, max_retries: int = 3):
        """
        Initialize async HTTP client.
        
        Args:
            auth_manager: Authentication manager instance
            max_retries: Maximum number of retry attempts
        """
        self.auth = auth_manager
        self.max_retries = max_retries
        self._session: Optional[aiohttp.ClientSession] = None
        self._last_request_time = 0
        self._min_request_interval = 1.0
    
    async def _ensure_session(self):
        """Ensure aiohttp session is created."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
    
    async def _wait_for_rate_limit(self):
        """Implement rate limiting by waiting between requests."""
        import asyncio
        
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - time_since_last)
        
        self._last_request_time = time.time()
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Any:
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response: Response object from aiohttp
            
        Returns:
            Parsed JSON data or None
            
        Raises:
            AuthenticationError: For 401 status
            RateLimitError: For 429 status
            APIError: For other error statuses
        """
        if response.status in (200, 201):
            try:
                return await response.json()
            except Exception:
                return None
        
        elif response.status == 204:
            return None
        
        elif response.status == 401:
            raise AuthenticationError("Unauthorized - invalid or expired session", status_code=401)
        
        elif response.status == 403:
            raise APIError("Forbidden - insufficient permissions", status_code=403)
        
        elif response.status == 404:
            raise APIError("Resource not found", status_code=404)
        
        elif response.status == 429:
            retry_after = response.headers.get("Retry-After", 60)
            raise RateLimitError("Rate limit exceeded", retry_after=int(retry_after))
        
        else:
            error_msg = f"API request failed with status {response.status}"
            try:
                error_data = await response.json()
                error_msg = error_data.get("error", error_data.get("message", error_msg))
            except Exception:
                pass
            
            raise APIError(error_msg, status_code=response.status)
    
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Make an async HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., "/v1/account/self")
            data: Form data for the request
            json: JSON data for the request
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Parsed response data
            
        Raises:
            APIError: If request fails
        """
        import asyncio
        
        await self._ensure_session()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        # Merge auth headers with custom headers
        req_headers = self.auth.get_headers()
        if headers:
            req_headers.update(headers)
        
        # Rate limiting
        await self._wait_for_rate_limit()
        
        # Retry logic
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                async with self._session.request(
                    method=method,
                    url=url,
                    data=data,
                    json=json,
                    params=params,
                    headers=req_headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    return await self._handle_response(response)
            
            except RateLimitError:
                # Don't retry rate limit errors
                raise
            
            except aiohttp.ClientError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)
                    continue
        
        raise APIError(f"Request failed after {self.max_retries} attempts: {str(last_exception)}")
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a GET request."""
        return await self.request("GET", endpoint, params=params)
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Make a POST request."""
        return await self.request("POST", endpoint, data=data, json=json, headers=headers)
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Make a PUT request."""
        return await self.request("PUT", endpoint, data=data, json=json, headers=headers)
    
    async def delete(self, endpoint: str) -> Any:
        """Make a DELETE request."""
        return await self.request("DELETE", endpoint)
    
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

