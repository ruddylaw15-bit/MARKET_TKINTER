import sqlite3
from tkinter import * 
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import threading
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import sys
import os

class Ventas(tk.Frame):
    db_name = "database.db"

    def __init__(self, padre):
        super().__init__(padre)
    # Inicializa el correlativo de factura consultando el valor máximo actual en la base de datos
        self.numero_factura = self.obtener_numero_factura_actual()
        self.productos_seleccionados = []
        self.widgets()
        self.cargar_producto()
        self.timer_producto = None

    def obtener_numero_factura_actual(self):
        """Consulta la base de datos para determinar el siguiente número de factura correlativo."""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT MAX (factura) FROM ventas")
            last_invoice_number = c.fetchone()[0]
            conn.close()
    # Si existen registros incrementa en 1, de lo contrario comienza en la factura 1
            return last_invoice_number + 1 if last_invoice_number is not None else 1 
        except sqlite3.Error as e:
            print("Error obteniendo el numero de factura actual:", e)
            return 1

    def cargar_producto(self):
        """Rellena el Combobox de productos con la lista de artículos registrados en el inventario."""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT articulo FROM articulos") 
            self.products = [product[0] for product in c.fetchall()]
            self.entry_producto["values"] = self.products
            conn.close()
        except sqlite3.Error as e:
            print("Error cargando productos:", e) 

    def filtrar_productos(self, event):
            """Gestiona un temporizador (debounce) para retrasar la búsqueda mientras el usuario escribe,
            evitando consultas innecesarias en cada pulsación de tecla."""
            if hasattr(self, 'timer_producto') and self.timer_producto:
                self.timer_producto.cancel()
            
    # Llama a la función de filtrado interno después de 0.5 segundos de inactividad
            self.timer_producto = threading.Timer(0.5, self._filter_productos)
            self.timer_producto.start()

    def _filter_productos(self):
        """Filtra la lista de productos según el texto ingresado y despliega los resultados de manera dinámica."""
        typed = self.entry_producto.get()

    # Si el campo está vacío, muestra la lista completa; de lo contrario, filtra coincidencias (ignorando mayúsculas)
        if typed == '':
            data = self.products
        else:
            data = [item for item in self.products if typed.lower() in item.lower()]

    # Actualiza las opciones del Combobox según los resultados encontrados
        if data:
            self.entry_producto['values'] = data
    #  Simula una tecla hacia abajo para forzar la apertura del menú desplegable con las opciones
            self.entry_producto.event_generate('<Down>')
        else:
            # Si no hay coincidencias, muestra un mensaje de aviso y limpia el campo
            self.entry_producto['values'] = ['No se encontraron resultados']
            self.entry_producto.event_generate('<Down>')
            self.entry_producto.delete(0, tk.END)

    def agregar_articulo(self):
        """Valida stock, calcula subtotales y agrega el artículo seleccionado a la tabla de ventas (Treeview)."""
        cliente = self.entry_cliente.get()
        producto = self.entry_producto.get()
        cantidad = self.entry_cantidad.get()

    # Validaciones iniciales de campos vacios o incorrectos
        if not cliente:
            messagebox.showerror("Error", "Por favor seleccione un cliente.")
            return

        if not producto:
            messagebox.showerror("Error", "Por favor seleccione un producto.")
            return

        if not cantidad.isdigit() or int(cantidad) <= 0:
            messagebox.showerror("Error", "Por favor ingrese una cantidad valida.")
            return 

        cantidad = int(cantidad)
        
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
    # Consulta el precio, costo y stock actual del artículo en la base de datos
            c.execute("SELECT precio, costo, stock FROM articulos WHERE articulo=?", (producto,))
            resultado = c.fetchone()

            if resultado is None:
                messagebox.showerror("Error", "Producto no encontrado.")
                conn.close()
                return

            precio, costo, stock = resultado

    # Validación estricta de stock disponible en almacén
            if cantidad > stock:
                messagebox.showerror("Error", f"Stock insuficiente. solo hay {stock} unidades disponibles.")
                conn.close()
                return

    # Cálculo del precio total del ítem
            total = precio * cantidad
            
    # NOTA CORREGIDA: Formateos ajustados para evitar errores tipográficos de sintaxis f-string o cadenas sueltas
            precio_formato = f"{precio:,.2f}"
            total_formato = f"{total:,.2f}"

    # Inserta los datos visuales en el Treeview de ventas
            self.tre.insert("", "end", values=(self.numero_factura, cliente, producto, precio_formato, cantidad, total_formato))
            
    # Almacena de manera interna los datos estructurados para su posterior procesamiento o guardado definitivo
            if not hasattr(self, 'productos_seleccionados'):
                self.productos_seleccionados = []
            self.productos_seleccionados.append((self.numero_factura, cliente, producto, precio, cantidad, total_formato, costo))

            conn.close()

    # Limpia los campos de entrada tras agregar con éxito
            self.entry_producto.set('')
            self.entry_cantidad.delete(0, 'end')

        except sqlite3.Error as e:
            print("Error al agregar articulo", e)

        self.calcular_precio_total()

    def calcular_precio_total(self):
            """Suma todos los subtotales de la tabla (Treeview) y actualiza la etiqueta del total a pagar."""
            total_pagar = sum(float(str(self.tre.item(item)["values"][-1]).replace(" ", "").replace(",", "")) for item in self.tre.get_children())
            
    # "{:,.0f}" da un formato en miles 
            total_pagar_formateado = "{:,.0f}".format(total_pagar)
            
            self.label_precio_total.config(text=f"Precio a Pagar: Bs {total_pagar_formateado}")

    def actualizar_stock(self, event=None):
        """Consulta y muestra en tiempo real el stock disponible del producto seleccionado en el Combobox."""
        self.producto_seleccionado = self.entry_producto.get()

        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT stock FROM articulos WHERE articulo=?", (self.producto_seleccionado,))
            resultado = c.fetchone()
            
            stock = resultado[0] if resultado else 0
            conn.close()

    # Muestra el stock actual en la etiqueta correspondiente
            self.label_stock.config(text=f"Stock: {stock}")

        except sqlite3.Error as e:
            print("Error al obtener el stock del producto:", e)

    def realizar_pago(self):
        """Abre una ventana emergente (Toplevel) para procesar el pago y calcular el cambio."""
        if not self.tre.get_children():
            messagebox.showerror("Error", "No hay productos seleccionados para realizar el pago.")
            return

    # Suma los totales desde la lista interna de productos seleccionados
        total_venta = sum(float(item[5].replace(" ", "").replace(",", "")) for item in self.productos_seleccionados)
        total_formateado = "{:,.0f}".format(total_venta)

    # Configuración de la ventana modal de pago
        ventana_pago = tk.Toplevel(self)
        ventana_pago.title("Realizar pago")
        ventana_pago.geometry("400x400+450+80")
        ventana_pago.config(bg="#C6D9E3")
        ventana_pago.resizable(False, False)
        ventana_pago.transient(self.master)
        ventana_pago.grab_set()
        ventana_pago.focus_set()
        ventana_pago.lift()

    # Títulos e información general en la ventana de pago
        label_titulo = tk.Label(ventana_pago, text="Realizar Pago", font="sans 30 bold", bg="#C6D9E3")
        label_titulo.place(x=70, y=10)

        label_total = tk.Label(ventana_pago, text=f"Total a pagar: Bs {total_formateado}", font="sans 14 bold", bg="#C6D9E3")
        label_total.place(x=80, y=100)

        label_monto = tk.Label(ventana_pago, text="Ingrese el monto pagado:", font="sans 14 bold", bg="#C6D9E3")
        label_monto.place(x=80, y=160)

    # Campo de entrada para registrar el dinero entregado por el cliente
        entry_monto = ttk.Entry(ventana_pago, font="sans 14 bold")
        entry_monto.place(x=80, y=210, width=240, height=40)

    # Boton para confirmar la transacción
        
        button_confirmar_pago = ttk.Button(ventana_pago, text="Confirmar pago", command=lambda: self.procesar_pago(entry_monto.get(), ventana_pago, total_venta))
        button_confirmar_pago.place(x=80, y=270, width=240, height=40)

    def procesar_pago(self, cantidad_pagada, ventana_pago, total_venta):
        """Valida el monto ingresado, calcula el cambio, registra la venta en la base de datos, 
        actualiza el stock y limpia la interfaz para una nueva transacción."""
        
     # Convierte el monto pagado a decimal para operar
        try:
            cantidad_pagada = float(cantidad_pagada)
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese un monto valido en números.")
            return

        cliente = self.entry_cliente.get()

    # Validación si el dinero es insuficiente
        if cantidad_pagada < total_venta:
            messagebox.showerror("Error", "La cantidad pagada es insuficiente.")
            return

    # Cálculo del cambio o devuelta
        cambio = cantidad_pagada - total_venta

        total_formateado = "{:,.0f}".format(total_venta)

    # Muestra el mensaje con el resumen del pago
        mensaje = f"Total: {total_formateado} \nCantidad pagada: {cantidad_pagada:,.0f} \nCambio: {cambio:,.0f} "
        messagebox.showinfo("Pago realizado", mensaje)

        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()

    # Obtiene la fecha y hora actual del sistema
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
            hora_actual = datetime.datetime.now().strftime("%H:%M:%S")

            for item in self.productos_seleccionados:
                factura, cliente, producto, precio, cantidad, total, costo = item
                
                total_limpio = float(total.replace(" ", "").replace(",", ""))
                
                c.execute("INSERT INTO ventas (factura, cliente, articulo, precio, cantidad, total, costo, fecha, hora) VALUES (?,?,?,?,?,?,?,?,?)",(factura, cliente, producto, precio, cantidad, total_limpio, costo * cantidad, fecha_actual, hora_actual))
                c.execute("UPDATE articulos SET stock = stock - ? WHERE articulo = ?", (cantidad, producto))

            conn.commit()

            self.generar_factura_pdf(total_venta, cliente)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al registrar la venta: {e}")
            return

    # Incrementa el número de factura para la siguiente venta
        self.numero_factura += 1
        
    # Actualiza el identificador de factura en pantalla si el label existe
        if hasattr(self, 'label_numero_factura'):
            self.label_numero_factura.config(text=str(self.numero_factura))

    # Restablece la lista interna de productos y limpia la interfaz
        self.productos_seleccionados = []
        self.limpiar_campos()

    # Cierra la ventana emergente de pago
        ventana_pago.destroy()

    def limpiar_campos(self):
        """Limpia la tabla de ventas, restablece el precio total a 0 y borra los campos de entrada."""
        for item in self.tre.get_children():
            self.tre.delete(item)
            
        self.label_precio_total.config(text="Precio a pagar: Bs 0 ")

        self.entry_producto.set('')
        self.entry_cantidad.delete(0, 'end')
        
    def limpiar_listas(self):
            """Limpia todos los elementos del Treeview, vacía la lista de selección y actualiza el total a pagar."""
            self.tre.delete(*self.tre.get_children())
            self.productos_seleccionados.clear()
            self.calcular_precio_total()

    def eliminar_articulo(self):
        """Elimina el artículo seleccionado de la tabla visual (Treeview) y de la lista interna de productos."""
        item_seleccionado = self.tre.selection()
        if not item_seleccionado:
            messagebox.showerror("Error", "No hay ningun articulo seleccionado.")
            return

        item_id = item_seleccionado[0]
        valores_item = self.tre.item(item_id)["values"]
        factura, cliente, articulo, precio, cantidad, total = valores_item

        self.tre.delete(item_id)

        self.productos_seleccionados = [producto for producto in self.productos_seleccionados if producto[2] != articulo]

        self.calcular_precio_total()

    def editar_articulo(self):
        """Modifica la cantidad de un artículo existente en la tabla, valida stock y actualiza los subtotales."""
        selected_item = self.tre.selection()
        if not selected_item:
            messagebox.showerror("Error", "Por favor seleccione un articulo para editar.")
            return

        item_values = self.tre.item(selected_item[0], 'values')
        if not item_values:
            return
        
        current_producto = item_values[2]
        current_cantidad = item_values[4]

    # Abre un cuadro de diálogo para solicitar la nueva cantidad
        new_cantidad = simpledialog.askinteger("Editar articulo", "ingrese la nueva cantidad:", initialvalue=current_cantidad)

        if new_cantidad is not None:
            try:
                conn = sqlite3.connect(self.db_name)
                c = conn.cursor()
                
                c.execute("SELECT precio, costo, stock FROM articulos WHERE articulo=?", (current_producto,))
                resultado = c.fetchone()

                if resultado is None:
                    messagebox.showerror("Error", "Producto no encontrado.")
                    conn.close()
                    return

                precio, costo, stock = resultado

    # Valida que la nueva cantidad no supere el stock disponible en almacén
                if new_cantidad > stock:
                    messagebox.showerror("Error", f"Stock insuficiente. Solo hay {stock} unidades disponibles")
                    conn.close()
                    return

                total = precio * new_cantidad
                total_cop = "{:,.0f}".format(total)

    # Actualiza visualmente la fila en el Treeview
                self.tre.item(selected_item[0], values=(self.numero_factura, self.entry_cliente.get(), current_producto, "{:,.0f}".format(precio), new_cantidad, total_cop))

                for idx, producto in enumerate(self.productos_seleccionados):
                    if producto[2] == current_producto:
                        self.productos_seleccionados[idx] = (self.numero_factura, self.entry_cliente.get(), current_producto, precio, new_cantidad, total_cop, costo)
                        break

                conn.close()
                self.calcular_precio_total()

            except sqlite3.Error as e:
                print("Error al editar el articulo: ", e)

    def ver_ventas_realizadas(self):
        """Abre una ventana emergente para consultar, visualizar y filtrar todas las ventas registradas en la base de datos."""
        try:
    # Conexión a la base de datos para recuperar el historial de ventas
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT * FROM ventas")
            ventas = c.fetchall()
            conn.close()

    # Configuración inicial de la ventana secundaria (Toplevel)
            ventana_ventas = tk.Toplevel(self)
            ventana_ventas.title("Ventas Realizadas")
            ventana_ventas.geometry("1100x650+120+20")
            ventana_ventas.configure(bg="#C6D9E3")
            ventana_ventas.resizable(False, False)
            ventana_ventas.transient(self.master)
            ventana_ventas.grab_set()
            ventana_ventas.focus_set()
            ventana_ventas.lift()

            def filtrar_ventas():
                """Filtra las ventas mostradas en la tabla según el número de factura y/o el nombre del cliente ingresados."""
                factura_a_buscar = entry_factura.get()
                cliente_a_buscar = entry_cliente.get()
                
    # Limpia los elementos actuales del Treeview antes de insertar los resultados filtrados
                for item in tree.get_children():
                    tree.delete(item)

    # Comprensión de lista para filtrar los registros de ventas según los criterios de búsqueda
                ventas_filtradas = [
                    venta for venta in ventas
                    if (str(venta[0]) == factura_a_buscar or not factura_a_buscar) and(venta[1].lower() == cliente_a_buscar.lower() or not cliente_a_buscar)
                ]

    # Itera sobre las ventas filtradas, da formato a precios/fechas y las inserta en la tabla
                for venta in ventas_filtradas:
                    venta = list(venta)
                    venta[3] = "{:,.0f}".format(venta[3])
                    venta[5] = "{:,.0f}".format(venta[5])
                    venta[6] = datetime.datetime.strptime(venta[6], "%Y-%m-%d").strftime("%d-%m-%Y")
                    tree.insert("", "end", values=venta)

    # Título principal de la ventana
            label_ventas_realizadas = tk.Label(ventana_ventas, text="Ventas realizadas", font="sans 26 bold", bg="#C6D9E3")
            label_ventas_realizadas.place(x=350, y=20)

            # Contenedor para los campos de filtro y el botón de búsqueda
            filtro_frame = tk.Frame(ventana_ventas, bg="#C6D9E3")
            filtro_frame.place(x=20, y=60, width=1060, height=60)

    # Etiqueta y campo de entrada para buscar por número de factura
            label_factura = tk.Label(filtro_frame, text="Numero de factura", bg="#C6D9E3", font="sans 14 bold")
            label_factura.place(x=10, y=15)

            entry_factura = ttk.Entry(filtro_frame, font="sans 14 bold")
            entry_factura.place(x=200, y=10, width=200, height=40)

    # Etiqueta y campo de entrada para buscar por cliente
            label_cliente = tk.Label(filtro_frame, text="Cliente", bg="#C6D9E3", font="sans 14 bold")
            label_cliente.place(x=420, y=15)

            entry_cliente = ttk.Entry(filtro_frame, font="sans 14 bold")
            entry_cliente.place(x=620, y=10, width=200, height=40)            

    # Boton para ejecutar la función de filtrado
            btn_filtrar = tk.Button(filtro_frame, text="Filtrar", font="sans 14 bold", command=filtrar_ventas)
            btn_filtrar.place(x=840, y=10)

    # Marco contenedor para la tabla (Treeview) y sus barras de desplazamiento
            tree_frame = tk.Frame(ventana_ventas, bg="white")
            tree_frame.place(x=20, y=130, width=1060, height=500)

            scrol_y = ttk.Scrollbar(tree_frame)
            scrol_y.pack(side=RIGHT, fill=Y)

            scrol_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL)
            scrol_x.pack(side=BOTTOM, fill=X)

    # Configuración de la tabla (Treeview) para mostrar el historial completo
            tree = ttk.Treeview(tree_frame, columns=("Factura", "Cliente", "Producto", "Precio", "Cantidad", "Total", "Fecha", "Hora"),  show="headings")    
            tree.pack(expand=True, fill=BOTH)

            scrol_y.config(command=tree.yview)
            scrol_x.config(command=tree.xview)

            # Definición de los encabezados de las columnas
            tree.heading("Factura", text="Factura")
            tree.heading("Cliente", text="Cliente")
            tree.heading("Producto", text="Producto")
            tree.heading("Precio", text="Precio")
            tree.heading("Cantidad", text="Cantidad")
            tree.heading("Total", text="Total")
            tree.heading("Fecha", text="Fecha")
            tree.heading("Hora", text="Hora")

    # Definición del ancho y alineación de las columnas de la tabla
            tree.column("Factura", width=60, anchor="center")
            tree.column("Cliente", width=120, anchor="center")
            tree.column("Producto", width=120, anchor="center")
            tree.column("Precio", width=80, anchor="center")
            tree.column("Cantidad", width=80, anchor="center")
            tree.column("Total", width=80, anchor="center")
            tree.column("Fecha", width=80, anchor="center")
            tree.column("Hora", width=80, anchor="center")

    # Carga inicial de todos los registros de ventas aplicando formato a precios y fechas
            for venta in ventas:
                venta = list(venta)
                venta[3] = "{:,.0f}".format(venta[3])
                venta[5] = "{:,.0f}".format(venta[5])
                venta[6] = datetime.datetime.strptime(venta[6], "%Y-%m-%d").strftime("%d-%m-%Y")
                tree.insert("", "end", values=venta)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al obtener las ventas: {e}")

    def generar_factura_pdf(self, total_venta, cliente):
        try:
        # Definir la ruta del archivo PDF y crear el lienzo (canvas)
            factura_path = f"factura/Factura_{self.numero_factura}.pdf"
            c = canvas.Canvas(factura_path, pagesize=letter)

        # Datos de la empresa emisora
            empresa_market = "S-MART"
            empresa_direccion = "Calle # 6, Candelaria - Zona Norte"
            empresa_telefono = "+591 7676-0597"
            empresa_email = "contacto@s-mart.com"
            empresa_website = "www.s-martbolivia.com"

        #  Encabezado principal del documento (Título centrado)
            c.setFont("Helvetica-Bold", 18)  
            c.drawCentredString(300, 750, "FACTURA DE SERVICIOS")  

        # Datos de la empresa en la parte superior izquierda
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 710, f"{empresa_market}")

            c.setFont("Helvetica", 12)
            c.drawString(50, 690, f"Dirección: {empresa_direccion}")
            c.drawString(50, 670, f"Teléfono: {empresa_telefono}")
            c.drawString(50, 650, f"Email: {empresa_email}")
            c.drawString(50, 630, f"Website: {empresa_website}")

        # Línea divisoria decorativa
            c.setLineWidth(0.5)
            c.setStrokeColor(colors.gray)
            c.line(50, 620, 550, 620)

        # Información de la factura (Número y Fecha actual)
            c.setFont("Helvetica", 12)
            c.drawString(50, 600, f"Número de factura: {self.numero_factura}")
            c.drawString(50, 580, f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Linea Horizontal separador    
            c.line(50, 550, 550, 550)

        # Datos del cliente
            c.drawString(50, 540, f"Cliente: {cliente}")
            c.drawString(50, 520, "Descripción de producto:")

        # Cabecera de la tabla de productos
            y_offset = 500
            c.setFont("Helvetica-Bold", 12)  
            c.drawString(70, y_offset, "Producto")
            c.drawString(270, y_offset, "Cantidad")
            c.drawString(370, y_offset, "Precio")
            c.drawString(470, y_offset, "Total")

        # Línea debajo de la cabecera de la tabla
            c.line(50, y_offset - 10, 550, y_offset - 10)
            y_offset -= 30

        # Iterar y rellenar los productos seleccionados en la tabla
            c.setFont("Helvetica", 12)
            for item in self.productos_seleccionados:
                factura, cliente, producto, precio, cantidad, total, costo = item
                c.drawString(70, y_offset, producto)
                c.drawString(270, y_offset, str(cantidad))
                c.drawString(370, y_offset, "Bs {:,.0f}".format(precio))
                c.drawString(470, y_offset, str(total))
                y_offset -= 20

        # Línea de cierre de la tabla
            c.line(50, y_offset, 550, y_offset)
            y_offset -= 20

            # 8. Monto total a pagar destacado
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(colors.darkblue)
            c.drawString(50, y_offset, f"Total a Pagar: Bs {total_venta:,.0f}")
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 12)

        # Mensaje de agradecimiento
            y_offset -= 30
            c.setFont("Helvetica-Bold", 12)  # Cambiamos a fuente en negrita y tamaño 12
            c.drawCentredString(300, y_offset, "¡Gracias por tu compra, vuelve pronto!")
        
        # Términos y condiciones al pie de página
            y_offset -= 60
            c.setFont("Helvetica", 10)
            c.drawString(50, y_offset, "Términos y Condiciones:")
            c.drawString(50, y_offset - 20, "1. Los productos comprados no tienen devolución.")
            c.drawString(50, y_offset - 40, "2. Conserve esta factura como comprobante de su compra.")
            c.drawString(50, y_offset - 60, "3. Para más información, visite nuestro sitio web o contacte a servicio al cliente.")

        # Guardar el documento PDF generado
            c.save()

            # Mostrar mensaje de éxito en pantalla y abrir el archivo automáticamente
            messagebox.showinfo("Factura generada", f"Se ha generado la factura en: {factura_path}")
            os.startfile(os.path.abspath(factura_path))

        except Exception as e:
            # Manejo de excepciones en caso de error imprevisto
            messagebox.showerror("Error", f"No se pudo generar la factura: {str(e)}")
   
    def widgets(self):
    # Marco contenedor superior para los campos de entrada y botones de control de ventas
        labelframe = tk.LabelFrame(self, font="sans 12 bold", bg="#C6D9E3")
        labelframe.place(x=25, y=30, width=1045, height=180)

    # Fila 1: Selección del cliente para la factura
        label_cliente = tk.Label(labelframe, text="Cliente: ", font="sans 14 bold", bg="#C6D9E3")
        label_cliente.place(x=10, y=11)
        self.entry_cliente = ttk.Combobox(labelframe, font="sans 14 bold")
        self.entry_cliente.place(x=120, y=8, width=260, height=40)

    # Fila 1: Selección del producto de inventario
        label_producto = tk.Label(labelframe, text="Producto: ", font="sans 14 bold", bg="#C6D9E3")
        label_producto.place(x=10, y=70)
        self.entry_producto = ttk.Combobox(labelframe, font="sans 14 bold")
        self.entry_producto.place(x=120, y=66, width=260, height=40)
        self.entry_producto.bind('<KeyRelease>', self.filtrar_productos)

    # Fila 2: Cantidad a vender del producto seleccionado
        label_cantidad = tk.Label(labelframe, text="Cantidad: ", font="sans 14 bold", bg="#C6D9E3")
        label_cantidad.place(x=400, y=11)
        self.entry_cantidad = ttk.Entry(labelframe, font="sans 14 bold")
        self.entry_cantidad.place(x=500, y=8, width=100, height=40)

    # Etiqueta informativa del stock disponible en almacen
        self.label_stock = tk.Label(labelframe, text="Stock: ", font="sans 14 bold", bg="#C6D9E3")
        self.label_stock.place(x=400, y=70)
        self.entry_producto.bind("<<ComboboxSelected>>", self.actualizar_stock)

    # Campo indicador del número de factura actual
        label_factura = tk.Label(labelframe, text="Numero de Factura:", font="sans 14 bold", bg="#C6D9E3")
        label_factura.place(x=630, y=11)

    # Indicamos el numero de factura actializada
        self.label_numero_factura = tk.Label(labelframe, text=f"{self.numero_factura}", font="sans 14 bold", bg="#C6D9E3")
        self.label_numero_factura.place(x=950, y=11)

    # Botones de acción inferior para la gestión del carrito o lista de ventas
        boton_agregar = tk.Button(labelframe, text="Agregar Articulo", font="sans 14 bold",command=self.agregar_articulo)
        boton_agregar.place(x=90, y=120, width=200, height=40) 

        boton_eliminar = tk.Button(labelframe, text="Eliminar Articulo", font="sans 14 bold", command=self.eliminar_articulo)
        boton_eliminar.place(x=310, y=120, width=200, height=40)

        boton_editar = tk.Button(labelframe, text="Editar Articulo", font="sans 14 bold", command=self.editar_articulo)
        boton_editar.place(x=530, y=120, width=200, height=40)

        boton_limpiar = tk.Button(labelframe, text="Limpiar lista", font="sans 14 bold", command=self.limpiar_listas)
        boton_limpiar.place(x=750, y=120, width=200, height=40)

    # Contenedor principal para la tabla (Treeview) de transacciones y sus barras de desplazamiento
        treFrame = tk.Frame(self, bg="white")
        treFrame.place(x=70, y=220, width=900, height=300)

        scrol_y = ttk.Scrollbar(treFrame)
        scrol_y.pack(side=RIGHT, fill=Y)

        scrol_x = ttk.Scrollbar(treFrame, orient=HORIZONTAL)
        scrol_x.pack(side=BOTTOM, fill=X)

    # inicialización del Treeview 
        self.tre = ttk.Treeview(treFrame, yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set, height=40, columns=("Factura", "Cliente", "Producto", "Precio", "Cantidad", "Total"), show="headings")
        self.tre.pack(expand=True, fill=BOTH)

        scrol_y.config(command=self.tre.yview)
        scrol_x.config(command=self.tre.xview)

    # Configuración de los títulos de los encabezados de la tabla
        self.tre.heading("Factura", text="Factura")
        self.tre.heading("Cliente", text="Cliente")
        self.tre.heading("Producto", text="Producto")
        self.tre.heading("Precio", text="Precio")
        self.tre.heading("Cantidad", text="Cantidad")
        self.tre.heading("Total", text="Total")

    # Configuración de las dimensiones y alineación de cada columna
        self.tre.column("Factura", width=70, anchor="center")
        self.tre.column("Cliente", width=250, anchor="center")
        self.tre.column("Producto", width=250, anchor="center")
        self.tre.column("Precio", width=120, anchor="center")
        self.tre.column("Cantidad", width=120, anchor="center")
        self.tre.column("Total", width=150, anchor="center")

        self.label_precio_total = tk.Label(self, text="Precio a Pagar: Bs 0 ",font="sans 18 bold", bg="#C6D9E3")
        self.label_precio_total.place(x=680, y=550)
    
    # Creacion de botones interactivos
        boton_pagar = tk.Button(self, text="Pagar", font="sans 14 bold", command=self.realizar_pago)
        boton_pagar.place(x=70, y=550, width=180, height=40)

        boton_ver_ventas = tk.Button(self, text="Ver Ventas Realizadas", font="sans 14 bold", command=self.ver_ventas_realizadas)
        boton_ver_ventas.place(x=290, y=550, width=280, height=40)