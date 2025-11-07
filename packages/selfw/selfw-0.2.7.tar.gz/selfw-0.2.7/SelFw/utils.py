from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
import time

def esperar(tiempo):
    if tiempo > 99999999:
        tiempo = 99999999
    time.sleep(tiempo)


def check_url(url_actual, url_objetivo):
    return url_actual == url_objetivo


def scroll(valor, driver):
    driver.execute_script(f"window.scrollBy(0, {valor});")


def get_text(xpath, driver):
    """Devuelve el texto del elemento si existe, o None si no se encuentra."""
    try:
        elemento = driver.find_element(By.XPATH, xpath)
        return elemento.text
    except NoSuchElementException:
        return None


def establecer_valor_input(xpath, valor, driver):
    elemento = driver.find_element(By.XPATH, xpath)
    driver.execute_script("arguments[0].value = arguments[1];", elemento, str(valor))


def establecer_fecha(xpath, valor, driver):
    """
    Establece un valor en un input readonly (ej. date/datetime).
    
    :param driver: instancia de Selenium WebDriver
    :param xpath: string con el XPath del input
    :param valor: string con el valor de fecha que quieres asignar (ej. '2025-09-20')
    """
    elemento = driver.find_element(By.XPATH, xpath)
    driver.execute_script("arguments[0].removeAttribute('readonly')", elemento)  # quita readonly
    driver.execute_script("arguments[0].value = arguments[1];", elemento, valor)  # asigna valor
    # Opcional: disparar evento 'change' para que la web lo detecte
    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", elemento)


