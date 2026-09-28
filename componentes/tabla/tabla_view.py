# componentes/tabla/tabla_view.py
import customtkinter as ctk
from tkinter import ttk


class TablaView(ctk.CTkFrame):
    """Maneja la representación visual de la tabla."""

    def __init__(self, master, columnas: list, **kwargs):
        super().__init__(master=master, **kwargs)

        # Guardamos columnas
        self.columnas = columnas

        # Creación del Treeview de Tkinter
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings")

        # Configurar encabezados
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=120, anchor="center")

        # Barra de desplazamiento vertical
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.tabla.yview
        )
        self.tabla.configure(yscrollcommand=self.scrollbar.set)

        # Empaquetado
        self.tabla.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def Insertar_filas(self, lista_filas: list):
        """Limpia e inserta nuevas filas en la pantalla."""
        self.limpiar_tabla()
        for fila in lista_filas:
            self.tabla.insert("", "end", values=fila)

    def limpiar_tabla(self):
        """Elimina todos los registros visibles."""
        for item in self.tabla.get_children():
            self.tabla.delete(item)
