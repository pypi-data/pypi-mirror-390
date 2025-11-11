import http.client
import json
import msal
import os
import urllib.parse
import logging
from urllib.parse import quote

SHAREPOINT_SITE = os.getenv('sharepoint_site_name')
SHAREPOINT_SITE_LEGALES = os.getenv('sharepoint_site_name_legales')

class SharePointGraph:
    def __init__(self):
        self.SECRETID = os.getenv('secretId')
        self.APPID = os.getenv('appId')
        self.TENANTID = os.getenv('tenantId')
        self.token = None
        self.site_id = None
        self.drive_id = None
        self.item_id = None

    # ---------- Helpers ----------
    @staticmethod
    def _normalize_path(path: str) -> str:
        """Normaliza rutas tipo Windows a Graph: backslashes→slashes, quita dobles y bordes."""
        if not path:
            return ""
        p = path.replace("\\", "/")
        # colapsar / múltiples
        while '//' in p:
            p = p.replace('//', '/')
        # quitar leading/trailing
        p = p.strip('/')
        return p

    @staticmethod
    def _is_success(status: int) -> bool:
        return 200 <= status < 300

    def _request_json(self, method: str, url_path: str, body: bytes = b"", headers: dict | None = None):
        """Hace request a graph.microsoft.com y devuelve (status, headers, parsed_json | raw_text)."""
        conn = http.client.HTTPSConnection("graph.microsoft.com")
        try:
            conn.request(method, url_path, body=body, headers=headers or {})
            resp = conn.getresponse()
            raw = resp.read()
            text = raw.decode("utf-8", errors="replace")
            try:
                data = json.loads(text) if text else {}
            except json.JSONDecodeError:
                data = {"_raw": text}
            return resp.status, dict(resp.getheaders()), data
        finally:
            conn.close()

    # ---------- Auth ----------
    def _az_auth(self, secret_id, app_id, tenant_id):
        self.SECRETID = secret_id
        self.APPID = app_id
        self.TENANTID = tenant_id

    def get_token(self):
        try:
            authority = f'https://login.microsoftonline.com/{self.TENANTID}'
            app = msal.ConfidentialClientApplication(
                self.APPID, authority=authority, client_credential=self.SECRETID)
            token_resp = app.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])
            if not token_resp or 'access_token' not in token_resp:
                raise RuntimeError(f"token_resp sin access_token: {token_resp}")
            self.token = token_resp['access_token']
            logging.info(f"🔐 Access Token: {self.token}")
        except Exception as e:
            logging.error(f"❌ Error al obetener Token: {e}")
            raise ValueError(f"❌ Error al obetener Token: {e}")

    # ---------- Site & Drive ----------
    def get_site_id(self, context="cw"):
        try:
            site = SHAREPOINT_SITE if context in ('cw', 'cw_dc') else SHAREPOINT_SITE_LEGALES
            headers = {'Authorization': f'Bearer {self.token}'}
            path = f"/v1.0/sites/customswatch.sharepoint.com:/sites/{quote(site)}"
            status, _, data = self._request_json("GET", path, headers=headers)

            if not self._is_success(status):
                raise RuntimeError(f"GET {path} -> {status} {data}")

            # Ej: "id": "customswatch.sharepoint.com,7ac388a7-...,xxxxxxxxx"
            site_id_raw = data.get("id")
            if not site_id_raw or ',' not in site_id_raw:
                raise RuntimeError(f"Respuesta site sin id esperado: {data}")
            self.site_id = site_id_raw.split(',')[1]
            logging.info(f"🔐 Site ID ({site}): {self.site_id}")
        except Exception as e:
            logging.error(f"❌ Error al obetener Site ID: {e}")
            raise ValueError(f"❌ Error al obetener Site ID: {e}")

    def get_drive_id(self, context="cw"):
        try:
            site = SHAREPOINT_SITE if context == 'cw' or context == 'cw_dc' else SHAREPOINT_SITE_LEGALES
            conn = http.client.HTTPSConnection("graph.microsoft.com")
            headers = {'Authorization': f'Bearer {self.token}'}
            conn.request("GET", f"/v1.0/sites/{self.site_id}/drives", '', headers)
            data = json.loads(conn.getresponse().read().decode("utf-8"))
            self.drive_id = data["value"][0]['id'] if context == 'cw_dc' else data["value"][2]['id']
            logging.info(f"🔐 Drive ID ({site}): {self.drive_id}")
        except Exception as e:
            logging.error(f"❌ Error al obetener Drive ID: {e}")
            raise ValueError(f"❌ Error al obetener Drive ID: {e}")


    # ---------- Rutas / Items ----------
    def get_item_id(self, base_path, context="cw"):
        """
        Resuelve el item_id del directorio 'base_path'.
        Si base_path es 'A/B/C', busca 'C' listando los hijos de 'A/B'.
        Si base_path no tiene '/', busca 'base_path' en la raíz.
        """
        try:
            site = SHAREPOINT_SITE if context in ('cw', 'cw_dc') else SHAREPOINT_SITE_LEGALES
            base_path = self._normalize_path(base_path)

            headers = {'Authorization': f'Bearer {self.token}'}

            # Separar padre e hijo
            if '/' in base_path:
                parent = base_path.rsplit('/', 1)[0]    # A/B
                leaf = base_path.rsplit('/', 1)[1]      # C
                parent_enc = quote(parent)
                list_path = f"/v1.0/drives/{self.drive_id}/root:/{parent_enc}:/children"
            else:
                # listar raíz
                leaf = base_path
                list_path = f"/v1.0/drives/{self.drive_id}/root/children"

            status, _, data = self._request_json("GET", list_path, headers=headers)
            if not self._is_success(status) or 'value' not in data:
                raise RuntimeError(f"GET {list_path} -> {status} {data}")

            # Buscar folder exacto por name (case-insensitive, trimmed)
            leaf_norm = (leaf or "").strip().lower()
            matches = [
                it for it in data['value']
                if it.get('name', '').strip().lower() == leaf_norm
            ]
            if not matches:
                raise RuntimeError(f"No se encontró carpeta '{leaf}' en '{base_path}'. Data: {data}")

            self.item_id = matches[0].get('id')
            if not self.item_id:
                raise RuntimeError(f"Item sin id válido: {matches[0]}")

            logging.info(f"🔐 Item ID ({site}/{base_path}): {self.item_id}")
        except Exception as e:
            logging.error(f"❌ Error al obetener Item ID: {e}")
            raise ValueError(f"❌ Error al obetener Item ID: {e}")

    def _auth(self, base_path, context="cw"):
        try:
            self.get_token()
            self.get_site_id(context)
            self.get_drive_id(context)
            self.get_item_id(base_path, context)
        except Exception as e:
            logging.error(f"❌ Error en autenticación Graph: {e}")
            raise ValueError(f"❌ Error en autenticación Graph: {e}")

    # ---------- Operaciones de carpetas / archivos ----------
    def check_dir(self, folder_name, base_path, context="cw"):
        try:
            if not all([self.token, self.drive_id]):
                self._auth(base_path, context)

            base_path = self._normalize_path(base_path)
            headers = {'Authorization': f'Bearer {self.token}'}
            url = f"/v1.0/drives/{self.drive_id}/root:/{quote(base_path)}:/children"

            while url:
                status, _, data = self._request_json("GET", url, headers=headers)
                if not self._is_success(status):
                    raise RuntimeError(f"GET {url} -> {status} {data}")

                for item in data.get('value', []):
                    if item['name'].strip().lower() == folder_name.strip().lower():
                        logging.info(f"✅ La carpeta '{folder_name}' ya existe.")
                        return True

                # paginación
                url = None
                next_link = data.get('@odata.nextLink')
                if next_link:
                    url = next_link.replace("https://graph.microsoft.com", "")

            logging.info(f"⚠️ La carpeta '{folder_name}' NO existe.")
            return False
        except Exception as e:
            logging.error(f"❌ Error en en la corroboracion de carpeta con Graph: {e}")
            raise ValueError(f"❌ Error en en la corroboracion de carpeta con Graph: {e}")

    def mk_dir(self, folder_name, base_path, context="cw"):
        try:
            if not all([self.token, self.drive_id, self.item_id]):
                self._auth(base_path, context)

            payload = json.dumps({
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename"
            }).encode("utf-8")
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }

            path = f"/v1.0/drives/{self.drive_id}/items/{self.item_id}/children"
            status, _, data = self._request_json("POST", path, body=payload, headers=headers)

            if not self._is_success(status):
                raise RuntimeError(f"POST {path} -> {status} {data}")

            logging.info(f"📁 Carpeta creada: {data.get('name')}")
            return data.get("name")
        except Exception as e:
            logging.error(f"❌ Error creando carpeta: {e}")
            raise ValueError(f"❌ Error creando carpeta: {e}")

    def download_file(self, base_path, file_name, context="cw"):
        try:
            if not all([self.token, self.drive_id]):
                self._auth(base_path, context)

            base_path = self._normalize_path(base_path)
            headers = { "Authorization": f"Bearer {self.token}" }

            route = (
                f"/v1.0/drives/{self.drive_id}/root:/"
                f"{quote(base_path)}/{quote(file_name)}:/content"
            )
            status, h, data = self._request_json("GET", route, headers=headers)

            # Handling redirect 302 (Graph suele redirigir al blob real)
            if status == 302:
                location = h.get("Location")
                if not location:
                    raise RuntimeError(f"302 sin Location: headers={h}")
                host = location.split("/")[2]
                path = "/" + "/".join(location.split("/")[3:])
                conn2 = http.client.HTTPSConnection(host)
                conn2.request("GET", path)
                resp2 = conn2.getresponse()
                raw = resp2.read()
                conn2.close()
                if self._is_success(resp2.status):
                    return raw
                raise RuntimeError(f"Error descargando tras redirect: {resp2.status} {raw.decode('utf-8', errors='replace')}")

            if self._is_success(status):
                # _request_json parsea por defecto; para contenido binario usamos el redireccionamiento anterior.
                # Si llega acá con 200 sin redirect es probable que sea un JSON con un link (poco común).
                if isinstance(data, dict):
                    # Si devuelve JSON inesperado, informar claramente
                    raise RuntimeError(f"Respuesta JSON inesperada al descargar: {data}")
                return data  # por compatibilidad, aunque en práctica 302 es el camino normal

            raise RuntimeError(f"❌ Error al descargar archivo '{file_name}': {status} {data}")
        except Exception as e:
            logging.error(f"❌ Error en download_file: {e}")
            raise ValueError(f"❌ Error en download_file: {e}")

    def upload_file(self, base_path, file_name, content_bytes, context='cw'):
        try:
            if not all([self.token, self.drive_id]):
                self._auth(base_path, context)

            base_path = self._normalize_path(base_path)
            endpoint = f"/v1.0/drives/{self.drive_id}/root:/{quote(base_path + '/' + file_name)}:/content"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/octet-stream"
            }

            conn = http.client.HTTPSConnection("graph.microsoft.com")
            conn.request("PUT", endpoint, body=content_bytes, headers=headers)
            resp = conn.getresponse()
            body = resp.read().decode("utf-8", errors="replace")
            conn.close()

            if self._is_success(resp.status):
                logging.info(f"✅ Archivo '{file_name}' subido correctamente.")
            else:
                raise ValueError(f"❌ Error subiendo '{file_name}': {resp.status} {body}")
        except Exception as e:
            logging.error(f"❌ Error en upload_file: {e}")
            raise ValueError(f"❌ Error subiendo archivo '{file_name}': {e}")

    def del_file(self, filename, base_path, context="cw"):
        try:
            if not all([self.token, self.drive_id]):
                self._auth(base_path, context)

            base_path = self._normalize_path(base_path)
            deleted_files = []
            headers = {'Authorization': f'Bearer {self.token}'}

            route_api = f"/v1.0/drives/{self.drive_id}/root:/{quote(base_path)}:/children"

            while route_api:
                status, _, data_api = self._request_json("GET", route_api, headers=headers)
                if not self._is_success(status):
                    raise RuntimeError(f"GET {route_api} -> {status} {data_api}")

                for api in data_api.get('value', []):
                    dir_name = api.get('name', '')
                    dir_encoded = urllib.parse.quote(dir_name)

                    route = f"/v1.0/drives/{self.drive_id}/root:/{quote(base_path)}/{dir_encoded}:/children"
                    while route:
                        s2, _, data = self._request_json("GET", route, headers=headers)
                        if not self._is_success(s2):
                            raise RuntimeError(f"GET {route} -> {s2} {data}")

                        for f in data.get('value', []):
                            if filename in f.get('name', ''):
                                del_path = f"/v1.0/drives/{self.drive_id}/items/{f['id']}"
                                s3, _, _ = self._request_json("DELETE", del_path, headers=headers)
                                if self._is_success(s3):
                                    logging.info(f"🗑️ Archivo eliminado: {f['name']}")
                                    deleted_files.append(f['name'])

                        # paginación
                        next_link = data.get('@odata.nextLink')
                        route = next_link.replace("https://graph.microsoft.com", "") if next_link else None

                # paginación nivel superior
                next_link_api = data_api.get('@odata.nextLink')
                route_api = next_link_api.replace("https://graph.microsoft.com", "") if next_link_api else None

            return deleted_files
        except Exception as e:
            logging.error(f"❌ Error al eliminar archivos: {e}")
            raise ValueError(f"❌ Error al eliminar archivos: {e}")

    