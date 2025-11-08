"""Clase base para módulos de Zoho."""

from typing import Optional
from ..client import ZohoClient


class ZohoModule:
    """Clase base para módulos específicos de Zoho."""

    MODULE_PATH = ""  # Debe ser sobrescrito por subclases

    def __init__(self, client: ZohoClient, organization_id: Optional[str] = None):
        """
        Inicializa el módulo.

        Args:
            client: Instancia de ZohoClient
            organization_id: ID de organización (requerido para algunos módulos)
        """
        self.client = client
        self.organization_id = organization_id

    def _build_endpoint(self, path: str = "") -> str:
        """Construye el endpoint completo para el módulo."""
        parts = [self.MODULE_PATH]

        if self.organization_id:
            parts.append(f"organization/{self.organization_id}")

        if path:
            parts.append(path.lstrip("/"))

        return "/".join(parts)