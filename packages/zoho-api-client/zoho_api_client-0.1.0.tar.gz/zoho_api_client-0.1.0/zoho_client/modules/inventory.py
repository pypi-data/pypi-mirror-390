"""Módulo para Zoho Inventory."""

from typing import Dict, Any, Optional
from .base import ZohoModule


class ZohoInventory(ZohoModule):
    """Cliente para Zoho Inventory API v1."""

    MODULE_PATH = "inventory/v1"

    def __init__(self, client, organization_id: str):
        """Zoho Inventory requiere organization_id."""
        if not organization_id:
            raise ValueError("organization_id es requerido para Zoho Inventory")
        super().__init__(client, organization_id)

    def get_items(self, page: int = 1, per_page: int = 200) -> Dict[str, Any]:
        """Obtiene items del inventario."""
        params = {"page": page, "per_page": per_page}
        endpoint = self._build_endpoint("items")
        return self.client.get(endpoint, params=params)

    def get_item(self, item_id: str) -> Dict[str, Any]:
        """Obtiene un item específico."""
        endpoint = self._build_endpoint(f"items/{item_id}")
        return self.client.get(endpoint)

    def update_stock(self, item_id: str, quantity: int) -> Dict[str, Any]:
        """Actualiza el stock de un item."""
        endpoint = self._build_endpoint(f"items/{item_id}")
        data = {"stock_on_hand": quantity}
        return self.client.put(endpoint, json=data)