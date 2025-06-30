import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from selenium.webdriver.common.by import By
import threading
from kodland import crear_contactos, exportar_contactos
from enlaces import crear_enlaces,verificar_sesion_iniciada
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import time

class SeleniumInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatizador Kodland")
        self.root.geometry("800x500")
        self.root.resizable(True, True)
        
        # Variables
        self.proceso_activo = 0
        self.selenium_thread = None
        self.driver = None
        self.count = 0
        self.contactos = []
        
        self.crear_interfaz()
        
    def iniciar_navegador(self):
        options = Options()
        options.add_argument("--start-maximized")  # Puedes añadir --headless si no quieres ver el navegador
        usuario = "sgomez5977"
        contrasena = "xxFMbbDDBx"
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://backoffice.kodland.org/es/login/")
        
        # Escribir el usuario y contraseña
        self.driver.find_element(By.ID, "id_username").send_keys(usuario)
        self.driver.find_element(By.ID, "id_password").send_keys(contrasena)

        # (Opcional) Simular clic en "Iniciar sesión"
        self.driver.find_element(By.CLASS_NAME, "login-button").click()

        # Esperar un poco antes de cerrar
        #time.sleep(5)
        
    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar el grid para que se expanda
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Input para enlace
        ttk.Label(main_frame, text="Enlace del grupo:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_enlace = ttk.Entry(main_frame, width=50)
        self.entry_enlace.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Input para nombre
        ttk.Label(main_frame, text="Etiqueta(opcional):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_nombre = ttk.Entry(main_frame, width=50)
        self.entry_nombre.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Botón Iniciar Proceso
        self.btn_iniciar = ttk.Button(
            button_frame, 
            text="Iniciar Proceso", 
            command=self.iniciar_proceso,
            style="Accent.TButton"
        )
        self.btn_iniciar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón Continuar
        self.btn_continuar = ttk.Button(
            button_frame, 
            text="Continuar", 
            command=self.continuar_proceso,
            state="disabled"
        )
        self.btn_continuar.pack(side=tk.LEFT)
        
        # Botón Detener
        self.btn_detener = ttk.Button(
            button_frame, 
            text="Detener", 
            command=self.detener_proceso,
            state="disabled"
        )
        self.btn_detener.pack(side=tk.LEFT, padx=(10, 0))
        
        # Label para estado
        self.label_estado = ttk.Label(main_frame, text="Estado: Listo", foreground="green")
        self.label_estado.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Frame para la lista de contactos
        list_frame = ttk.LabelFrame(main_frame, text="Contactos Extraídos", padding="10")
        list_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview para mostrar contactos
        columns = ("Etiqueta","Nombre", "Teléfono", "Pais")
        self.tree_contactos = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # Configurar columnas
        self.tree_contactos.heading("Etiqueta", text="Etiqueta")
        self.tree_contactos.heading("Nombre", text="Nombre")
        self.tree_contactos.heading("Teléfono", text="Teléfono")
        self.tree_contactos.heading("Pais",text="Pais")
        self.tree_contactos.column("Etiqueta", width=50)
        self.tree_contactos.column("Nombre", width=250)
        self.tree_contactos.column("Teléfono", width=200)
        self.tree_contactos.column("Pais", width=100)
        
        # Configurar estilo para el treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
        
        # Scrollbar para el treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_contactos.yview)
        self.tree_contactos.configure(yscrollcommand=scrollbar.set)
        
        # Grid del treeview y scrollbar
        self.tree_contactos.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Frame para botones de la lista
        list_buttons_frame = ttk.Frame(list_frame)
        list_buttons_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Botón Limpiar Lista
        ttk.Button(
            list_buttons_frame, 
            text="Generar Mensajes", 
            command=self.generar_mensaje
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón Exportar
        ttk.Button(
            list_buttons_frame, 
            text="Exportar CSV", 
            command=self.exportar_csv
        ).pack(side=tk.LEFT)
        
        # Configurar expansión del grid
        main_frame.rowconfigure(4, weight=1)
    
    def iniciar_proceso(self):
        """Inicia el proceso de extracción"""
        enlace = self.entry_enlace.get().strip()
        
        if not enlace:
            messagebox.showerror("Error", "Por favor ingresa un enlace")
            return
         
        self.proceso_activo = 1
        self.actualizar_estado_botones()
        self.actualizar_estado("1. Inicia sesion en el navegador")
        self.iniciar_navegador()
        self.actualizar_estado("creando enlaces de los estudiantes, espera un poco")
        if self.driver is not None:
            while True:
                time.sleep(5)
                if verificar_sesion_iniciada(self.driver):
                    break
            
            crear_enlaces(self.driver, enlace)
            self.actualizar_estado("5. creando contactos, espera un poco")
            self.contactos = crear_contactos(self.driver)
            for i in range(len(self.contactos)):
                self.root.after(0, self.agregar_contacto, self.contactos[i][0], self.contactos[i][1],self.contactos[i][3])
                self.root.after(0, self.actualizar_estado, f"Numero de Estudiantes: {i+1}/{len(self.contactos)}")
            self.count = 0 
        
       
        self.actualizar_estado("2. Presiona el boton de continuar")
        
    def continuar_proceso(self):
        """Continúa el proceso pausado"""
        """if not verificar_sesion_iniciada(self.driver):
            self.mostrar_error("No se ha iniciado sesión, vuelve a iniciar el proceso")
            self.proceso_activo = 0
            self.actualizar_estado_botones()
            self.driver.quit()
            return"""   
        self.actualizar_estado("5. creando contactos, espera un poco")
        self.contactos = crear_contactos(self.driver)
        for i in range(len(self.contactos)):
            self.root.after(0, self.agregar_contacto, self.contactos[i][0], self.contactos[i][1],self.contactos[i][3])
            self.root.after(0, self.actualizar_estado, f"Numero de Estudiantes: {i+1}/{len(self.contactos)}")
        self.count = 0  
        

    def detener_proceso(self):
        """Detiene el proceso"""
        
     
    def agregar_contacto(self, nombre, telefono, pais):
        """Agrega un contacto a la lista"""
        etiqueta = self.entry_nombre.get().strip()
        self.tree_contactos.insert("", "end", values=(etiqueta.upper(), nombre, telefono, pais))
        # Auto-scroll al último elemento
        children = self.tree_contactos.get_children()
        if children:
            self.tree_contactos.see(children[-1])
    
    def generar_mensaje(self):
        mensaje_base = """¡Hola {nombre}! 🌟
Aquí están tus datos de acceso para que puedas unirte a la clase sin problemas. Asegúrate de tenerlos listos:

🔑 Inicio de sesión: {usuario}
🔒 Contraseña: {contrasena}

📝 Recuerda: Guarda estos datos en un lugar seguro y no los compartas con nadie más. Si tienes problemas para iniciar sesión, avísanos y te ayudaremos.

¡Nos vemos en la clase! 💡💻

"""

         # Lista para almacenar todos los estudiantes como diccionarios individuales
        estudiantes = []

        for contacto in self.contactos:
            # Separar credenciales desde el texto del tercer campo
            credenciales = [linea.split(': ')[1] for linea in contacto[2].split('\r\n') if ': ' in linea]
            
            # Crear diccionario con la información del estudiante
            estudiante = {
                "nombre": contacto[0],
                "usuario": credenciales[0] if len(credenciales) > 0 else '',
                "contrasena": credenciales[1] if len(credenciales) > 1 else ''
            }

            estudiantes.append(estudiante)

        # Escribir mensajes en el archivo
        with open("mensajes_estudiantes.txt", "w", encoding="utf-8") as f:
            for est in estudiantes:
                f.write(mensaje_base.format(
                    nombre=est['nombre'],
                    usuario=est['usuario'],
                    contrasena=est['contrasena']
                ))
                f.write("\n" + "-"*50 + "\n")  # Separador opcional entre mensajes


    
    def exportar_csv(self):
        etiqueta = self.entry_nombre.get().strip()
        copy = []
        for contacto in self.contactos:
            copy.append([etiqueta.upper() + " " + contacto[0],contacto[1]])
        exportar_contactos(copy)
        
    
    def actualizar_estado_botones(self):
        """Actualiza el estado de los botones según el proceso"""
        if self.proceso_activo == 0:
            self.btn_iniciar.config(state="normal")
            self.btn_continuar.config(state="disabled")
            self.btn_detener.config(state="disabled")
        else:
            self.btn_iniciar.config(state="disable")
            self.btn_continuar.config(state="normal")
            self.btn_detener.config(state="normal")
    
    def actualizar_estado(self, mensaje):
        """Actualiza el mensaje de estado"""
        self.label_estado.config(text=f"{mensaje}")
    
    def proceso_completado(self):
        """Se ejecuta cuando el proceso se completa"""
        self.proceso_activo = 0
        self.actualizar_estado_botones()
        self.actualizar_estado("Proceso completado")
        messagebox.showinfo("Completado", "El proceso de extracción ha finalizado")
    
    def mostrar_error(self, error):
        """Muestra un error en la interfaz"""
        self.proceso_activo = False
        self.actualizar_estado_botones()
        self.actualizar_estado("Error en el proceso, inicia nuevamente")
        messagebox.showerror("Error", f"{error}")
    

def main():
    root = tk.Tk()
    app = SeleniumInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main()