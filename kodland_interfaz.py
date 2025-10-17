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
Ejecuta este archivo directamente:

>>> python kodland interfaz.py

"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading, queue
from kodland_scraping import KodlandScraper
import os
from tkinter import filedialog


class SeleniumInterface:
    def __init__(self, root):
        """
        Inicializa la interfaz gráfica de usuario (GUI) para el scraping de Kodland.
        Parámetros:
        - root: instancia principal de la ventana de Tkinter
        """
        self.root = root
        self.root.title("Automatizador Kodland")
        self.root.geometry("800x500")
        self.root.resizable(True, True)
        self.mensaje = queue.Queue()  # Cola de mensajes de estado
        self.contactos_mensaje = queue.Queue()  # Cola para nuevos contactos
        self.contactos = []
        self.scrap = None
        self.crear_interfaz()

    def iniciar_scraping(self, enlace, ruta = ''):
        """Inicia el scraper en un hilo separado para no congelar la interfaz."""
        self.limpiar_datos()
        if  ruta != '':
            self.scrap = KodlandScraper(enlace, self.mensaje, self.contactos_mensaje)
            threading.Thread(target=self.scrap.cargar, args=(ruta,), daemon=True).start()
        else:
            self.scrap = KodlandScraper(enlace, self.mensaje, self.contactos_mensaje)
            threading.Thread(target=self.scrap.iniciarProceso, daemon=True).start()

    def actualizar_mensajes(self):
        """Revisa la cola de mensajes y actualiza el estado en la interfaz si hay nuevos mensajes."""
        try:
            while True:
                mensaje = self.mensaje.get_nowait()
                self.label_estado.config(text=f"{mensaje}")
        except queue.Empty:
            pass
        self.root.after(100, self.actualizar_mensajes)

    def revisar_nuevos_contactos(self):
        """Revisa la cola de nuevos contactos y los agrega automáticamente al TreeView."""
        try:
            while True:
                contacto = self.contactos_mensaje.get_nowait()
                nombre, telefono, pais = contacto
                self.root.after(0, self.agregar_contacto, nombre, telefono, pais)
        except queue.Empty:
            pass
        self.root.after(100, self.revisar_nuevos_contactos)

    def crear_interfaz(self):
        """Crea todos los elementos visuales de la aplicación."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Campos de entrada
        ttk.Label(main_frame, text="Enlace del grupo:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_enlace = ttk.Entry(main_frame, width=50)
        self.entry_enlace.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Etiqueta(opcional):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_nombre = ttk.Entry(main_frame, width=50)
        self.entry_nombre.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # Botones principales
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        self.btn_iniciar = ttk.Button(button_frame, text="Iniciar Proceso", command=self.iniciar_proceso, style="Accent.TButton")
        self.btn_iniciar.pack(side=tk.LEFT, padx=(0, 10))

        self.label_estado = ttk.Label(main_frame, text="Estado: Listo", foreground="green")
        self.label_estado.grid(row=3, column=0, columnspan=2, pady=10)

        # Vista de contactos
        list_frame = ttk.LabelFrame(main_frame, text="Contactos Extraídos", padding="10")
        list_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        columns = ("Etiqueta", "Nombre", "Teléfono", "Pais")
        self.tree_contactos = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree_contactos.heading(col, text=col)
        self.tree_contactos.column("Etiqueta", width=50)
        self.tree_contactos.column("Nombre", width=250)
        self.tree_contactos.column("Teléfono", width=200)
        self.tree_contactos.column("Pais", width=100)

        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_contactos.yview)
        self.tree_contactos.configure(yscrollcommand=scrollbar.set)
        self.tree_contactos.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        list_buttons_frame = ttk.Frame(list_frame)
        list_buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(list_buttons_frame, text="Generar Mensajes", command=self.generar_mensaje).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(list_buttons_frame, text="Exportar CSV", command=self.exportar_csv).pack(side=tk.LEFT)

        #los botones seran utilizados para una implementación de un modulo extra
        self.btn_continuar = ttk.Button(button_frame, text="Cargar Grupo", command=self.continuar_proceso, state="normal")
        self.btn_continuar.pack(side=tk.LEFT, padx=(10, 0))

        ##self.btn_detener = ttk.Button(button_frame, text="Detener", command=self.detener_proceso, state="normal")
        ##self.btn_detener.pack(side=tk.LEFT, padx=(10, 0))

        main_frame.rowconfigure(4, weight=1)
        self.mensaje.put("Ingresa el enlace del grupo que quieras extraer la información")

        self.actualizar_mensajes()
        self.revisar_nuevos_contactos()

    def iniciar_proceso(self):
        """Valida el enlace y llama a iniciar_scraping si es válido."""
        enlace = self.entry_enlace.get().strip()
        if not enlace:
            messagebox.showerror("Error", "Por favor ingresa un enlace")
            return
        self.iniciar_scraping(enlace)

    

    def continuar_proceso(self):
        """Abre un cuadro de diálogo para elegir una carpeta y muestra las subcarpetas en una lista seleccionable."""
        # Seleccionar carpeta raíz
        """carpeta_base = filedialog.askdirectory(title="Selecciona la carpeta base")
        if not carpeta_base:
            return"""
        carpeta_base = "kodland"
        # Obtener subcarpetas
        subcarpetas = [nombre for nombre in os.listdir(carpeta_base)
                        if os.path.isdir(os.path.join(carpeta_base, nombre))]

        if not subcarpetas:
            messagebox.showinfo("Información", "No se encontraron subcarpetas en la carpeta seleccionada.")
            return

        # Crear ventana emergente
        ventana_lista = tk.Toplevel(self.root)
        ventana_lista.title("Selecciona una carpeta del grupo")
        ventana_lista.geometry("400x300")
        ventana_lista.grab_set()  # Bloquea la ventana principal mientras está abierta

        ttk.Label(ventana_lista, text="Selecciona una carpeta:").pack(pady=10)

        # Lista de carpetas
        lista = tk.Listbox(ventana_lista, font=("Helvetica", 12))
        lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for carpeta in subcarpetas:
            lista.insert(tk.END, carpeta)

        # Botón de selección
        def seleccionar():
            seleccion = lista.get(tk.ACTIVE)
            if seleccion:
                ruta = f'kodland\{seleccion}\link.txt'
                ventana_lista.destroy()
                if os.path.isfile(ruta):
                    with open(ruta, 'r', encoding='utf-8') as f:
                        enlace = f.read()
                    confirmacion = messagebox.askyesno("Confirmar", "¿Desea Cargar los datos sin actualizarlos?, para actualizar tendras que iniciar sesion")
                    if confirmacion:
                        self.iniciar_scraping(enlace, f'kodland\{seleccion}')
                    else:
                        self.iniciar_scraping(enlace)

        ttk.Button(ventana_lista, text="Seleccionar", command=seleccionar).pack(pady=10)
        
    def limpiar_datos(self):
        for item in self.tree_contactos.get_children():
            self.tree_contactos.delete(item)

        # Vaciar listas internas
        self.contactos.clear()
        if self.scrap:
            self.scrap.contactos.clear()


    def detener_proceso(self):
        """(Reservado para implementación futura de detener el scraping en curso)."""
        pass

    def agregar_contacto(self, nombre, telefono, pais):
        """Agrega un nuevo contacto al árbol visual de contactos."""
        etiqueta = self.entry_nombre.get().strip()
        self.tree_contactos.insert("", "end", values=(etiqueta.upper(), nombre, telefono, pais))
        children = self.tree_contactos.get_children()
        if children:
            self.tree_contactos.see(children[-1])

    def generar_mensaje(self):
        """Genera mensajes personalizados con usuario y contraseña para cada contacto.
           se guarda en un archivo de texto llamado "mensajes_estudiantes.txt" para poder ser enviado a cada estudiante al iniciar el curso 
        """
        mensaje_base = """¡Hola {nombre}! 🌟\nAquí están tus datos de acceso para que puedas unirte a la clase sin problemas. Asegúrate de tenerlos listos:\n\n🔑 Inicio de sesión: {usuario}\n🔒 Contraseña: {contrasena}\n\n📝 Recuerda: Guarda estos datos en un lugar seguro y no los compartas con nadie más. Si tienes problemas para iniciar sesión, avísanos y te ayudaremos.\n\n¡Nos vemos en la clase! 💡💻\n\n"""
        estudiantes = []
        self.contactos = self.scrap.contactos
        for contacto in self.contactos:
            credenciales = [linea.split(': ')[1] for linea in contacto[2].split('\r\n') if ': ' in linea]
            estudiante = {
                "nombre": contacto[0],
                "usuario": credenciales[0] if len(credenciales) > 0 else '',
                "contrasena": credenciales[1] if len(credenciales) > 1 else ''
            }
            estudiantes.append(estudiante)

        with open("mensajes_estudiantes.txt", "w", encoding="utf-8") as f:
            for est in estudiantes:
                f.write(mensaje_base.format(**est))
                f.write("\n" + "-" * 50 + "\n")
        messagebox.showinfo("Información", "Mensajes de inicio de sesión guardados en 'mensajes_estudiantes.txt'")

    def exportar_csv(self):
        """Exporta los contactos extraídos al formato CSV de Google."""
        etiqueta = self.entry_nombre.get().strip()
        self.contactos = self.scrap.contactos
        copy = []
        for contacto in self.contactos:
            copy.append([etiqueta.upper() + " " + contacto[0], contacto[1]])
        print(copy)
        self.scrap.exportar_contactos(copy)
        messagebox.showinfo("Información", "Datos exportados a 'contactos_google.csv'")

    def actualizar_estado(self, mensaje):
        """Actualiza el texto del estado manualmente desde cualquier método."""
        self.label_estado.config(text=f"{mensaje}")


def main():
    root = tk.Tk()
    app = SeleniumInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main()