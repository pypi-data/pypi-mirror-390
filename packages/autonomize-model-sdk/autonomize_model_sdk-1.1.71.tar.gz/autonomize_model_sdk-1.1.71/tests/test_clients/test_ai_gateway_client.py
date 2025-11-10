"""Tests for AIGatewayClient."""

import json
from unittest.mock import MagicMock, patch

import httpx
import pytest

from modelhub.clients.ai_gateway_client import AIGatewayClient
from autonomize.core.credential import ModelhubCredential
from autonomize.exceptions.core.credentials import (
    ModelHubAPIException,
    ModelHubBadRequestException,
    ModelhubUnauthorizedException,
)


@pytest.fixture
def mock_credential():
    """Create a mock ModelhubCredential."""
    credential = MagicMock(spec=ModelhubCredential)
    credential.get_token.return_value = "sk-test-virtual-key"
    return credential


@pytest.fixture
def ai_gateway_client():
    """Create an AIGatewayClient instance for testing."""
    return AIGatewayClient(
        virtual_key="sk-test-virtual-key",
        gateway_url="https://test-gateway.com"
    )


class TestAIGatewayClient:
    """Test cases for AIGatewayClient."""

    def test_init(self, ai_gateway_client):
        """Test client initialization."""
        assert ai_gateway_client.gateway_url == "https://test-gateway.com"
        assert ai_gateway_client.base_url == "https://test-gateway.com/genesis-platform/ai-gateway"
        assert ai_gateway_client.health_readiness_endpoint == "https://test-gateway.com/genesis-platform/ai-gateway/health/readiness"
        assert ai_gateway_client.health_liveliness_endpoint == "https://test-gateway.com/genesis-platform/ai-gateway/health/liveliness"

    def test_init_default_gateway_url(self):
        """Test client initialization with default gateway URL."""
        client = AIGatewayClient(virtual_key="sk-test-key")
        assert client.gateway_url == "https://genesis.dev-v2.platform.autonomize.dev"


    def test_health_check_success(self, ai_gateway_client):
        """Test successful health check using dedicated health endpoints."""
        # Mock the AIGatewayClient.request method directly
        with patch.object(ai_gateway_client, 'request') as mock_request:
            # Configure request method to return different responses for different endpoints
            def mock_request_side_effect(method, endpoint, **kwargs):
                if endpoint == "/health/liveliness":
                    return '"I\'m alive!"'  # Return string for liveliness
                elif endpoint == "/health/readiness":
                    return {
                        "status": "connected",
                        "db": "connected",
                        "cache": None,
                        "litellm_version": "1.76.1"
                    }
                else:
                    raise ValueError(f"Unexpected endpoint: {endpoint}")

            mock_request.side_effect = mock_request_side_effect

            result = ai_gateway_client.health_check()

            assert result["status"] == "healthy"
            assert result["gateway_url"] == "https://test-gateway.com"
            assert result["auth_valid"] is True
            assert result["liveliness"] == "I'm alive!"
            assert result["readiness"]["status"] == "connected"
            assert result["readiness"]["db"] == "connected"

    def test_health_check_failure(self, ai_gateway_client):
        """Test health check failure with network errors."""
        # Mock the AIGatewayClient.request method to raise an exception
        with patch.object(ai_gateway_client, 'request') as mock_request:
            mock_request.side_effect = Exception("Connection failed")

            result = ai_gateway_client.health_check()

            assert result["status"] == "unhealthy"
            assert result["gateway_url"] == "https://test-gateway.com"
            assert "Connection failed" in result["liveliness"]
            assert result["auth_valid"] is True

    def test_health_check_auth_failure(self, ai_gateway_client):
        """Test health check with authentication failure (401/403)."""
        # Mock the AIGatewayClient.request method to raise HTTPStatusError
        with patch.object(ai_gateway_client, 'request') as mock_request:
            # Create a mock response with status_code
            mock_error_response = MagicMock()
            mock_error_response.status_code = 401

            mock_request.side_effect = httpx.HTTPStatusError(
                "401 Unauthorized", request=MagicMock(), response=mock_error_response
            )

            result = ai_gateway_client.health_check()

            assert result["status"] == "unhealthy"
            assert result["gateway_url"] == "https://test-gateway.com"
            assert result["auth_valid"] is False
            assert result["liveliness"] == "HTTP 401"

    def test_health_check_partial_success(self, ai_gateway_client):
        """Test health check with liveliness success but readiness failure."""
        # Mock the AIGatewayClient.request method
        with patch.object(ai_gateway_client, 'request') as mock_request:
            def mock_request_side_effect(method, endpoint, **kwargs):
                if endpoint == "/health/liveliness":
                    return '"I\'m alive!"'
                elif endpoint == "/health/readiness":
                    # Simulate 500 error
                    mock_error_response = MagicMock()
                    mock_error_response.status_code = 500
                    raise httpx.HTTPStatusError(
                        "500 Internal Server Error",
                        request=MagicMock(),
                        response=mock_error_response
                    )
                else:
                    raise ValueError(f"Unexpected endpoint: {endpoint}")

            mock_request.side_effect = mock_request_side_effect

            result = ai_gateway_client.health_check()

            assert result["status"] == "unhealthy"  # Overall unhealthy due to readiness failure
            assert result["gateway_url"] == "https://test-gateway.com"
            assert result["auth_valid"] is True  # Liveliness worked
            assert result["liveliness"] == "I'm alive!"
            assert result["readiness"] == "HTTP 500"

    @patch('httpx.Client')
    def test_request_get_success(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with GET request."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"test": "data"}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        result = ai_gateway_client.request("GET", "/test/endpoint")

        assert result == {"test": "data"}
        mock_client_instance.request.assert_called_once()

    @patch('httpx.Client')
    def test_request_post_json_success(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with POST request and JSON payload."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"result": "success"}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        result = ai_gateway_client.request("POST", "/test/endpoint", json={"input": "data"})

        assert result == {"result": "success"}
        call_args = mock_client_instance.request.call_args
        kwargs = call_args.kwargs
        assert kwargs["method"] == "POST"
        assert kwargs["json"] == {"input": "data"}

    @patch('httpx.Client')
    def test_request_binary_response(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with binary response."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "image/png"}
        mock_response.content = b"binary_data"

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        result = ai_gateway_client.request("GET", "/test/image")

        assert result == b"binary_data"

    @patch('httpx.Client')
    def test_request_with_params(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with query parameters."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"data": "filtered"}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        result = ai_gateway_client.request("GET", "/test/endpoint", params={"filter": "active"})

        assert result == {"data": "filtered"}
        call_args = mock_client_instance.request.call_args
        kwargs = call_args.kwargs
        assert kwargs["params"] == {"filter": "active"}

    @patch('httpx.Client')
    def test_request_put_method(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with PUT request."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"result": "updated"}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        result = ai_gateway_client.request("PUT", "/test/endpoint/123", json={"name": "test"})

        assert result == {"result": "updated"}
        call_args = mock_client_instance.request.call_args
        kwargs = call_args.kwargs
        assert kwargs["method"] == "PUT"
        assert kwargs["json"] == {"name": "test"}

    @patch('httpx.Client')
    def test_request_delete_method(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with DELETE request."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"result": "deleted"}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        result = ai_gateway_client.request("DELETE", "/test/endpoint/123")

        assert result == {"result": "deleted"}
        call_args = mock_client_instance.request.call_args
        kwargs = call_args.kwargs
        assert kwargs["method"] == "DELETE"

    @patch('httpx.Client')
    def test_request_patch_method(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with PATCH request."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"result": "patched"}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        result = ai_gateway_client.request("PATCH", "/test/endpoint/123", json={"status": "active"})

        assert result == {"result": "patched"}
        call_args = mock_client_instance.request.call_args
        kwargs = call_args.kwargs
        assert kwargs["method"] == "PATCH"
        assert kwargs["json"] == {"status": "active"}

    @patch('httpx.Client')
    def test_request_custom_headers(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with custom headers."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"result": "success"}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        custom_headers = {"X-Custom-Header": "custom-value", "User-Agent": "test-agent"}
        result = ai_gateway_client.request("GET", "/test/endpoint", headers=custom_headers)

        assert result == {"result": "success"}
        call_args = mock_client_instance.request.call_args
        kwargs = call_args.kwargs
        # Check that both Authorization and custom headers are present
        assert "Authorization" in kwargs["headers"]
        assert kwargs["headers"]["Authorization"] == "Bearer sk-test-virtual-key"
        assert kwargs["headers"]["X-Custom-Header"] == "custom-value"
        assert kwargs["headers"]["User-Agent"] == "test-agent"

    @patch('httpx.Client')
    def test_request_400_bad_request_error(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with 400 Bad Request error."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request: Invalid parameters"

        mock_client_instance = MagicMock()
        mock_client_instance.request.side_effect = httpx.HTTPStatusError(
            "400 Bad Request", request=MagicMock(), response=mock_response
        )
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        with pytest.raises(ModelHubBadRequestException) as exc_info:
            ai_gateway_client.request("POST", "/test/endpoint", json={"invalid": "data"})

        assert "Request failed with status 400: Bad Request" in str(exc_info.value)

    @patch('httpx.Client')
    def test_request_401_unauthorized_error(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with 401 Unauthorized error."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized: Invalid token"

        mock_client_instance = MagicMock()
        mock_client_instance.request.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized", request=MagicMock(), response=mock_response
        )
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        with pytest.raises(ModelhubUnauthorizedException) as exc_info:
            ai_gateway_client.request("GET", "/test/endpoint")

        assert "Request failed with status 401: Unauthorized" in str(exc_info.value)

    @patch('httpx.Client')
    def test_request_403_forbidden_error(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with 403 Forbidden error."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden: Access denied"

        mock_client_instance = MagicMock()
        mock_client_instance.request.side_effect = httpx.HTTPStatusError(
            "403 Forbidden", request=MagicMock(), response=mock_response
        )
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        with pytest.raises(ModelhubUnauthorizedException) as exc_info:
            ai_gateway_client.request("GET", "/test/endpoint")

        assert "Request failed with status 403: Forbidden" in str(exc_info.value)

    @patch('httpx.Client')
    def test_request_500_server_error(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with 500 Internal Server Error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_client_instance = MagicMock()
        mock_client_instance.request.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=MagicMock(), response=mock_response
        )
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        with pytest.raises(ModelHubAPIException) as exc_info:
            ai_gateway_client.request("GET", "/test/endpoint")

        assert "Request failed with status 500: Internal Server Error" in str(exc_info.value)

    @patch('httpx.Client')
    def test_request_network_error(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with network connection error."""
        mock_client_instance = MagicMock()
        mock_client_instance.request.side_effect = httpx.RequestError("Connection failed")
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        with pytest.raises(ModelHubAPIException) as exc_info:
            ai_gateway_client.request("GET", "/test/endpoint")

        assert "Connection failed" in str(exc_info.value)

    @patch('httpx.Client')
    def test_request_timeout_error(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with timeout error."""
        mock_client_instance = MagicMock()
        mock_client_instance.request.side_effect = httpx.TimeoutException("Request timed out")
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        with pytest.raises(ModelHubAPIException) as exc_info:
            ai_gateway_client.request("GET", "/test/endpoint")

        assert "Request timed out" in str(exc_info.value)

    @patch('httpx.Client')
    def test_request_content_type_header(self, mock_httpx_client, ai_gateway_client):
        """Test that Content-Type header is automatically added for JSON requests."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"result": "success"}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        ai_gateway_client.request("POST", "/test/endpoint", json={"data": "test"})

        call_args = mock_client_instance.request.call_args
        kwargs = call_args.kwargs
        assert kwargs["headers"]["Content-Type"] == "application/json"
        assert kwargs["headers"]["Authorization"] == "Bearer sk-test-virtual-key"

    @patch('httpx.Client')
    def test_request_no_content_type_for_non_json(self, mock_httpx_client, ai_gateway_client):
        """Test that Content-Type header is not added for non-JSON requests."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"result": "success"}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        ai_gateway_client.request("GET", "/test/endpoint")

        call_args = mock_client_instance.request.call_args
        kwargs = call_args.kwargs
        assert "Content-Type" not in kwargs["headers"]
        assert kwargs["headers"]["Authorization"] == "Bearer sk-test-virtual-key"

    @patch('httpx.Client')
    def test_request_custom_timeout(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with custom timeout."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"result": "success"}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        result = ai_gateway_client.request("GET", "/test/endpoint", timeout=60)

        assert result == {"result": "success"}
        # Check that httpx.Client was called with the custom timeout
        mock_httpx_client.assert_called_once_with(verify=True, timeout=60)

    @patch('httpx.Client')
    def test_request_default_timeout(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method uses default timeout when not specified."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"result": "success"}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        result = ai_gateway_client.request("GET", "/test/endpoint")

        assert result == {"result": "success"}
        # Check that httpx.Client was called with the default timeout (30)
        mock_httpx_client.assert_called_once_with(verify=True, timeout=30)

    @patch('httpx.Client')
    def test_request_malformed_json_response(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with malformed JSON response."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.side_effect = ValueError("Invalid JSON")

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        # Should handle JSON parsing errors gracefully
        with pytest.raises(ValueError):
            ai_gateway_client.request("GET", "/test/endpoint")

    @patch('httpx.Client')
    def test_request_unknown_content_type(self, mock_httpx_client, ai_gateway_client):
        """Test generic request method with unknown content type returns raw content."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.content = b"Hello World"

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        result = ai_gateway_client.request("GET", "/test/endpoint")

        assert result == b"Hello World"  # Should return raw bytes for non-JSON content

    @patch('httpx.Client')
    def test_request_method_case_insensitive(self, mock_httpx_client, ai_gateway_client):
        """Test that HTTP methods are converted to uppercase."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"result": "success"}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        result = ai_gateway_client.request("post", "/test/endpoint", json={"data": "test"})

        call_args = mock_client_instance.request.call_args
        kwargs = call_args.kwargs
        assert kwargs["method"] == "POST"  # Should be uppercase
