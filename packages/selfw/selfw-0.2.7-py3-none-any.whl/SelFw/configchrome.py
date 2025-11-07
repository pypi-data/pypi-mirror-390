# from seleniumwire import webdriver
# from selenium import webdriver as selenium_normal
# from selenium.webdriver.chrome.options import Options
# import os

# def iniciar_chrome(
#     modo="normal",
#     proxy=None,
#     headless=False,
#     usar_seleniumwire=True,
#     perfil=None
# ):
#     """
#     Inicia una sesión de Chrome flexible con soporte para perfiles, headless y proxy (sin autenticación).

#     :param modo: 'normal', 'extension' o 'limpio'
#     :param proxy: str con proxy (ej: 'ip:puerto')
#     :param headless: bool para ejecutar sin interfaz visible
#     :param usar_seleniumwire: bool para usar seleniumwire o webdriver normal
#     :param perfil: ruta al perfil de Chrome (solo si modo='extension')
#     :return: driver listo para usar
#     """

#     chrome_options = Options()
#     chrome_options.add_argument("--start-maximized")
#     chrome_options.add_argument("--disable-notifications")
#     chrome_options.add_argument("--ignore-certificate-errors")
#     chrome_options.add_argument("--disable-infobars")
#     chrome_options.add_argument("--log-level=3")
#     chrome_options.add_argument("--remote-debugging-port=0")
#     chrome_options.add_argument('--blink-settings=imagesEnabled=false')
#     chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
#     chrome_options.add_argument(
#         '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
#     )

#     if headless:
#         chrome_options.add_argument("--headless=new")

#     # --- MODO EXTENSIÓN ---
#     if modo == "extension":
#         perfil_path = perfil or r"C:\SeleniumProfile"
#         os.makedirs(perfil_path, exist_ok=True)
#         chrome_options.add_argument(fr"user-data-dir={os.path.abspath(perfil_path)}")

#     # --- MODO LIMPIO ---
#     elif modo == "limpio":
#         chrome_options.add_argument("--incognito")
#         chrome_options.add_argument("--disable-extensions")

#     # --- CONFIGURAR PROXY SIN AUTENTICACIÓN ---
#     seleniumwire_options = {}
#     if proxy:
#         # proxy es un string tipo "ip:puerto"
#         if usar_seleniumwire:
#             seleniumwire_options = {
#                 "proxy": {
#                     "http": f"http://{proxy}",
#                     "https": f"http://{proxy}",
#                     "no_proxy": "localhost,127.0.0.1"
#                 },
#                 "verify_ssl": False
#             }
#         else:
#             chrome_options.add_argument(f"--proxy-server=http://{proxy}")

#     # --- CREAR DRIVER ---
#     if usar_seleniumwire:
#         driver = webdriver.Chrome(options=chrome_options, seleniumwire_options=seleniumwire_options)
#     else:
#         driver = selenium_normal.Chrome(options=chrome_options)

#     return driver

import os
import re
import json
from seleniumwire import webdriver as sw_webdriver
from selenium import webdriver as selenium_normal
from selenium.webdriver.chrome.options import Options

# -----------------------
# Helpers para patrones
# -----------------------
def _match_pattern(url: str, pattern: str) -> bool:
    """
    Si pattern empieza con 're:' lo tratamos como regex; si no, hacemos búsqueda substring (case-insensitive).
    """
    if not url:
        return False
    url_l = url.lower()
    if pattern.startswith("re:"):
        try:
            return bool(re.search(pattern[3:], url, flags=re.IGNORECASE))
        except re.error:
            return False
    else:
        return pattern.lower() in url_l

# -----------------------
# Función principal
# -----------------------
def iniciar_chrome(
    modo="normal",
    proxy=None,
    headless=False,
    usar_seleniumwire=True,
    perfil=None,
    api_rules=None,  # dict: { pattern_str: {"action":"abort"|"mock"|"allow", "mock_status":200, "mock_body": b'...', "mock_headers":{}} }
):
    """
    Inicia Chrome. Cuando usar_seleniumwire=True puedes pasar api_rules para controlar endpoints dinámicamente.

    api_rules example:
    {
        "/api/loqsea": {"action":"abort"},
        "/api/mockme": {"action":"mock", "mock_status":200, "mock_body": b'{"message":"no sabes"}', "mock_headers":{"Content-Type":"application/json"} },
        "re:.*\\/v1\\/private\\/.*": {"action":"abort"}
    }
    """

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--disable-http2')
    chrome_options.add_argument('--disable-quic')
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--remote-debugging-port=0")
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    )

    if headless:
        chrome_options.add_argument("--headless=new")

    # MODO EXTENSIÓN
    if modo == "extension":
        perfil_path = perfil or r"C:\SeleniumProfile"
        os.makedirs(perfil_path, exist_ok=True)
        chrome_options.add_argument(fr"user-data-dir={os.path.abspath(perfil_path)}")
    elif modo == "limpio":
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-extensions")

    # Configurar proxy
    seleniumwire_options = {}
    if proxy:
        if usar_seleniumwire:
            seleniumwire_options = {
                "proxy": {
                    "http": f"http://{proxy}",
                    "https": f"http://{proxy}",
                    "no_proxy": "localhost,127.0.0.1"
                },
                "verify_ssl": False
            }
        else:
            chrome_options.add_argument(f"--proxy-server=http://{proxy}")

    # Inicializar driver
    if usar_seleniumwire:
        driver = sw_webdriver.Chrome(options=chrome_options, seleniumwire_options=seleniumwire_options)
        # estructura interna de reglas (pattern -> rule dict)
        driver._api_rules = api_rules.copy() if api_rules else {}

        # Request interceptor: se usa para abortar o para crear responses mock antes de ir a red.
        def _request_interceptor(request):
            try:
                url = request.url or ""
                for pattern, rule in list(driver._api_rules.items()):
                    if _match_pattern(url, pattern):
                        action = rule.get("action", "abort")
                        if action == "abort":
                            # cancela la petición (el navegador verá un error de red)
                            request.abort()
                            return
                        elif action == "mock":
                            # si queremos devolver mock SIN tocar la red, usamos create_response
                            status = int(rule.get("mock_status", 200))
                            body = rule.get("mock_body", b'')  # bytes
                            headers = rule.get("mock_headers", {"Content-Type": "application/json"})
                            # Selenium Wire permite crear una respuesta directamente:
                            request.create_response(
                                status_code=status,
                                headers=headers,
                                body=body
                            )
                            return
                        elif action == "allow":
                            # No hacemos nada; la request sigue
                            return
            except Exception:
                # no queremos que cualquier excepción rompa el flujo
                pass

        # Response interceptor: útil si decidimos modificar la respuesta REAL que vino de la red
        def _response_interceptor(request, response):
            try:
                url = request.url or ""
                for pattern, rule in list(driver._api_rules.items()):
                    if _match_pattern(url, pattern):
                        action = rule.get("action", "abort")
                        if action == "mock" and rule.get("mock_replace_real_response", False):
                            # Se reemplaza la respuesta real por el mock_body
                            response.status_code = int(rule.get("mock_status", 200))
                            # selenium-wire Response tiene atributos .body y .headers en muchas versiones
                            response.body = rule.get("mock_body", b'')
                            # actualizar cabeceras si vienen
                            for k, v in rule.get("mock_headers", {}).items():
                                response.headers[k] = v
                            return response
                        # si action==abort o action==mock (create_response ya lo devolvió en request), no hacemos nada
            except Exception:
                pass
            return response

        driver.request_interceptor = _request_interceptor
        driver.response_interceptor = _response_interceptor

        # Métodos utility para modificar reglas en caliente
        def add_api_rule(pattern, action="abort", mock_status=200, mock_body=None, mock_headers=None, mock_replace_real_response=False):
            """
            Añade/actualiza una regla.
            - pattern: substring o 're:<regex>'
            - action: 'abort' | 'mock' | 'allow'
            - mock_body: bytes (p. ej. b'{"message":"no sabes"}')
            - mock_replace_real_response: si True, se reemplaza la respuesta real en response_interceptor (requiere que la request no se haya creado con create_response)
            """
            rule = {"action": action}
            if mock_body is not None:
                rule["mock_body"] = mock_body
            rule["mock_status"] = int(mock_status)
            rule["mock_headers"] = mock_headers or {"Content-Type": "application/json"}
            rule["mock_replace_real_response"] = bool(mock_replace_real_response)
            driver._api_rules[pattern] = rule

        def remove_api_rule(pattern):
            driver._api_rules.pop(pattern, None)

        def list_api_rules():
            return dict(driver._api_rules)

        # Attach helpers al objeto driver
        driver.add_api_rule = add_api_rule
        driver.remove_api_rule = remove_api_rule
        driver.list_api_rules = list_api_rules

    else:
        driver = selenium_normal.Chrome(options=chrome_options)

    return driver
