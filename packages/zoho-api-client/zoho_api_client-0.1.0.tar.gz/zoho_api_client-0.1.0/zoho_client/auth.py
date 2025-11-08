"""Gestión de autenticación para Zoho."""

import time
import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)


class ZohoAuth:
    """Gestiona la autenticación OAuth2 con Zoho."""

    AUTH_URL = "https://accounts.zoho.com/oauth/v2/token"
    TOKEN_LIFETIME = 3600  # 1 hora en segundos

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            refresh_token: str,
            region: str = "com"
    ):
        """
        Inicializa el gestor de autenticación.

        Args:
            client_id: Client ID de Zoho
            client_secret: Client Secret de Zoho
            refresh_token: Refresh token de Zoho
            region: Región de Zoho (com, eu, in, etc.)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.region = region

        self._access_token: Optional[str] = None
        self._token_expiry: float = 0

    @property
    def auth_url(self) -> str:
        """URL de autenticación según la región."""
        return f"https://accounts.zoho.{self.region}/oauth/v2/token"

    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Obtiene un access token válido, refrescándolo si es necesario.

        Args:
            force_refresh: Fuerza el refresco del token

        Returns:
            Access token válido
        """
        if not force_refresh and self._is_token_valid():
            return self._access_token

        return self._refresh_access_token()

    def _is_token_valid(self) -> bool:
        """Verifica si el token actual es válido."""
        if not self._access_token:
            return False
        # Considera el token inválido 5 minutos antes de su expiración
        return time.time() < (self._token_expiry - 300)

    def _refresh_access_token(self) -> str:
        """Refresca el access token usando el refresh token."""
        payload = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }

        try:
            response = requests.post(self.auth_url, data=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            self._access_token = data["access_token"]
            self._token_expiry = time.time() + self.TOKEN_LIFETIME

            logger.info("🔑 Access token refrescado exitosamente")
            return self._access_token

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error al refrescar token: {e}")
            raise ZohoAuthError(f"Error al refrescar token: {e}") from e
