# Crear archivo test_installation.py
import zoho_client
from zoho_client import ZohoClient, ZohoCRM

print("✅ Paquete instalado correctamente!")
print(f"Versión: {zoho_client.__version__}")
print(f"ZohoClient: {ZohoClient}")
print(f"ZohoCRM: {ZohoCRM}")