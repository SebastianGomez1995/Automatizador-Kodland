"""Scraper para Kodland usando Selenium

Este módulo define la clase `KodlandScraper`, que automatiza la extracción de información de contacto
(y credenciales) de estudiantes desde la plataforma Kodland usando Selenium.

El scraper es invocado desde una interfaz gráfica (`SeleniumInterface`) y se ejecuta en un hilo de fondo.
Los resultados son devueltos a través de `queue.Queue`, lo que permite comunicación fluida y segura entre
el hilo del scraper y la interfaz principal.

"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time, csv, pyperclip, phonenumbers, pycountry
from selenium.common.exceptions import NoSuchElementException

class KodlandScraper:
    def __init__(self, url, mensaje, contacto):
        """
        Inicializa el scraper con los parámetros necesarios.

        Parámetros:
        - url: Enlace del grupo/clase de Kodland
        - mensaje: cola (Queue) para enviar mensajes de estado a la interfaz
        - contacto: cola (Queue) para enviar contactos detectados a la interfaz
        """
        self.driver = None
        self.driver_path = "chromedriver.exe"
        self.url = url
        self.contactos = []
        self.mensaje_ = mensaje
        self.contacto_mensaje = contacto

    def log(self, mensaje):
        """Envía un mensaje a la cola de estado para mostrarlo en la interfaz."""
        self.mensaje_.put(mensaje)

    def verificar_sesion_iniciada(self):
        """
        Verifica si el usuario ya ha iniciado sesión correctamente.
        Retorna True si encuentra el botón de "Salir", False en caso contrario.
        """
        try:
            time.sleep(2)
            self.driver.find_element(By.XPATH, '//a[contains(@href, "/logout/") and contains(text(), "Salir")]')
            print("✅ Sesión iniciada correctamente.")
            return True
        except NoSuchElementException:
            print("⛔ No se ha iniciado sesión.")
            return False

    def iniciarProceso(self):
        """
        Método principal que ejecuta el proceso completo:
        - Abre navegador
        - Inicia sesión
        - Extrae enlaces
        - Obtiene contactos
        - Cierra el navegador
        """
        self.log("Inicia sesión en el navegador")
        self.iniciar_navegador()
        while True:
            time.sleep(5)
            if self.verificar_sesion_iniciada():
                break
        self.log("Creando enlaces, espere un momento")
        self.crear_enlaces()
        self.contactos = self.crear_contactos()
        
        self.driver.quit()

    def iniciar_navegador(self):
        """
        Configura el navegador Chrome y accede a la página de login.
        Llena el formulario de usuario y contraseña automáticamente.
        """
        options = Options()
        options.add_argument("--start-maximized")
        
        
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://backoffice.kodland.org/es/login/")
        
        with open('contraseña.txt', 'r', encoding='utf-8') as f:
            contenido = f.read()
        if contenido != "":
            data = [u.strip().replace('"', '') for u in contenido.split(',') if u.strip()]
            self.driver.find_element(By.ID, "id_username").send_keys(data[0])
            self.driver.find_element(By.ID, "id_password").send_keys(data[1])
            self.driver.find_element(By.CLASS_NAME, "login-button").click()

    def crear_enlaces(self):
        """
        Recorre la tabla/lista de estudiantes en la plataforma Kodland
        y guarda enlaces individuales a cada perfil de estudiante.
        """
        self.driver.get(self.url)
        time.sleep(3)
        tag = "tr" if "groups" not in self.url else "div"
        student_links = []

        filas = self.driver.find_elements(By.TAG_NAME, tag)
        for fila in filas:
            try:
                link = fila.find_element(By.XPATH, './/a[contains(@href, "/students/")]')
                href = link.get_attribute('href')

                if tag == "div":
                    icon = fila.find_element(By.CSS_SELECTOR, ".v-chip.status i")
                    if "ri-check-line" in icon.get_attribute("class"):
                        student_links.append(href + "?language=es")
                else:
                    if "Inscrito" in fila.text:
                        student_links.append(href)
            except:
                continue

        student_links = list(set(student_links))  # eliminar duplicados

        with open("student_links.txt", "w", encoding="utf-8") as archivo:
            for link in student_links:
                archivo.write(f'"{link}",\n')

    def crear_contactos(self):
        """
        Visita cada enlace de estudiante guardado y extrae:
        - Nombre del estudiante
        - Teléfono
        - Texto copiado (usuario y contraseña)
        - País (detectado por número de teléfono)

        Devuelve una lista de listas [[nombre, telefono, credenciales, pais], ...]
        """
        with open('student_links.txt', 'r', encoding='utf-8') as f:
            contenido = f.read()

        urls = [u.strip().replace('"', '') for u in contenido.split(',') if u.strip()]
        contactos = []

        for user_id in urls:
            self.log(f"Procesando Estudiante {urls.index(user_id)+1}/{len(urls)}")
            self.driver.get(user_id)
            time.sleep(3)

            self.driver.find_element(By.CSS_SELECTOR, 'i.ri-lock-password-line').find_element(By.XPATH, '..').click()
            time.sleep(1)
            copiado = pyperclip.paste()

            try:
                nombre = self.driver.find_element(By.CSS_SELECTOR, "h3.childName").text.strip()
            except:
                nombre = "No encontrado"

            telefono = "No encontrado"
            try:
                spans = self.driver.find_elements(By.CLASS_NAME, "font-weight-medium")
                for i, span in enumerate(spans):
                    if "Número de teléfono" in span.text and i != 5:
                        telefono = span.find_element(By.XPATH, "..").text.split(":")[-1].strip()
                        break
            except:
                telefono = "No encontrado"

            pais = self.obtener_pais(telefono)
            self.contacto_mensaje.put((nombre, telefono, pais))
            contactos.append([nombre, telefono, copiado, pais])
            time.sleep(1)
        self.log(f"Estudiantes: {len(contactos)}/{len(contactos)}")
        return contactos

    def exportar_contactos(self, contactos):
        """
        Exporta los contactos al formato CSV de Google Contacts.
        Cada fila contiene: Nombre, Teléfono
        """
        with open('contactos_google.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Nombre", "Telefono"])
            writer.writerows(contactos)

    def obtener_pais(self, numero):
        """
        Usa la librería phonenumbers para detectar el país a partir del número.
        Devuelve el nombre del país, o "Desconocido" si no se puede determinar.
        """
        try:
            parsed = phonenumbers.parse(numero, None)
            codigo_pais = phonenumbers.region_code_for_number(parsed)
            pais = pycountry.countries.get(alpha_2=codigo_pais)
            return pais.name if pais else "Desconocido"
        except Exception as e:
            return f"Error: {e}"
