"""Módulo para Zoho Books."""

from typing import Dict, Any, Optional
from .base import ZohoModule


class ZohoBooks(ZohoModule):
    """Cliente para Zoho Books API v3."""

    MODULE_PATH = "books/v3"

    def __init__(self, client, organization_id: str):
        """Zoho Books requiere organization_id."""
        if not organization_id:
            raise ValueError("organization_id es requerido para Zoho Books")
        super().__init__(client, organization_id)

    def get_invoices(
            self,
            status: Optional[str] = None,
            page: int = 1,
            per_page: int = 200
    ) -> Dict[str, Any]:
        """
        Obtiene facturas.

        Args:
            status: Filtrar por estado (sent, draft, paid, etc.)
            page: Número de página
            per_page: Registros por página

        Returns:
            Lista de facturas
        """
        params = {"page": page, "per_page": per_page}
        if status:
            params["status"] = status

        endpoint = self._build_endpoint("invoices")
        return self.client.get(endpoint, params=params)

    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Obtiene una factura específica."""
        endpoint = self._build_endpoint(f"invoices/{invoice_id}")
        return self.client.get(endpoint)

    def create_invoice(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva factura."""
        endpoint = self._build_endpoint("invoices")
        return self.client.post(endpoint, json=data)

    def get_customers(self, page: int = 1, per_page: int = 200) -> Dict[str, Any]:
        """Obtiene lista de clientes."""
        params = {"page": page, "per_page": per_page}
        endpoint = self._build_endpoint("contacts")
        return self.client.get(endpoint, params=params)

    def get_items(self, page: int = 1, per_page: int = 200) -> Dict[str, Any]:
        """Obtiene lista de items/productos."""
        params = {"page": page, "per_page": per_page}
        endpoint = self._build_endpoint("items")
        return self.client.get(endpoint, params=params)
