# cw_sdk — SDK simple para SharePoint (Microsoft Graph)

Pequeña librería en Python para interactuar con SharePoint Online vía Microsoft Graph: crear carpetas, subir y descargar archivos, y verificar existencia de directorios.

---

## Instalación

- PyPI: `pip install cw_sdk`
- Desde GitHub: `pip install git+https://github.com/customswatch/cw_sdk.git`

Requiere Python 3.8+.

---

## Configuración

La librería obtiene credenciales y nombres de sitio desde variables de entorno:

Necesarias para autenticación (Azure AD, aplicación tipo Confidential):

```text
secretId="<CLIENT_SECRET>"
appId="<CLIENT_ID>"
tenantId="<TENANT_ID>"
```

Sitios de SharePoint (contextos):

```text
sharepoint_site_name="CustomsWatch"           # contexto por defecto: "cw"
sharepoint_site_name_legales="CustomsWatch-Legales"  # contexto alternativo: "legales"
```

Sugerencia: si usas un archivo `.env`, recuerda cargarlo en tu aplicación (por ejemplo, con `python-dotenv`).

---

## Uso Rápido

```python
from cw_sdk import SharePointGraph

sp = SharePointGraph()

# 1) Verificar si existe una carpeta dentro de un path
existe = sp.check_dir(
    folder_name="MiCarpeta",
    base_path="Datos/ADUANAS/Robot",
    context="cw",  # ó "legales"
)
print("Existe?", existe)

# 2) Crear una carpeta dentro de base_path
nombre_creado = sp.mk_dir(
    folder_name="MiCarpeta",
    base_path="Datos/ADUANAS/Robot",
)
print("Carpeta creada:", nombre_creado)

# 3) Subir un archivo (bytes) a un directorio existente
sp.upload_file(
    base_path="Datos/ADUANAS/Robot/MiCarpeta",
    file_name="ejemplo.txt",
    content_bytes=b"Hola desde cw_sdk!",
)

# 4) Descargar un archivo (retorna bytes)
contenido = sp.download_file(
    base_path="Datos/ADUANAS/Robot/MiCarpeta",
    file_name="ejemplo.txt",
)
open("ejemplo_local.txt", "wb").write(contenido)
```

Notas de uso de `base_path`:
- En `check_dir`, `base_path` es el directorio donde buscarás `folder_name`.
- En `mk_dir`, `base_path` identifica la carpeta “padre” donde se creará `folder_name`.
- En `upload_file` y `download_file`, `base_path` es el directorio que ya contiene al archivo.

---

## API de Alto Nivel

- `SharePointGraph.check_dir(folder_name: str, base_path: str, context: str = "cw") -> bool`:
  Verifica si existe una carpeta dentro de `base_path`. Retorna `True/False`.

- `SharePointGraph.mk_dir(folder_name: str, base_path: str, context: str = "cw") -> str`:
  Crea una carpeta dentro de `base_path`. Retorna el nombre creado (puede ser renombrado por SharePoint si hay conflicto).

- `SharePointGraph.upload_file(base_path: str, file_name: str, content_bytes: bytes, context: str = "cw") -> None`:
  Sube un archivo como bytes a `base_path` con nombre `file_name`.

- `SharePointGraph.download_file(base_path: str, file_name: str, context: str = "cw") -> bytes`:
  Descarga `file_name` desde `base_path` y retorna sus bytes.

Parámetro `context`:
- `"cw"` usa la variable `sharepoint_site_name` (por defecto).
- Cualquier otro valor usa `sharepoint_site_name_legales`.

---

## Detalles Internos y Autenticación

Esta librería usa Microsoft Graph mediante `http.client` y gestiona el token con `msal` (flujo Client Credentials):

- `get_token()` obtiene y almacena el token de acceso.
- `get_site_id(context)` resuelve el `site_id` del sitio configurado.
- `get_drive_id(context)` obtiene el `drive_id` (actualmente toma el tercer drive disponible del sitio).
- `get_item_id(base_path, context)` resuelve el ítem (carpeta) apuntado por `base_path`.
- `_auth(base_path, context)` ejecuta el ciclo completo anterior cuando hace falta.

Nota: la selección del drive usa `value[2]` (tercer drive). Si el orden cambia en tu tenant, puede que debas ajustar la implementación.

Configuración de credenciales en tiempo de ejecución (opcional):

```python
sp = SharePointGraph()
sp._az_auth(secret_id="...", app_id="...", tenant_id="...")
# Luego usa los métodos de alto nivel normalmente
```

---

## Logging y Errores

La clase registra información y errores con el módulo estándar `logging`. Para ver trazas:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

Los métodos lanzan `ValueError` con mensajes descriptivos cuando ocurre un error (por ejemplo, problemas de autenticación o de red).

---

## Requisitos

- Python 3.8+
- Dependencias: `msal` (y `requests`, aunque no se usa directamente en la clase actual)

---

## Ejemplos Prácticos

1) Crear si no existe y luego subir:

```python
from cw_sdk import SharePointGraph

sp = SharePointGraph()
if not sp.check_dir("Reportes", base_path="Datos/ADUANAS/Robot"):
    sp.mk_dir("Reportes", base_path="Datos/ADUANAS/Robot")

sp.upload_file(
    base_path="Datos/ADUANAS/Robot/Reportes",
    file_name="reporte.csv",
    content_bytes="id,valor\n1,100\n".encode("utf-8"),
)
```

2) Descargar y procesar en memoria:

```python
data = sp.download_file(
    base_path="Datos/ADUANAS/Robot/Reportes",
    file_name="reporte.csv",
)
print(len(data), "bytes descargados")
```

---

## Notas y Limitaciones

- El parámetro `context` controla qué sitio de SharePoint se usa.
- Para `mk_dir`, el folder se crea dentro de la carpeta indicada por `base_path`.
- Para `upload_file`/`download_file`, `base_path` debe existir previamente.
- La selección del drive es fija al tercer elemento (`value[2]`). Ajusta el código si tu estructura difiere.

---

## Licencia

MIT

