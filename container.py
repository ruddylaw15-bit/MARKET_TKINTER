from tkinter import *
import tkinter as tk 
from ventas import Ventas
from inventario import Inventario
from clientes import Clientes
from pedidos import Pedidos
from proveedor import Proveedor
from informacion import Informacion
import sys 
import os

class Container(tk.Frame):
    """
    Clase que actúa como contenedor principal de las vistas internas 
    (Ventas, Inventario, Clientes, etc.) y la barra de navegación.
    """
    def __init__(self, padre, controlador):

        # Llamamos al constructor de nuestro contenedor
        super().__init__(padre)


        self.controlador = controlador
        self.pack()
        # Posicionamos el contenedor dentro de la ventana principal
        self.place(x=0, y=0, width=1100, height=650)
        
        # Inicializamos los elementos visuales (botones de menú, etc.)
        self.widgets()
        
        self.frames = {}
        self.buttons = []
        
        # Iteramos sobre las vistas secundarias para inicializarlas
        for i in (Ventas, Inventario, Clientes, Pedidos, Proveedor, Informacion):
            frame = i(self)
            self.frames[i] = frame
            frame.pack()
            # Configuramos el diseño visual de cada frame secundario
            frame.config(bg="#C6D9E3", highlightbackground="gray", highlightthickness=1)
            
            # Ubicamos el frame debajo de la barra de navegación (dejando 40px arriba)
            frame.place(x=0, y=40, width=1100, height=610)
            
        # Mostramos la vista de Ventas por defecto al cargar el contenedor
        self.show_frame(Ventas)

    # Creamos un método para mostrar la sección que el usuario seleccione.
    # Recibe como parámetro la clase de la sección que queremos mostrar.
    def show_frame(self, container):
        frame = self.frames[container]
        frame.tkraise()

    def ventas(self):
        self.show_frame(Ventas) 

    def inventario(self):
        self.show_frame(Inventario) 

    def clientes(self):
        self.show_frame(Clientes) 

    def pedidos(self):
        self.show_frame(Pedidos) 

    def proveedor(self):
        self.show_frame(Proveedor) 

    def informacion(self):
        self.show_frame(Informacion) 

    def widgets(self):
        """
        Método reservado para colocar los botones del menú superior o navegacion
        """
        # Creamos un Frame secundario.
        # Este servirá como contenedor de todos los botones del menú
        frame2 = tk.Frame(self, bg="#C6D9E3")
        # Posicionamos el menú en la parte superior del contenedo
        frame2.place(x=0, y=0, width=1100, height=40)

        self.btn_ventas = Button(frame2, fg="black", text="Ventas", font="sans 16 bold", command=self.ventas)
        self.btn_ventas.place(x=0, y=0, width=184, height=40)

        self.btn_inventario = Button(frame2, fg="black", text="Inventario", font="sans 16 bold", command=self.inventario)
        self.btn_inventario.place(x=184, y=0, width=184, height=40)

        self.btn_clientes = Button(frame2, fg="black", text="Clientes", font="sans 16 bold", command=self.clientes)
        self.btn_clientes.place(x=369, y=0, width=184, height=40)

        self.btn_pedidos = Button(frame2, fg="black", text="Pedidos", font="sans 16 bold", command=self.pedidos)
        self.btn_pedidos.place(x=554, y=0, width=184, height=40)

        self.btn_proveedor = Button(frame2, fg="black", text="Proveedor", font="sans 16 bold", command=self.proveedor)
        self.btn_proveedor.place(x=739, y=0, width=184, height=40)

        self.btn_informacion = Button(frame2, fg="black", text="Información", font="sans 16 bold", command=self.informacion)
        self.btn_informacion.place(x=922, y=0, width=184, height=40)

        self.button = [self.btn_ventas, self.btn_inventario, self.btn_clientes, self.btn_pedidos, self.btn_proveedor, self.btn_informacion]