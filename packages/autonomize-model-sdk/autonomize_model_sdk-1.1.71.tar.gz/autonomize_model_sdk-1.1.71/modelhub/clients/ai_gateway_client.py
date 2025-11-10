"""Client for interacting with Genesis AI Gateway."""

from typing import Any, Dict, List, Optional, Union

import httpx

from autonomize.core.credential import ModelhubCredential
from autonomize.types.core.credential import AuthType

from ..utils import setup_logger

logger = setup_logger(__name__)


class AIGatewayClient:
    """Client for Genesis AI Gateway chat completions."""

    def __init__(
        self,
        virtual_key: str,
        gateway_url: str = "https://genesis.dev-v2.platform.autonomize.dev",
        timeout: int = 30,
        verify_ssl: bool = True,
    ):
        """
        Initialize the AIGatewayClient.

        Args:
            virtual_key: The Genesis AI Gateway virtual key (permanent token)
            gateway_url: Base URL for the Genesis AI Gateway
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        # Simple permanent token authentication as per autonomize-core documentation
        self.credential = ModelhubCredential(
            token=virtual_key,
            auth_type=AuthType.PERMANENT_TOKEN
        )
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        self.gateway_url = gateway_url
        self.base_url = f"{gateway_url}/genesis-platform/ai-gateway"
        self.health_readiness_endpoint = f"{self.base_url}/health/readiness"
        self.health_liveliness_endpoint = f"{self.base_url}/health/liveliness"
        
        logger.info(f"Initialized AIGatewayClient with gateway URL: {gateway_url}")

    def request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **httpx_kwargs
    ) -> Union[Dict[str, Any], bytes]:
        """
        Make an authenticated request to any AI Gateway endpoint.

        This is the core generic method that can handle any AI Gateway endpoint
        with proper authentication using the virtual key.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH, etc.)
            endpoint: API endpoint path (e.g., '/v1/chat/completions', '/v1/images/generations')
            json: JSON payload for POST/PUT/PATCH requests
            params: Query parameters for GET requests
            headers: Additional headers to include
            **httpx_kwargs: Additional httpx parameters (timeout, stream, etc.)

        Returns:
            Union[Dict[str, Any], bytes]: JSON response as dict, or raw bytes for binary responses

        Raises:
            ModelHubAPIException: For API errors
            ModelHubBadRequestException: For 400 errors
            ModelhubUnauthorizedException: For 401/403 errors
        """
        logger.info(f"Making {method} request to {endpoint}")

        # Build full URL
        url = f"{self.base_url}{endpoint}"

        # Prepare headers with authentication
        request_headers = {
            "Authorization": f"Bearer {self.credential.get_token()}"
        }

        # Add Content-Type for JSON requests
        if json is not None:
            request_headers["Content-Type"] = "application/json"

        # Merge with user-provided headers
        if headers:
            request_headers.update(headers)

        # Set default timeout if not provided
        if 'timeout' not in httpx_kwargs:
            httpx_kwargs['timeout'] = self.timeout

        try:
            with httpx.Client(verify=self.verify_ssl, **httpx_kwargs) as client:
                response = client.request(
                    method=method.upper(),
                    url=url,
                    json=json,
                    params=params,
                    headers=request_headers
                )

                # Handle different response types
                if response.headers.get("content-type", "").startswith("application/json"):
                    return response.json()
                else:
                    # Return raw bytes for binary responses (images, etc.)
                    return response.content

        except httpx.HTTPStatusError as e:
            error_msg = f"Request failed with status {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)

            # Map HTTP status codes to appropriate exceptions
            if e.response.status_code == 401:
                from autonomize.exceptions.core.credentials import ModelhubUnauthorizedException
                raise ModelhubUnauthorizedException(error_msg) from e
            elif e.response.status_code == 403:
                from autonomize.exceptions.core.credentials import ModelhubUnauthorizedException
                raise ModelhubUnauthorizedException(error_msg) from e
            elif e.response.status_code == 400:
                from autonomize.exceptions.core.credentials import ModelHubBadRequestException
                raise ModelHubBadRequestException(error_msg) from e
            else:
                from autonomize.exceptions.core.credentials import ModelHubAPIException
                raise ModelHubAPIException(error_msg) from e

        except httpx.RequestError as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            from autonomize.exceptions.core.credentials import ModelHubAPIException
            raise ModelHubAPIException(error_msg) from e


    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the AI Gateway using dedicated health endpoints.

        This method uses the official Genesis AI Gateway health endpoints:
        - /health/liveliness: Basic liveliness check
        - /health/readiness: Detailed readiness check

        Returns:
            Dict containing health status information including:
            - status: "healthy" or "unhealthy"
            - liveliness: Basic health status
            - readiness: Detailed health information (if available)
            - auth_valid: Whether authentication is working
        """
        logger.info("Performing AI Gateway health check using dedicated endpoints")

        try:
            headers = {
                "Authorization": f"Bearer {self.credential.get_token()}"
            }

            health_status = {
                "status": "unknown",
                "gateway_url": self.gateway_url,
                "auth_valid": True
            }

            # First, check liveliness (basic health)
            try:
                liveliness_response = self.request("GET", "/health/liveliness")

                if isinstance(liveliness_response, str):
                    health_status["liveliness"] = liveliness_response.strip('"')  # Remove quotes from "I'm alive!"
                    health_status["status"] = "healthy"
                else:
                    # If we get a dict response (error), check for status codes
                    health_status["liveliness"] = "Error response"
                    health_status["status"] = "unhealthy"

            except Exception as e:
                if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                    status_code = e.response.status_code
                    health_status["liveliness"] = f"HTTP {status_code}"
                    health_status["status"] = "unhealthy"
                    if status_code in [401, 403]:
                        health_status["auth_valid"] = False
                else:
                    health_status["liveliness"] = f"Network error: {str(e)}"
                    health_status["status"] = "unhealthy"

            # Then, check readiness (detailed health)
            try:
                readiness_response = self.request("GET", "/health/readiness")

                if isinstance(readiness_response, dict):
                    health_status["readiness"] = readiness_response
                    # If liveliness was healthy and we have readiness data, keep status healthy
                    if health_status["status"] == "healthy":
                        health_status["status"] = "healthy"
                else:
                    # If we get a string response (unexpected), mark as error
                    health_status["readiness"] = "Unexpected response format"
                    health_status["status"] = "unhealthy"

            except Exception as e:
                if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                    status_code = e.response.status_code
                    health_status["readiness"] = f"HTTP {status_code}"
                    health_status["status"] = "unhealthy"
                    if status_code in [401, 403]:
                        health_status["auth_valid"] = False
                else:
                    health_status["readiness"] = f"Network error: {str(e)}"
                    health_status["status"] = "unhealthy"

            return health_status

        except Exception as e:
            logger.warning(f"Health check failed completely: {str(e)}")
            return {
                "status": "unhealthy",
                "gateway_url": self.gateway_url,
                "error": str(e),
                "auth_valid": False
            }
