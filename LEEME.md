"""Interfaz gráfica de Automatización para Kodland

Este módulo proporciona una aplicación de escritorio con interfaz gráfica (Tkinter) que
coordina un scraper basado en Selenium (`KodlandScraper`) para extraer información de
contacto de estudiantes desde un enlace de grupo de Kodland.



Características principales
---------------------------
* **Iniciar** el proceso de scraping en un hilo de fondo para que
  la interfaz no se congele.
* **Actualizaciones en vivo** – los mensajes generados por el scraper aparecen
  inmediatamente en la barra de estado.
* **Lista de contactos en tiempo real** – los nuevos contactos se muestran
  automáticamente en un `ttk.Treeview`.
* **Acciones útiles** – generación de mensajes personalizados con usuario y contraseña de la plataforma Kodland  y exportación de contactos
  en formato CSV compatible con Google.

La clase :class:`SeleniumInterface` contiene todos los elementos gráficos y la lógica
interactiva. Las operaciones específicas de Selenium se delegan a la clase
`KodlandScraper` del módulo `kodland_scraping`, lo que permite una separación clara de responsabilidades.



Uso
---
Instrucciones:

1. **Clonar** el repositorio desde GitHub
Abre la terminal o PowerShell y ejecuta:

git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio(cambia tu repositorio por la carpeta donde se clonó el repositorio)


2. **Crear y activar un entorno virtual**
crea entorno virtual:
python -m venv venv

Activar En Windows:
venv\Scripts\activate

Activar En macOS/Linux:
source venv/bin/activate

3. **Instalar las dependencias necesarias**
Asegúrate de que el archivo requirements.txt esté presente (debe incluir):

selenium>=4.0.0
pyperclip
phonenumbers
pycountry

Luego ejecuta:
pip install -r requirements.txt

4. **Descargar y configurar ChromeDriver**
Verifica la versión de tu Google Chrome:

Escribe chrome://version en la barra del navegador.

Descarga el ChromeDriver correspondiente desde:
https://googlechromelabs.github.io/chrome-for-testing/

Extrae chromedriver.exe y colócalo:

En la carpeta raíz del proyecto, o
en alguna ruta del sistema (C:\Windows\System32 o una carpeta incluida en PATH)

5. **Ejecutar la interfaz**
>>> python kodland interfaz.py

**Consejo**
si se crea un archivo llamado "contraseña.txt"
con nombre de usuario y contraseña del tutor,  separados por comas el programa hace todo automaticamente.
si no creas, ingresa los datos manualmente en el navegador que se abre al iniciar el proceso, ejemplo:

usuario,
contraseña

**Como Funciona**
https://drive.google.com/file/d/1mvVxUANxmKezukOovGB3yJPxCLkivmXf/view?usp=drive_link
"""