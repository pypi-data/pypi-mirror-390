# my_cli_utilities_common/http_helpers.py
"""
Unified HTTP client helpers and factory.
Provides standardized HTTP client creation and request handling.
"""

import httpx
import json
import asyncio
from typing import Optional, Dict, Any, Tuple
import logging

# Initialize logger
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger('http_helpers')


# ============================================================================
# HTTP Client Factory - Unified client creation
# ============================================================================

class HTTPClientFactory:
    """Factory for creating standardized HTTP clients."""
    
    # Default connection limits
    DEFAULT_MAX_KEEPALIVE = 10
    DEFAULT_MAX_CONNECTIONS = 20
    
    @staticmethod
    def create_sync_client(
        timeout: float = 30.0,
        auth: Optional[Tuple[str, str]] = None,
        follow_redirects: bool = True,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Client:
        """
        Create synchronous HTTP client with standard settings.
        
        Args:
            timeout: Request timeout in seconds
            auth: Optional (username, password) tuple for basic auth
            follow_redirects: Whether to follow redirects automatically
            headers: Optional custom headers
            
        Returns:
            Configured httpx.Client instance
        """
        return httpx.Client(
            timeout=httpx.Timeout(timeout),
            auth=auth,
            follow_redirects=follow_redirects,
            headers=headers,
            limits=httpx.Limits(
                max_keepalive_connections=HTTPClientFactory.DEFAULT_MAX_KEEPALIVE
            )
        )
    
    @staticmethod
    def create_async_client(
        timeout: float = 30.0,
        auth: Optional[Tuple[str, str]] = None,
        follow_redirects: bool = True,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.AsyncClient:
        """
        Create async HTTP client with standard settings.
        
        Args:
            timeout: Request timeout in seconds
            auth: Optional (username, password) tuple for basic auth
            follow_redirects: Whether to follow redirects automatically
            headers: Optional custom headers
            
        Returns:
            Configured httpx.AsyncClient instance
        """
        return httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            auth=auth,
            follow_redirects=follow_redirects,
            headers=headers,
            limits=httpx.Limits(
                max_keepalive_connections=HTTPClientFactory.DEFAULT_MAX_KEEPALIVE,
                max_connections=HTTPClientFactory.DEFAULT_MAX_CONNECTIONS
            )
        )


# ============================================================================
# Legacy helper functions (kept for backward compatibility)
# ============================================================================

def log_error(message: str, request_url: str = None, response_text: str = None):
    """Helper function to log formatted error messages."""
    error_msg = f"{message}"
    if request_url:
        error_msg += f" (URL: {request_url})"
    logger.error(error_msg)
    if response_text:
        # Truncate long responses for readability
        truncated_response = response_text[:500] + "..." if len(response_text) > 500 else response_text
        logger.debug(f"Raw response: {truncated_response}")


def make_sync_request(
    url: str,
    params: Optional[Dict] = None,
    method: str = "GET",
    timeout: float = 30.0,
    auth: Optional[Tuple[str, str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Makes a synchronous HTTP request and handles common errors.
    
    Args:
        url: Request URL
        params: Query parameters or request body
        method: HTTP method (GET, POST, etc.)
        timeout: Request timeout in seconds
        auth: Optional (username, password) tuple
        
    Returns:
        JSON response as dict or None on error
    """
    try:
        with HTTPClientFactory.create_sync_client(timeout=timeout, auth=auth) as client:
            if method.upper() == "GET":
                response = client.get(url, params=params)
            elif method.upper() == "POST":
                response = client.post(url, json=params)
            elif method.upper() == "PUT":
                response = client.put(url, json=params)
            elif method.upper() == "DELETE":
                response = client.delete(url, params=params)
            else:
                log_error(f"Unsupported HTTP method: {method}", url)
                return None
            
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        log_error(f"HTTP error {exc.response.status_code}", str(exc.request.url), exc.response.text)
    except httpx.RequestError as exc:
        request_url_for_error = str(exc.request.url) if hasattr(exc.request, 'url') and exc.request.url else url
        log_error(f"Request error: {type(exc).__name__}", request_url_for_error)
    except json.JSONDecodeError:
        log_error("Failed to decode JSON response", url)
    return None


async def make_async_request(
    url: str,
    params: Optional[Dict] = None,
    method: str = "GET",
    timeout: float = 30.0,
    auth: Optional[Tuple[str, str]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Makes an asynchronous HTTP request and handles common errors.
    
    Args:
        url: Request URL
        params: Query parameters or request body
        method: HTTP method (GET, POST, etc.)
        timeout: Request timeout in seconds
        auth: Optional (username, password) tuple
        headers: Optional custom headers
        
    Returns:
        JSON response as dict or None on error
    """
    try:
        async with HTTPClientFactory.create_async_client(
            timeout=timeout,
            auth=auth,
            headers=headers
        ) as client:
            if method.upper() == "GET":
                response = await client.get(url, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, json=params)
            elif method.upper() == "PUT":
                response = await client.put(url, json=params)
            elif method.upper() == "DELETE":
                response = await client.delete(url, params=params)
            else:
                log_error(f"Unsupported HTTP method: {method}", url)
                return None

            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        log_error(f"HTTP error {exc.response.status_code}", str(exc.request.url), exc.response.text)
    except httpx.RequestError as exc:
        request_url_for_error = str(exc.request.url) if hasattr(exc.request, 'url') and exc.request.url else url
        log_error(f"Request error: {type(exc).__name__}", request_url_for_error)
    except json.JSONDecodeError:
        log_error("Failed to decode JSON response", url)
    return None

if __name__ == '__main__':
    # Example usage (synchronous)
    logger.info("Testing sync request...")
    sync_data = make_sync_request("https://jsonplaceholder.typicode.com/todos/1")
    if sync_data:
        logger.info("Sync data: " + json.dumps(sync_data, indent=2))
    else:
        logger.error("Sync request failed.")

    # Example usage (asynchronous)
    async def main_async_test():
        logger.info("Testing async request...")
        async_data = await make_async_request("https://jsonplaceholder.typicode.com/posts/1")
        if async_data:
            logger.info("Async data: " + json.dumps(async_data, indent=2))
        else:
            logger.error("Async request failed.")

    asyncio.run(main_async_test()) 