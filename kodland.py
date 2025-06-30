from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time, csv, pyperclip, phonenumbers, pycountry

from phonenumbers import geocoder



def crear_contactos(driver):
    with open('e.txt', 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Limpiar comillas y separar por coma
    urls = [u.strip().replace('"', '') for u in contenido.split(',') if u.strip()]

    contactos = []

    for user_id in urls:
        url = user_id
        driver.get(url)
        time.sleep(3)  # Esperar a que cargue
        
        btn_copiar = driver.find_element(By.CSS_SELECTOR, 'i.ri-lock-password-line')
        btn_copiar.find_element(By.XPATH, '..').click()  # clic en el botón "copiar"
        time.sleep(1)  # Esperar a que se copie al portapapeles
        copiado = pyperclip.paste()
        
        try:
            nombre = driver.find_element(By.CSS_SELECTOR, "h3.childName").text.strip()
        except:
            nombre = "No encontrado"

        try:
            # Buscar el texto "Número de teléfono" y luego su valor
            spans = driver.find_elements(By.CLASS_NAME, "font-weight-medium")
            telefono = "No encontrado"
            for i, span in enumerate(spans):
                
                if "Número de teléfono" in span.text and i != 5:
                    telefono = span.find_element(By.XPATH, "following-sibling::text()")
                    break
        except:
            
            try:
                telefono = span.find_element(By.XPATH, "..").text.split("Número de teléfono:")[-1].strip()
            except:
                telefono = "No encontrado"
        
        pais = obtener_pais(telefono)
        contactos.append([nombre, telefono, copiado, pais])
        
        time.sleep(1)  # Esperar a que se cargue
    driver.quit()
    return contactos

def exportar_contactos(contactos):
    # Exportar a CSV
    with open('contactos_google.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Nombre","Telefono"])  # Encabezados requeridos por Google
        writer.writerows(contactos)

def obtener_pais(numero):
    try:
        parsed = phonenumbers.parse(numero, None)
        codigo_pais = phonenumbers.region_code_for_number(parsed)
        pais = pycountry.countries.get(alpha_2=codigo_pais)
        return pais.name if pais else "Desconocido"
    except Exception as e:
        return f"Error: {e}"

