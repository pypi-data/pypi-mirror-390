# tai-keycloak
Keycloak development complete framework

## Configuración Rápida

Para empezar a administrar tu instancia de Keycloak de forma rápida, solo necesitas exportar una variable de entorno:

```bash
# Configuración completa
export MAIN_KEYCLOAK_URL=admin:secret@keycloak.company.com:8080

# Solo usuario (password por defecto: 'admin')
export MAIN_KEYCLOAK_URL=myuser@keycloak.company.com:8080

# Solo host y puerto (user/password por defecto: 'admin/admin')
export MAIN_KEYCLOAK_URL=keycloak.company.com:8080

# Solo host - detección inteligente de puerto
export MAIN_KEYCLOAK_URL=localhost                    # → http://localhost:8090
export MAIN_KEYCLOAK_URL=myapp.azurewebsites.net      # → https://myapp.azurewebsites.net
export MAIN_KEYCLOAK_URL=keycloak.company.com         # → https://keycloak.company.com
```

### Detección Inteligente de Puerto y Protocolo

La librería detecta automáticamente el puerto y protocolo óptimo según el ciclo de desarrollo:

#### Desarrollo Local
- `localhost` o `127.0.0.1` → puerto `8090`, protocolo `http`

#### Azure Web Apps  
- Hosts `*.azurewebsites.net` → puerto `443`, protocolo `https`
- Azure Web Apps incluyen SSL gratuito y automático

#### Producción
- Otros hosts → puerto `443`, protocolo `https`

#### Puertos Explícitos
- Puerto `443` o `8443` → protocolo `https`
- Otros puertos → protocolo `http`

### Ejemplo de Uso

```python
from tai_keycloak.service import KeycloakAdminService

# Con MAIN_KEYCLOAK_URL configurado, solo necesitas:
service = KeycloakAdminService()

# Probar conexión
result = service.test_connection()
print(result.message)
```

## Configuración Avanzada

Si necesitas más control, puedes usar variables individuales o configuración programática:

```bash
# Variables individuales (prefijo TAIKC_)
export TAIKC_URL=https://keycloak.company.com:8443
export TAIKC_USERNAME=admin
export TAIKC_PASSWORD=secret
export TAIKC_REALM=master
```

```python
from tai_keycloak.service import KeycloakAdminService, KeycloakConfig

# Configuración programática
config = KeycloakConfig(
    url="https://keycloak.company.com:8443",
    username="admin",
    password="secret",
    realm="master"
)

service = KeycloakAdminService(config)
```
