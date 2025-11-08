"""Cliente principal para la API de Zoho."""

import logging
import time
from typing import Optional, Dict, Any
import requests

from .auth import ZohoAuth
from .exceptions import (
    ZohoAPIError,
    ZohoAuthError,
    ZohoRateLimitError,
    ZohoValidationError,
)

logger = logging.getLogger(__name__)


class ZohoClient:
    """Cliente base para interactuar con las APIs de Zoho."""

    # URLs base por región
    REGION_URLS = {
        "com": "https://www.zohoapis.com",
        "eu": "https://www.zohoapis.eu",
        "in": "https://www.zohoapis.in",
        "com.cn": "https://www.zohoapis.com.cn",
        "com.au": "https://www.zohoapis.com.au",
    }

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            refresh_token: str,
            region: str = "com",
            timeout: int = 30,
            max_retries: int = 3,
            logger_instance: Optional[logging.Logger] = None
    ):
        """
        Inicializa el cliente de Zoho.

        Args:
            client_id: Client ID de Zoho
            client_secret: Client Secret de Zoho
            refresh_token: Refresh token de Zoho
            region: Región de Zoho (com, eu, in, etc.)
            timeout: Timeout para las peticiones HTTP
            max_retries: Número máximo de reintentos
            logger_instance: Logger personalizado
        """
        self.region = region
        self.timeout = timeout
        self.max_retries = max_retries

        # Configurar auth
        self.auth = ZohoAuth(client_id, client_secret, refresh_token, region)

        # Logger
        self.logger = logger_instance or logger

        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.2  # 200ms entre peticiones

    @property
    def base_url(self) -> str:
        """Retorna la URL base según la región."""
        return self.REGION_URLS.get(self.region, self.REGION_URLS["com"])

    def _build_headers(self) -> Dict[str, str]:
        """Construye los headers de autenticación."""
        token = self.auth.get_access_token()
        return {
            "Authorization": f"Zoho-oauthtoken {token}",
            "Content-Type": "application/json",
        }

    def _build_url(self, endpoint: str) -> str:
        """Construye la URL completa."""
        base = self.base_url.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base}/{endpoint}"

    def _rate_limit(self):
        """Implementa rate limiting básico."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Procesa la respuesta y maneja errores.

        Args:
            response: Respuesta de requests

        Returns:
            Datos JSON de la respuesta

        Raises:
            ZohoAPIError: Para errores de la API
        """
        try:
            data = response.json()
        except ValueError:
            data = {"raw_response": response.text}

        # Manejo de errores por código de estado
        if response.status_code == 401:
            raise ZohoAuthError(
                "Error de autenticación",
                status_code=401,
                response=data
            )
        elif response.status_code == 429:
            raise ZohoRateLimitError(
                "Límite de tasa excedido",
                status_code=429,
                response=data
            )
        elif response.status_code == 400:
            raise ZohoValidationError(
                "Error de validación",
                status_code=400,
                response=data
            )
        elif not response.ok:
            raise ZohoAPIError(
                f"Error en la API: {response.status_code}",
                status_code=response.status_code,
                response=data
            )

        return data

    def _request(
            self,
            method: str,
            endpoint: str,
            params: Optional[Dict] = None,
            json: Optional[Dict] = None,
            data: Optional[Dict] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Realiza una petición HTTP con reintentos y manejo de errores.

        Args:
            method: Método HTTP (GET, POST, PUT, DELETE, etc.)
            endpoint: Endpoint de la API
            params: Parámetros de query string
            json: Datos JSON para el body
            data: Datos form para el body
            **kwargs: Argumentos adicionales para requests

        Returns:
            Respuesta JSON de la API
        """
        url = self._build_url(endpoint)

        for attempt in range(self.max_retries):
            try:
                self._rate_limit()
                headers = self._build_headers()

                response = requests.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    params=params,
                    json=json,
                    data=data,
                    timeout=self.timeout,
                    **kwargs
                )

                # Manejar token expirado
                if response.status_code == 401 and attempt < self.max_retries - 1:
                    self.logger.warning("⚠️ Token expirado, refrescando...")
                    self.auth.get_access_token(force_refresh=True)
                    continue

                return self._handle_response(response)

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if attempt == self.max_retries - 1:
                    raise ZohoAPIError(f"Error de conexión: {e}") from e
                self.logger.warning(f"Reintento {attempt + 1}/{self.max_retries}")
                time.sleep(2 ** attempt)  # Backoff exponencial

        raise ZohoAPIError("Máximo de reintentos alcanzado")

    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Realiza una petición GET."""
        return self._request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, json: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Realiza una petición POST."""
        return self._request("POST", endpoint, json=json, **kwargs)

    def put(self, endpoint: str, json: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Realiza una petición PUT."""
        return self._request("PUT", endpoint, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realiza una petición DELETE."""
        return self._request("DELETE", endpoint, **kwargs)

    def patch(self, endpoint: str, json: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Realiza una petición PATCH."""
        return self._request("PATCH", endpoint, json=json, **kwargs)
