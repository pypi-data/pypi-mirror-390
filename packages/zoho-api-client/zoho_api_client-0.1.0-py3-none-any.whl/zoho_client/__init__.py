"""
Zoho API Client - Cliente unificado para APIs de Zoho.
"""

__version__ = "0.1.0"

from .client import ZohoClient
from .modules.crm import ZohoCRM
from .modules.books import ZohoBooks
from .modules.inventory import ZohoInventory
from .exceptions import (
    ZohoAPIError,
    ZohoAuthError,
    ZohoRateLimitError,
    ZohoValidationError,
)

__all__ = [
    "ZohoClient",
    "ZohoCRM",
    "ZohoBooks",
    "ZohoInventory",
    "ZohoAPIError",
    "ZohoAuthError",
    "ZohoRateLimitError",
    "ZohoValidationError",
]