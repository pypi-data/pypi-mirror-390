"""Tests para módulos de Zoho."""

import pytest
from zoho_client.modules.crm import ZohoCRM
from zoho_client.modules.books import ZohoBooks


class TestZohoCRM:
    """Tests para ZohoCRM."""

    def test_get_records(self, zoho_crm, mocker):
        """Test de obtener registros."""
        mock_response = {"data": [{"id": "1", "Last_Name": "Doe"}]}
        mocker.patch.object(zoho_crm.client, 'get', return_value=mock_response)

        result = zoho_crm.get_records("Leads")
        assert result == mock_response

        zoho_crm.client.get.assert_called_once()

    def test_create_record(self, zoho_crm, mocker):
        """Test de crear registro."""
        mock_response = {"data": [{"id": "123", "status": "success"}]}
        mocker.patch.object(zoho_crm.client, 'post', return_value=mock_response)

        data = {"Last_Name": "Doe", "Email": "john@example.com"}
        result = zoho_crm.create_record("Leads", data)

        assert result == mock_response

    def test_search_records(self, zoho_crm, mocker):
        """Test de búsqueda."""
        mock_response = {"data": [{"id": "1"}]}
        mocker.patch.object(zoho_crm.client, 'get', return_value=mock_response)

        criteria = "(Email:equals:john@example.com)"
        result = zoho_crm.search_records("Contacts", criteria)

        assert result == mock_response


class TestZohoBooks:
    """Tests para ZohoBooks."""

    def test_requires_organization_id(self, zoho_client):
        """Test que organization_id es requerido."""
        with pytest.raises(ValueError):
            ZohoBooks(zoho_client, organization_id=None)

    def test_get_invoices(self, zoho_books, mocker):
        """Test de obtener facturas."""
        mock_response = {"invoices": [{"invoice_id": "1"}]}
        mocker.patch.object(zoho_books.client, 'get', return_value=mock_response)

        result = zoho_books.get_invoices(status="sent")
        assert result == mock_response

    def test_create_invoice(self, zoho_books, mocker):
        """Test de crear factura."""
        mock_response = {"invoice": {"invoice_id": "123"}}
        mocker.patch.object(zoho_books.client, 'post', return_value=mock_response)

        data = {"customer_id": "456", "line_items": []}
        result = zoho_books.create_invoice(data)

        assert result == mock_response