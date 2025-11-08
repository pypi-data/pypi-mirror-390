"""Tests para ZohoClient."""

import pytest
import requests
from zoho_client import ZohoClient
from zoho_client.exceptions import (
    ZohoAPIError,
    ZohoAuthError,
    ZohoRateLimitError,
    ZohoValidationError
)


class TestZohoClient:
    """Tests para la clase ZohoClient."""

    def test_init(self, mock_credentials):
        """Test de inicialización."""
        client = ZohoClient(**mock_credentials)
        assert client.region == "com"
        assert client.timeout == 30
        assert client.max_retries == 3

    def test_base_url_by_region(self, mock_credentials):
        """Test de URLs base por región."""
        regions = {
            "com": "https://www.zohoapis.com",
            "eu": "https://www.zohoapis.eu",
            "in": "https://www.zohoapis.in"
        }

        for region, expected_url in regions.items():
            mock_credentials["region"] = region
            client = ZohoClient(**mock_credentials)
            assert client.base_url == expected_url

    def test_build_url(self, zoho_client):
        """Test de construcción de URLs."""
        url = zoho_client._build_url("crm/v2/Leads")
        assert url == "https://www.zohoapis.com/crm/v2/Leads"

        url = zoho_client._build_url("/crm/v2/Leads")
        assert url == "https://www.zohoapis.com/crm/v2/Leads"

    def test_get_request(self, zoho_client, mocker):
        """Test de petición GET."""
        mock_response = mocker.Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}

        mocker.patch('requests.request', return_value=mock_response)

        result = zoho_client.get("crm/v2/Leads")
        assert result == {"data": []}

    def test_post_request(self, zoho_client, mocker):
        """Test de petición POST."""
        mock_response = mocker.Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_response.json.return_value = {"data": [{"id": "123"}]}

        mocker.patch('requests.request', return_value=mock_response)

        result = zoho_client.post("crm/v2/Leads", json={"Last_Name": "Doe"})
        assert "data" in result

    def test_auth_error_handling(self, zoho_client, mocker):
        """Test de manejo de error 401."""
        mock_response = mocker.Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "invalid_token"}

        mocker.patch('requests.request', return_value=mock_response)

        with pytest.raises(ZohoAuthError):
            zoho_client.get("crm/v2/Leads")

    def test_rate_limit_error_handling(self, zoho_client, mocker):
        """Test de manejo de error 429."""
        mock_response = mocker.Mock()
        mock_response.ok = False
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "rate_limit_exceeded"}

        mocker.patch('requests.request', return_value=mock_response)

        with pytest.raises(ZohoRateLimitError):
            zoho_client.get("crm/v2/Leads")

    def test_validation_error_handling(self, zoho_client, mocker):
        """Test de manejo de error 400."""
        mock_response = mocker.Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "invalid_data"}

        mocker.patch('requests.request', return_value=mock_response)

        with pytest.raises(ZohoValidationError):
            zoho_client.post("crm/v2/Leads", json={})

