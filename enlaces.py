from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
from selenium.common.exceptions import NoSuchElementException

def verificar_sesion_iniciada(driver):
    try:
        # Esperamos unos segundos por si hay redirección automática
        #driver.get("https://backoffice.kodland.org/es/courses_1116/")
        time.sleep(2)

        # Intentamos encontrar el enlace de salir (logout)
        driver.find_element(By.XPATH, '//a[contains(@href, "/logout/") and contains(text(), "Salir")]')
        print("✅ Sesión iniciada correctamente.")
        return True
    except NoSuchElementException:
        print("⛔ No se ha iniciado sesión.")
        return False


def crear_enlaces(driver, url):
    driver.get(url)
    time.sleep(3)
    tag = "tr"
    if "groups" in url:
        tag = "div"
        

    student_links = []

    # Buscar todas las filas <tr> que podrían tener enlaces y estado
    filas = driver.find_elements(By.TAG_NAME, tag)
    for fila in filas:
        try:
            # Buscar el enlace
            link = fila.find_element(By.XPATH, './/a[contains(@href, "/students/")]')
            href = link.get_attribute('href')

            if tag == "div":
                icon = fila.find_element(By.CSS_SELECTOR, ".v-chip.status i")
                clase_icono = icon.get_attribute("class")
                if "ri-check-line" in clase_icono:
                    student_links.append(href + "?language=es")
            else:
                if "Inscrito" in fila.text:
                    student_links.append(href)
        except:
            continue

    # Eliminar duplicados
    student_links = list(set(student_links))

    # Guardar en archivo
    with open("e.txt", "w", encoding="utf-8") as archivo:
        for link in student_links:
            archivo.write(f"\"{link}\",\n")

    
