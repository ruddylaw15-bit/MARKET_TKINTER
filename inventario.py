import sqlite3
from tkinter import * 
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import sys
import os


class Inventario(tk.Frame):

    def __init__(self, padre):
        super().__init__(padre)

    # Inicialización de componentes principales de la interfaz y base de datos
        self.widgets()
        self.articulos_combobox()
        self.cargar_articulos()
        self.timer_articulos = None

    # Configuración del directorio para el almacenamiento local de imágenes
        self.image_folder = "fotos"
        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)

    def widgets(self):
# ************************************************************************************************************************************z
    # Contenedor principal con scroll para mostrar la cuadrícula de artículos registrados    
        canvas_articulos = tk.LabelField if hasattr(tk, 'LabelField') else tk.LabelFrame(self, text="Articulos", font="arial 14 bold", background="#C6D9E3")
        canvas_articulos.place(x=300, y=10, width=780, height=580)

        self.canvas = tk.Canvas(canvas_articulos, bg="#C6D9E3")
        self.scrollbar = tk.Scrollbar(canvas_articulos, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#C6D9E3")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all") # Actualiza el área de desplazamiento del canvas dinamicamen
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
# ************************************************************************************************************************************

    # Panel de búsqueda rápida y filtrado interactivo mediante combobox
        lblframe_buscar = LabelFrame(self, text="Buscar", font="arial 14 bold", bg="#C6D9E3")
        lblframe_buscar.place(x=10, y=10, width=280, height=80)

        self.comboboxbuscar = ttk.Combobox(lblframe_buscar, font="arial 12")
        self.comboboxbuscar.place(x=5, y=5, width=260, height=40)
        self.comboboxbuscar.bind("<<ComboboxSelected>>", self.on_combobox_select)
        self.comboboxbuscar.bind("<KeyRelease>", self.filtrar_articulos)
# ************************************************************************************************************************************

    # Panel informativo que detalla los atributos del artículo seleccionado
        lblframe_seleccion = LabelFrame(self, text="Selección", font="arial 14 bold", bg="#C6D9E3")
        lblframe_seleccion.place(x=10, y=95, width=280, height=190)

        self.label1 = tk.Label(lblframe_seleccion, text="Articulo: ", font="arial 12", bg="#C6D9E3", wraplength=300)
        self.label1.place(x=5, y=5)

        self.label2 = tk.Label(lblframe_seleccion, text="Precio: ", font="arial 12", bg="#C6D9E3")
        self.label2.place(x=5, y=40)

        self.label3 = tk.Label(lblframe_seleccion, text="Costo: ", font="arial 12", bg="#C6D9E3")
        self.label3.place(x=5, y=70)

        self.label4 = tk.Label(lblframe_seleccion, text="Stock: ", font="arial 12", bg="#C6D9E3")
        self.label4.place(x=5, y=100)

        self.label5 = tk.Label(lblframe_seleccion, text="Estado: ", font="arial 12", bg="#C6D9E3")
        self.label5.place(x=5, y=130)
# ************************************************************************************************************************************
        
    # Panel de acciones CRUD (Agregar y Editar registros en el inventario)
        lblframe_botones = LabelFrame(self, bg="#C6D9E3", text="Opciones", font="arial 14 bold")
        lblframe_botones.place(x=10, y=290, width=280, height=300)

        btn1 = tk.Button(lblframe_botones, text="Agregar", font="arial 14 bold", command=self.agregar_articulo)
        btn1.place(x=20, y=20, width=180, height=40)

        btn2 = tk.Button(lblframe_botones, text="Editar", font="arial 14 bold", command=self.editar_articulo)
        btn2.place(x=20, y=80, width=180, height=40)

    def load_image(self):

    # Abre el explorador de archivos para seleccionar una imagen nueva
        file_path = filedialog.askopenfilename()
        if file_path:

    # Abre y redimensiona la imagen seleccionada utilizando un filtro de alta calidad
            image = Image.open(file_path)
            image = image.resize((200, 200), Image.Resampling.LANCZOS)

    # Copia y guarda la imagen dentro de la carpeta local del sistem
            image_name = os.path.basename(file_path)
            image_save_path = os.path.join(self.image_folder, image_name)
            image.save(image_save_path)

    # Almacena la referencia de la imagen para evitar que Python la elimine de la memoria
            self.image_tk = ImageTk.PhotoImage(image)

            self.product_image = self.image_tk
            self.image_path = image_save_path

    # Actualiza o dibuja la previsualización de la imagen cargada dentro del frame contenedor
            img_label = tk.Label(self.frameing, image = self.image_tk)
            img_label.place(x=0, y=0, width=200, height=200)

    def articulos_combobox(self):

    # Conecta con la base de datos SQLite y extrae todos los nombres de artículos para el autocompletado
        self.con = sqlite3.connect('database.db')
        self.cur = self.con.cursor()
        self.cur.execute("SELECT articulo FROM articulos")
        self.articulos = [row[0] for row in self.cur.fetchall()]
        self.comboboxbuscar['values'] = self.articulos

    def agregar_articulo(self):

    # Crea una ventana secundaria flotante (Toplevel) para el registro de nuevos artículos
        top = tk.Toplevel(self)
        top.title("Agregar Articulo")
        top.geometry("700x400+200+50")
        top.config(bg="#C6D9E3")
        top.resizable(False, False)

    # Configura la ventana modal para bloquear interacción con la principal hasta cerrarla
        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()

    # Campo de entrada para el nombre del artículo
        tk.Label(top, text="Articulos: ", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=20, width=80, height=25)
        entry_articulo = ttk.Entry(top, font="arial 12 bold")
        entry_articulo.place(x=120, y=20, width=250, height=30)

    # Campo de entrada para el precio de venta al público
        tk.Label(top, text="Precio: ", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=60, width=80, height=25)
        entry_precio = ttk.Entry(top, font="arial 12 bold")
        entry_precio.place(x=120, y=60, width=250, height=30)

    # Campo de entrada para el costo de adquisición del producto
        tk.Label(top, text="Costo: ", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=100, width=80, height=25)
        entry_costo = ttk.Entry(top, font="arial 12 bold")
        entry_costo.place(x=120, y=100, width=250, height=30)

    # Campo de entrada para la cantidad disponible en inventario (Stock)
        tk.Label(top, text="Stock: ", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=140, width=80, height=25)
        entry_stock = ttk.Entry(top, font="arial 12 bold")
        entry_stock.place(x=120, y=140, width=250, height=30)

    # Campo de entrada para definir el estado actual del artículo (Activo/Inactivo)
        tk.Label(top, text="Estado: ", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=180, width=80, height=25)
        entry_estado = ttk.Entry(top, font="arial 12 bold")
        entry_estado.place(x=120, y=180, width=250, height=30)

    # Contenedor visual enmarcado para la previsualización de la imagen del producto
        self.frameing = tk.Frame(top, bg="white", highlightbackground="gray", highlightthickness=1)
        self.frameing.place(x=440, y=30, width=200, height=200)

    # Boton para activar el selector de archivos e importar la imagen del articulo
        btnimage = tk.Button(top, text="Cargar imagen", font="arial 12 bold", command=self.load_image)
        btnimage.place(x=470, y=260, width=150, height=40)

        def guardar():

    # Obtiene los valores ingresados en cada campo de la ventan
            articulo = entry_articulo.get()
            precio = entry_precio.get()
            costo = entry_costo.get()
            stock = entry_stock.get()
            estado = entry_estado.get()

    # Valida que ningún campo se encuentre vacío antes de continuar
            if not articulo or not precio or not costo or not stock or not estado:
                messagebox.showerror("Error", "Todos los campos deben ser completados")
                return

    # Intenta convertir los campos numéricos a sus tipos de datos correctos
            try:
                precio = float(precio)
                costo = float(costo)
                stock = int(stock)
            except ValueError:
                messagebox.showerror("Error", "precio, costo y stock deben ser numeros validos")

    # Verifica si se seleccionó una imagen propia; de lo contrario, asigna una por defecto
            if hasattr(self, 'image_path'):
                image_path = self.image_path
            else:
                image_path = (r"fotos/default.png")

    # Realiza la inserción del nuevo artículo en la base de datos SQLite
            try:
                self.cur.execute("INSERT INTO articulos(articulo, precio, costo, stock, estado, image_path) VALUES (?, ?, ?, ?, ?, ?)",
                                    (articulo, precio, costo, stock, estado, image_path))
                self.con.commit()
                messagebox.showinfo("Exito", "Articulo agrgado correctamente")
                top.destroy()
                self.cargar_articulos()
                self.articulos_combobox()
            except sqlite3.Error as e:
                print("Error al cargar el articulo:", e)
                messagebox.showerror("Error", "Error al agregar el articulo")
                return
    
    # Botones de acción principales (Guardar o Cancelar la operación)
        tk.Button(top, text="Guardar", font="arial 12 bold", command=guardar).place(x=50, y=260, width=150, height=40)
        tk.Button(top, text="Cancelar", font="arial 12 bold", command=top.destroy).place(x=260, y=260, width=150, height=40)

    def cargar_articulos(self, filtro=None, categoria=None):
    # Refresca y carga la lista visual de artículos en el canvas principal mediante un hilo seguro
        self.after(0, self._cargar_articulos, filtro, categoria)

    def _cargar_articulos(self, filtro=None, categoria=None):
    # Limpia y destruye todos los widgets previos dentro del frame con scroll antes de recargar
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    # Prepara la consulta SQL base para obtener nombre, precio y ruta de imagen de los artículos
        query = "SELECT articulo, precio, image_path FROM articulos"
        params = []

    # Aplica un filtro de búsqueda parcial por nombre si se proporciona un parámetro
        if filtro:
            query += " WHERE articulo LIKE ?"
            params.append(f'%{filtro}%')

    # Ejecuta la consulta en la base de datos y recupera los resultados
        self.cur.execute(query, params)
        articulos = self.cur.fetchall()

    # Inicializa las coordenadas de la cuadrícula (fila y columna inicial)
        self.row = 0
        self.column = 0

    # Recorre cada registro obtenido para renderizar su tarjeta visual en la interfaz
        for articulo, precio, image_path in articulos:
            self.mostrar_articulo(articulo, precio, image_path)

    def mostrar_articulo(self, articulo, precio, image_path):
    # Crea un marco contenedor individual para cada tarjeta de artículo con bordes y fondo blanco
        article_frame = tk.Frame(self.scrollable_frame, bg="white", relief="solid")
        article_frame.grid(row=self.row, column=self.column, padx=10, pady=10)

    # Carga, redimensiona y muestra la imagen del artículo si existe la ruta en disco
        if image_path and os.path.exists(image_path):
            image = Image.open(image_path)
            image = image.resize((150, 150), Image.LANCZOS)
            image = ImageTk.PhotoImage(image)

            image_label = tk.Label(article_frame, image=image)
            image_label.image = image  # ⚡ Mantiene la referencia para evitar el recolector de basura de Python
            image_label.pack(expand=True, fill="both")

    # Etiqueta superior con el nombre del artículo
        name_label = tk.Label(article_frame, text=articulo, bg="white", anchor="w", wraplength=150, font="arial 10 bold")
        name_label.pack(side="top", fill="x")

    # Etiqueta inferior con el precio formateado a dos decimales
        precio_label = tk.Label(article_frame, text=f"Precio: Bs.{precio:.2f}", bg="white", anchor="w", wraplength=150, font="arial 10 bold")
        precio_label.pack(side="bottom", fill="x")

    # Controla la posición en la cuadrícula: avanza una columna y salta a la siguiente fila al superar 3 columnas
        self.column += 1
        if self.column > 3:
            self.column = 0
            self.row += 1

    def on_combobox_select(self, event):
    # Evento que se dispara al seleccionar un elemento del combobox para actualizar las etiquetas de información
        self.actualizar_label()

    def actualizar_label(self, event=None):
    # Obtiene el nombre del artículo actualmente seleccionado en la barra de búsqueda
        articulo_seleccionado = self.comboboxbuscar.get()

        try:
    # Consulta los detalles completos del artículo específico en la base de datos
            self.cur.execute("SELECT articulo, precio, costo, stock, estado FROM articulos WHERE articulo=?", (articulo_seleccionado,))
            resultado = self.cur.fetchone()

            if resultado is not None:
                articulo, precio, costo, stock, estado = resultado

    # Actualiza cada etiqueta del panel de selección con la información obtenida
                self.label1.config(text=f"Articulo: {articulo}")
                self.label2.config(text=f"Precio: {precio}")
                self.label3.config(text=f"Costo: {costo}")
                self.label4.config(text=f"Stock: {stock}")

                self.label5.config(text=f"Estado: {estado}")
    # Cambia el color del texto del estado dinámicamente según su valor lógico
                if estado.lower() == "activo":
                    self.label5.config(fg="green")
                elif estado.lower() == "inactivo":
                    self.label5.config(fg="red")
                else:
                    self.label5.config(fg="black")

            else:
    # Restablece las etiquetas a valores por defecto si no se encuentra el artículo
                self.label1.config(text="Articulo: No encontrado")
                self.label2.config(text="Precio: N/A")
                self.label3.config(text="Costo: N/A")
                self.label4.config(text="Stock: N/A")
                self.label5.config(text="Estado: N/A")
            
        except sqlite3.Error as e:
            print("Error al obtener los datos del articulo:", e)
            messagebox.showerror("Error", "Error al obtener los datos del articulo")

    def filtrar_articulos(self, event):
    # Implementa un temporizador (debounce) para evitar consultas excesivas mientras el usuario escribe rápido
        if self.timer_articulos:
            self.timer_articulos.cancel()
        self.timer_articulos = threading.Timer(0.5, self._filter_articulos)
        self.timer_articulos.start()

    def _filter_articulos(self):
    # Obtiene el texto escrito actualmente en el buscador
        typed = self.comboboxbuscar.get()

    # Filtra la lista de artículos según coincidencia parcial de texto
        if typed == '':
            data = self.articulos
        else:
            data = [item for item in self.articulos if typed.lower() in item.lower()]

    # Actualiza los valores desplegables del combobox o muestra mensaje de resultado vacío
        if data:
            self.comboboxbuscar['values'] = data
            self.comboboxbuscar.event_generate('<Down>')
        else:
            self.comboboxbuscar['values'] = ['No se encontraron resultados']

    # Refresca la vista principal aplicando el filtro de búsqueda escrito
        self.cargar_articulos(filtro=typed)

    def editar_articulo(self):
    #  Obtiene el artículo seleccionado en el combobox para proceder a su edición
        selected_item = self.comboboxbuscar.get()

        if not selected_item:
            messagebox.showerror("Error", "Selecciona un articulo para editar")
            return

    # Busca todos los datos actuales del artículo en la base de datos
        self.cur.execute("SELECT articulo, precio, costo, stock, estado, image_path FROM articulos WHERE articulo=?", (selected_item,))
        resultado = self.cur.fetchone()

        if not resultado:
            messagebox.showerror("Error", "Articulo no encontrado")
            return  

    # Crea la ventana flotante (Toplevel) para modificar los datos del artículo
        top = tk.Toplevel(self)
        top.title("Editar Articulo")
        top.geometry("700x400+200+50")
        top.config(bg="#C6D9E3")
        top.resizable(False, False)

    # Configura la ventana como modal dependiente de la principal
        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()

        (articulo, precio, costo, stock, estado, image_path) = resultado

    # Campos de entrada precargados con la información actual del producto
        tk.Label(top, text="Articulo: ", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=20, width=80, height=25)
        entry_articulo = ttk.Entry(top, font="arial 12 bold")
        entry_articulo.place(x=120, y=20, width=250, height=30)
        entry_articulo.insert(0, articulo)

        tk.Label(top, text="Precio: ", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=60, width=80, height=25)
        entry_precio = ttk.Entry(top, font="arial 12 bold")
        entry_precio.place(x=120, y=60, width=250, height=30)
        entry_precio.insert(0, precio)

        tk.Label(top, text="Costo: ", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=100, width=80, height=25)
        entry_costo = ttk.Entry(top, font="arial 12 bold")
        entry_costo.place(x=120, y=100, width=250, height=30)
        entry_costo.insert(0, costo)

        tk.Label(top, text="Stock: ", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=140, width=80, height=25)
        entry_stock = ttk.Entry(top, font="arial 12 bold")
        entry_stock.place(x=120, y=140, width=250, height=30)
        entry_stock.insert(0, stock)

        tk.Label(top, text="Estado: ", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=180, width=80, height=25)
        entry_estado = ttk.Entry(top, font="arial 12 bold")
        entry_estado.place(x=120, y=180, width=250, height=30)
        entry_estado.insert(0, estado)

    # Marco visual para mostrar la imagen actual del artículo en edición
        self.frameing = tk.Frame(top, bg="white", highlightbackground="gray", highlightthickness=1)
        self.frameing.place(x=440, y=30, width=200, height=200)

        if image_path and os.path.exists(image_path):
            image = Image.open(image_path)
            image = image.resize((200, 200), Image.LANCZOS)
            self.product_image = ImageTk.PhotoImage(image)
            self.image_path = image_path
            image_label = tk.Label(self.frameimg, image=self.product_image)
            image_label.pack(expand=True, fill="both")

    # Boton para cambiar o cargar una nueva imagen
        btnimagen = tk.Button(top, text="Cargar Imagen", font="arial 12 bold", command=self.load_image)
        btnimagen.place(x=470, y=260, width=150, height=40)

        def guardar():
    # Recoge los valores modificados de los campos de texto
            nuevo_articulo = entry_articulo.get()
            precio = entry_precio.get()
            costo = entry_costo.get()
            stock = entry_stock.get()
            estado = entry_estado.get()

    # Verifica que ningún campo quede vacío
            if not nuevo_articulo or not precio or not costo or not stock or not estado:
                messagebox.showerror("Error", "Todos los campos deben ser completados")
                return

    # Valida y convierte los campos numéricos correspondientes
            try:
                precio = float(precio)
                costo = float(costo)
                stock = int(stock)
            except ValueError:
                messagebox.showerror("Error", "Precio, costo y stock deben ser numeros validos")
                return

    # Valida la ruta de la imagen seleccionada o mantiene la existente por defecto
            if hasattr(self, 'image_path'):
                image_path = self.image_path
            else:
                image_path = (r"fotos/default.png")

    # Ejecuta la sentencia SQL para actualizar los datos en la base de datos
            self.cur.execute("UPDATE articulos SET articulo=?, precio=?, costo=?, stock=?, image_path=?, estado=? WHERE articulo=?",
                             (nuevo_articulo, precio, costo, stock, image_path, estado, selected_item))
            self.con.commit()

    # Actualiza el combobox y recarga los artículos en la vista principal
            self.articulos_combobox()
            self.after(0, lambda: self.cargar_articulos(filtro=nuevo_articulo))

            top.destroy()
            messagebox.showinfo("Exito", "Articulo editado exitosamente")

    # Boton para confirmar y guardar los cambios realizados
        btn_guardar = tk.Button(top, text="Guardar", font="arial 12 bold", command=guardar)
        btn_guardar.place(x=260, y=260, width=150, height=40)