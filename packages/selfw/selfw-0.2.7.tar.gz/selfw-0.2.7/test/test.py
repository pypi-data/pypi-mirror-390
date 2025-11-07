import SelFw
import time

driver = SelFw.iniciar_chrome(proxy="localhost:8888")
SelFw.abrir('https://www.cualesmiip.com/', driver)
time.sleep(8888)