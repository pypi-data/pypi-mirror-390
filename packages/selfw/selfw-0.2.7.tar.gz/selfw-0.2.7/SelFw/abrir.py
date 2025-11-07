from selenium.common.exceptions import WebDriverException


def abrir(url, driver):
    try:
        driver.get(f'{url}')
    except WebDriverException as e:
        pass
    except Exception as e:
        pass