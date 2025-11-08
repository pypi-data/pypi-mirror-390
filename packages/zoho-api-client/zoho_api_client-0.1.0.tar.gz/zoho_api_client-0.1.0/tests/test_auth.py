"""Tests para ZohoAuth."""

import pytest
from zoho_client.auth import ZohoAuth
from zoho_client.exceptions import ZohoAuthError


class TestZohoAuth:
    """Tests para la clase ZohoAuth."""

    def test_init(self):
        """Test de inicialización."""
        auth = ZohoAuth(
            client_id="test_id",
            client_secret="test_secret",
            refresh_token="test_token",
            region="com"
        )
        assert auth.client_id == "test_id"
        assert auth.region == "com"

    def test_auth_url_by_region(self):
        """Test de URL de auth por región."""
        auth_com = ZohoAuth("id", "secret", "token", "com")
        assert auth_com.auth_url == "https://accounts.zoho.com/oauth/v2/token"

        auth_eu = ZohoAuth("id", "secret", "token", "eu")
        assert auth_eu.auth_url == "https://accounts.zoho.eu/oauth/v2/token"

    def test_token_caching(self, mocker):
        """Test de caché de token."""
        auth = ZohoAuth("id", "secret", "token")

        # Mock de la respuesta
        mock_response = mocker.Mock()
        mock_response.json.return_value = {"access_token": "new_token"}
        mock_response.raise_for_status = mocker.Mock()

        mocker.patch('requests.post', return_value=mock_response)

        # Primera llamada - debe hacer petición
        token1 = auth.get_access_token()
        assert token1 == "new_token"

        # Segunda llamada - debe usar caché
        token2 = auth.get_access_token()
        assert token2 == "new_token"

        # Solo debe haber una llamada HTTP
        assert mocker.patch.call_count == 1