"""Módulo para Zoho CRM."""

from typing import Dict, Any, Optional, List
from .base import ZohoModule


class ZohoCRM(ZohoModule):
    """Cliente para Zoho CRM API v2."""

    MODULE_PATH = "crm/v2"

    def get_records(
            self,
            module: str,
            page: int = 1,
            per_page: int = 200,
            fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene registros de un módulo.

        Args:
            module: Nombre del módulo (Leads, Contacts, Deals, etc.)
            page: Número de página
            per_page: Registros por página (máx 200)
            fields: Campos a retornar

        Returns:
            Respuesta con los registros
        """
        params = {
            "page": page,
            "per_page": min(per_page, 200)
        }

        if fields:
            params["fields"] = ",".join(fields)

        endpoint = self._build_endpoint(module)
        return self.client.get(endpoint, params=params)

    def get_record(self, module: str, record_id: str) -> Dict[str, Any]:
        """Obtiene un registro específico."""
        endpoint = self._build_endpoint(f"{module}/{record_id}")
        return self.client.get(endpoint)

    def create_record(self, module: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo registro."""
        endpoint = self._build_endpoint(module)
        payload = {"data": [data]}
        return self.client.post(endpoint, json=payload)

    def update_record(
            self,
            module: str,
            record_id: str,
            data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Actualiza un registro existente."""
        endpoint = self._build_endpoint(f"{module}/{record_id}")
        payload = {"data": [data]}
        return self.client.put(endpoint, json=payload)

    def delete_record(self, module: str, record_id: str) -> Dict[str, Any]:
        """Elimina un registro."""
        endpoint = self._build_endpoint(f"{module}/{record_id}")
        return self.client.delete(endpoint)

    def search_records(
            self,
            module: str,
            criteria: str,
            page: int = 1,
            per_page: int = 200
    ) -> Dict[str, Any]:
        """
        Busca registros usando criterios.

        Args:
            module: Nombre del módulo
            criteria: Criterio de búsqueda (ej: "(Email:equals:john@example.com)")
            page: Número de página
            per_page: Registros por página

        Returns:
            Respuesta con los registros encontrados
        """
        params = {
            "criteria": criteria,
            "page": page,
            "per_page": min(per_page, 200)
        }

        endpoint = self._build_endpoint(f"{module}/search")
        return self.client.get(endpoint, params=params)
