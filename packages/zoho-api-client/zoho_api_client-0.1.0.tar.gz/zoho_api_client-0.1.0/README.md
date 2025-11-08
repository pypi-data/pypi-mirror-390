# Zoho API Client

Cliente Python unificado para interactuar con las APIs de Zoho (CRM, Books, Inventory, etc.)

## Características

- ✅ Soporte para múltiples módulos de Zoho (CRM, Books, Inventory)
- ✅ Autenticación OAuth2 automática con refresco de tokens
- ✅ Manejo automático de rate limiting
- ✅ Reintentos automáticos en caso de errores
- ✅ Type hints completos
- ✅ Manejo de errores robusto
- ✅ Logging integrado
- ✅ Soporte para todas las regiones de Zoho

## Instalación

### Desde PyPI (cuando esté publicado)

```bash
pip install zoho-api-client
```

### Desde el código fuente

```bash
git clone https://github.com/tuusuario/zoho-api-client.git
cd zoho-api-client
pip install -e .
```

### Para desarrollo

```bash
pip install -e ".[dev]"
```

## Configuración

Primero necesitas obtener tus credenciales de Zoho:

1. Ve a [Zoho API Console](https://api-console.zoho.com/)
2. Crea una nueva aplicación Self Client
3. Genera un refresh token

## Uso Rápido

### Cliente Base

```python
from zoho_client import ZohoClient

# Inicializar el cliente
client = ZohoClient(
    client_id="tu_client_id",
    client_secret="tu_client_secret",
    refresh_token="tu_refresh_token",
    region="com"  # o "eu", "in", etc.
)

# Hacer peticiones genéricas
response = client.get("crm/v2/Leads")
```

### Zoho CRM

```python
from zoho_client import ZohoClient, ZohoCRM

# Inicializar cliente y módulo CRM
client = ZohoClient(
    client_id="tu_client_id",
    client_secret="tu_client_secret",
    refresh_token="tu_refresh_token"
)

crm = ZohoCRM(client)

# Obtener leads
leads = crm.get_records("Leads", page=1, per_page=200)

# Buscar un contacto específico
contacts = crm.search_records(
    "Contacts",
    criteria="(Email:equals:john@example.com)"
)

# Crear un nuevo lead
new_lead = crm.create_record("Leads", {
    "Last_Name": "Doe",
    "Email": "john.doe@example.com",
    "Company": "Acme Corp"
})

# Actualizar un registro
updated = crm.update_record("Leads", "lead_id", {
    "Phone": "+1234567890"
})

# Eliminar un registro
crm.delete_record("Leads", "lead_id")
```

### Zoho Books

```python
from zoho_client import ZohoClient, ZohoBooks

client = ZohoClient(
    client_id="tu_client_id",
    client_secret="tu_client_secret",
    refresh_token="tu_refresh_token"
)

# Zoho Books requiere organization_id
books = ZohoBooks(client, organization_id="tu_org_id")

# Obtener facturas
invoices = books.get_invoices(status="sent", page=1)

# Obtener una factura específica
invoice = books.get_invoice("invoice_id")

# Crear una nueva factura
new_invoice = books.create_invoice({
    "customer_id": "123456",
    "line_items": [
        {
            "item_id": "789",
            "quantity": 2,
            "rate": 100
        }
    ]
})

# Obtener clientes
customers = books.get_customers()

# Obtener items
items = books.get_items()
```

### Zoho Inventory

```python
from zoho_client import ZohoClient, ZohoInventory

client = ZohoClient(
    client_id="tu_client_id",
    client_secret="tu_client_secret",
    refresh_token="tu_refresh_token"
)

inventory = ZohoInventory(client, organization_id="tu_org_id")

# Obtener items del inventario
items = inventory.get_items()

# Obtener un item específico
item = inventory.get_item("item_id")

# Actualizar stock
inventory.update_stock("item_id", quantity=100)
```

## Configuración Avanzada

### Regiones

```python
# Para región europea
client = ZohoClient(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    region="eu"
)

# Regiones disponibles: "com", "eu", "in", "com.cn", "com.au"
```

### Timeout y Reintentos

```python
client = ZohoClient(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    timeout=60,  # Timeout en segundos
    max_retries=5  # Número de reintentos
)
```

### Logging Personalizado

```python
import logging

# Crear tu logger personalizado
my_logger = logging.getLogger("mi_app")
my_logger.setLevel(logging.DEBUG)

client = ZohoClient(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    logger_instance=my_logger
)
```

## Manejo de Errores

```python
from zoho_client import (
    ZohoClient,
    ZohoCRM,
    ZohoAPIError,
    ZohoAuthError,
    ZohoRateLimitError,
    ZohoValidationError
)

client = ZohoClient(...)
crm = ZohoCRM(client)

try:
    leads = crm.get_records("Leads")
except ZohoAuthError as e:
    print(f"Error de autenticación: {e}")
    print(f"Código de estado: {e.status_code}")
except ZohoRateLimitError as e:
    print(f"Límite de tasa excedido: {e}")
    # Esperar antes de reintentar
except ZohoValidationError as e:
    print(f"Error de validación: {e}")
    print(f"Respuesta: {e.response}")
except ZohoAPIError as e:
    print(f"Error general de API: {e}")
```

## Migración desde tu Clase Anterior

### Antes

```python
from settings import Settings
from zoho_manager import ZohoManager

settings = Settings()
zoho = ZohoManager(settings)
response = zoho.get("contacts")
```

### Ahora

```python
from zoho_client import ZohoClient, ZohoBooks

# Opción 1: Cliente genérico
client = ZohoClient(
    client_id="...",
    client_secret="...",
    refresh_token="..."
)
response = client.get("books/v3/contacts", params={"organization_id": "..."})

# Opción 2: Módulo específico (recomendado)
books = ZohoBooks(client, organization_id="...")
contacts = books.get_customers()
```

## Desarrollo

### Configurar entorno de desarrollo

```bash
# Clonar el repositorio
git clone https://github.com/tuusuario/zoho-api-client.git
cd zoho-api-client

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar en modo desarrollo
pip install -e ".[dev]"

# Instalar pre-commit hooks
pre-commit install
```

### Ejecutar tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=zoho_client --cov-report=html

# Tests específicos
pytest tests/test_client.py
```

### Formatear código

```bash
# Formatear con black
black zoho_client tests

# Verificar con flake8
flake8 zoho_client tests

# Type checking con mypy
mypy zoho_client
```

## Estructura del Proyecto

```
zoho-api-client/
├── zoho_client/
│   ├── __init__.py
│   ├── client.py          # Cliente base
│   ├── auth.py            # Autenticación OAuth2
│   ├── exceptions.py      # Excepciones personalizadas
│   ├── utils.py           # Utilidades
│   └── modules/
│       ├── __init__.py
│       ├── base.py        # Clase base para módulos
│       ├── crm.py         # Zoho CRM
│       ├── books.py       # Zoho Books
│       └── inventory.py   # Zoho Inventory
├── tests/
│   ├── __init__.py
│   ├── test_client.py
│   ├── test_auth.py
│   └── test_modules.py
├── setup.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Roadmap

- [ ] Soporte para más módulos de Zoho (Desk, Projects, etc.)
- [ ] Cliente async con aiohttp
- [ ] Cache de respuestas
- [ ] Paginación automática
- [ ] Webhooks
- [ ] CLI para operaciones comunes
- [ ] Documentación completa con ejemplos

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Changelog

### v0.1.0 (2025-10-11)

- Versión inicial
- Soporte para Zoho CRM, Books e Inventory
- Autenticación OAuth2 automática
- Rate limiting básico
- Manejo de errores robusto

## Soporte

- 📧 Email: tu@email.com
- 🐛 Issues: [GitHub Issues](https://github.com/tuusuario/zoho-api-client/issues)
- 📖 Documentación: [GitHub Wiki](https://github.com/tuusuario/zoho-api-client/wiki)

## Créditos

Desarrollado por [Tu Nombre](https://github.com/tuusuario)
