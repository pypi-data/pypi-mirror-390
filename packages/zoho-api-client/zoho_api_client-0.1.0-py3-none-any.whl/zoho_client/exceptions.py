"""Excepciones personalizadas para el cliente de Zoho."""


class ZohoAPIError(Exception):
    """Excepción base para errores de la API de Zoho."""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ZohoAuthError(ZohoAPIError):
    """Error de autenticación."""
    pass


class ZohoRateLimitError(ZohoAPIError):
    """Error de límite de tasa excedido."""
    pass


class ZohoValidationError(ZohoAPIError):
    """Error de validación de datos."""
    pass