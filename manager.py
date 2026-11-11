from tkinter import *
from tkinter import ttk
from login import Login
from login import Registro
from container import Container
import sys
import os

class Manager(Tk):
    def __init__(self, *args, **kwagrs):
        super().__init__(*args, **kwagrs)

        # Configuracion inicial de la ventana principal
        self.title("Mini Market Tkinter")
        self.geometry("1100x650+120+20")
        
        # resizable(False, False) bloquea el cambio de tamaño de la ventana (ancho y alto)
        self.resizable(False, False) 

        # Contenedor principal que agrupara y albergara a las distintas pantallas/frames
        container = Frame(self)
        container.pack(side=TOP, fill=BOTH, expand=True)
        container.configure(bg="#2B0531") # Color de fondo del contenedor principal

        # Diccionario para almacenar las digerentes vistas de la aplicacion
        self.frames = {}

        # Iteramos sobre las clases de las vistas para inicializarlas y guardarlas
        for i in (Login, Registro, Container):
            frame = i(container, self)
            self.frames[i] = frame

        # Mostramos la pantalla de inicio de sesion por defecto al arrancar
        self.show_frame(Container)
        # Configuracion de estilos visuales modernos para los widgets de ttk
        self.style = ttk.Style()
        self.style.theme_use("clam")

    def show_frame(self, container):
        """
        Metodo para traer al frente el frame que se le indique por parametro
        """
        frame = self.frames[container]
        frame.tkraise()

def main():
    """
    Funcion principal que instancia la aplicacion y arranca el bucle de eventos
    """
    app = Manager()
    app.mainloop()

if __name__ == "__main__":
    main()    