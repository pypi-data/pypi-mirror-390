from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, JavascriptException


def quitar_alarm(driver):
    """
    Desactiva las alertas (window.alert) en la página actual.
    Útil para evitar que alertas bloqueen la automatización.
    """
    script = """
        window.alert = function() {
            console.log("Alerta bloqueada por Selenium.");
        };
        window.confirm = function() {
            console.log("Confirm bloqueado por Selenium.");
            return true;
        };
        window.prompt = function() {
            console.log("Prompt bloqueado por Selenium.");
            return null;
        };
    """
    try:
        driver.execute_script(script)
    except JavascriptException as e:
        print(f"[Error] No se pudo ejecutar el script para quitar alertas: {e}")


def quitar_readonly(xpath, driver):
    """
    Elimina el atributo 'readonly' de un elemento localizado por XPath.

    :param xpath: XPath del elemento (ejemplo: "//input[@id='fecha']")
    :param driver: instancia activa de Selenium WebDriver
    """
    try:
        elemento = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].removeAttribute('readonly')", elemento)
    except NoSuchElementException:
        print(f"[Advertencia] No se encontró el elemento con XPath: {xpath}")
    except JavascriptException as e:
        print(f"[Error] No se pudo eliminar el atributo 'readonly': {e}")
