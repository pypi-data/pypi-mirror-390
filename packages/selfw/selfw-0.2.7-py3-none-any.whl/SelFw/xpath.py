from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import JavascriptException, TimeoutException, ElementNotInteractableException, NoSuchElementException
import time


def existe(xpath, driver, timeout=5):
    """Verifica si el elemento existe y es visible"""
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return True
    except TimeoutException:
        return False


def click(xpath, driver, timeout=5):
    """Hace click cuando el elemento es clickeable"""
    try:
        if existe(xpath, driver) is False:
            print(f"No encuentro: {xpath}")
        elem = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
        elem.click()
        return True
    except (TimeoutException, ElementNotInteractableException) as e:
        print(e)
        # fallback al click JS
        try:
            elem = driver.find_element(By.XPATH, xpath)
            driver.execute_script("arguments[0].click();", elem)
            return True
        except Exception as e2:
            print(f"[click] Error en {xpath}: {e2}")
            return False


def send_keys(xpath, valor, driver, timeout=5):
    """Envía texto a un campo visible y habilitado"""
    try:
        if valor is None:
            print(f"[send_keys] Valor None recibido para {xpath}")
            return False
        if existe(xpath, driver) is False:
            print(f"No encuentro: {xpath}")
        elem = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
        elem.clear()
        elem.send_keys(valor)
        return True
    except (TimeoutException, ElementNotInteractableException):
        # fallback con JavaScript
        try:
            elem = driver.find_element(By.XPATH, xpath)
            driver.execute_script("""
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
                arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
            """, elem, valor)
            return True
        except Exception as e2:
            print(f"[send_keys] Error en {xpath}: {e2}")
            return False


def select(xpath, buscar, driver, attr="value", timeout=5):
    """Selecciona una opción de un <select>"""
    try:
        if existe(xpath, driver) is False:
            print(f"No encuentro: {xpath}")
        select_element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_element)
        sel = Select(select_element)
        buscar = str(buscar)
        if attr == "value":
            sel.select_by_value(buscar)
        elif attr == "text":
            sel.select_by_visible_text(buscar)
        else:
            for option in sel.options:
                if option.get_attribute(attr) == buscar:
                    option.click()
                    break
            else:
                raise ValueError(f"No se encontró opción con {attr}='{buscar}'")
        return True
    except Exception as e:
        print(f"[select] Error en {xpath}: {e}")
        return False



def force_select_combobox(input_xpath, option_text, driver, timeout=5):
    try:
        wait = WebDriverWait(driver, timeout)

        # 1️⃣ Clic en el input para abrir el menú
        input_elem = wait.until(EC.element_to_be_clickable((By.XPATH, input_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_elem)
        input_elem.click()

        # 2️⃣ Esperar que aparezca la opción
        option_xpath = f"//li[@role='option' and normalize-space(text())='{option_text}']"
        option_elem = wait.until(EC.presence_of_element_located((By.XPATH, option_xpath)))

        # 3️⃣ Forzar clic vía JavaScript
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_elem)
        driver.execute_script("arguments[0].click();", option_elem)

        print(f"✅ Seleccionado: {option_text}")
        return True

    except Exception as e:
        print(f"❌ Error forzando selección de '{option_text}': {e}")
        return False



def clear(xpath, driver):
    campo = driver.find_element(By.XPATH, xpath)
    campo.clear()

def quitar_disable(xpath, driver, timeout=5):
    """
    Elimina atributos que impiden la edición de un elemento localizado por XPath.
    Intenta quitar 'readonly' y 'disabled' y además fuerza element.readOnly = false.

    :param xpath: XPath del elemento (ejemplo: "//input[@id='fecha']")
    :param driver: instancia activa de Selenium WebDriver
    :param timeout: segundos a esperar por el elemento (default 10)
    :return: True si se realizó algún cambio, False si no se encontró/el cambio falló
    """
    try:
        # Espera a que el elemento esté presente
        elemento = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

        # Ejecuta JS para quitar ambos atributos y forzar readOnly = false
        js = (
            "if (arguments[0]) {"
            "  arguments[0].removeAttribute('readonly');"
            "  arguments[0].removeAttribute('disabled');"
            "  try { arguments[0].readOnly = false; } catch(e) {};"
            "  return true;"
            "}"
            "return false;"
        )
        result = driver.execute_script(js, elemento)
        time.sleep(1)
        elemento.click()
        return bool(result)

    except TimeoutException:
        print(f"[Advertencia] No se encontró el elemento con XPath (timeout {timeout}s): {xpath}")
        return False
    except NoSuchElementException:
        print(f"[Advertencia] No se encontró el elemento con XPath: {xpath}")
        return False
    except JavascriptException as e:
        print(f"[Error] Error al ejecutar JS para eliminar atributos: {e}")
        return False
    except Exception as e:
        # captura cualquier otra excepción inesperada
        print(f"[Error inesperado] {e}")
        return False
    

def agregar_clase_valid(driver, xpath=None, xpaths=None, timeout=5):
    """
    Añade la clase 'valid' a uno o varios elementos localizados por XPath sin eliminar otras clases.
    """
    # Validar entrada
    if not xpaths and not xpath:
        print("[Error] agregar_clase_valid: No se proporcionó ni 'xpath' ni 'xpaths'.")
        return 0  # <- evita el crash

    # Normalizar la lista de XPaths
    if xpaths is None:
        xpaths = [xpath]

    # Asegurar que xpaths es realmente iterable
    if not isinstance(xpaths, (list, tuple)):
        print(f"[Error] agregar_clase_valid: 'xpaths' no es iterable ({type(xpaths)}).")
        return 0

    modificados = 0
    js = "if (arguments[0]) { arguments[0].classList.add('valid'); return true; } return false;"

    for xp in xpaths:
        try:
            elemento = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xp))
            )
            result = driver.execute_script(js, elemento)
            if result:
                modificados += 1
        except TimeoutException:
            print(f"[Advertencia] No se encontró el elemento con XPath (timeout {timeout}s): {xp}")
        except JavascriptException as e:
            print(f"[Error JS en {xp}] {e}")
        except Exception as e:
            print(f"[Error inesperado en {xp}] {type(e).__name__}: {e}")

    return modificados

