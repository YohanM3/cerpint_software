import sqlite3
from tkinter import messagebox

from componentes.tabla.tabla_controller import TablaController
from componentes.tabla.tabla_model import TablaModel
from database.errores import (
    RegistroNoEncontradoError,
    ValidacionError,
    mensaje_error_sqlite,
)


class ClientesController:
    """Controla las operaciones del módulo de Clientes."""

    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        self.documento_seleccionado = None
        self.tabla_model = TablaModel(self.vista.tabla_clientes.columnas)
        self.tabla_controller = TablaController(
            self.tabla_model, self.vista.tabla_clientes
        )

        # Conectar botones
        self.vista.btn_guardar.configure(command=self.registrar_cliente)
        self.vista.btn_actualizar.configure(command=self.modificar_cliente)
        self.vista.btn_eliminar.configure(command=self.eliminar_cliente)

        # Evento de clic en la tabla
        self.vista.tabla_clientes.tabla.bind(
            "<ButtonRelease-1>", self.cargar_cliente_seleccionado
        )

        # Cargar datos iniciales
        self.actualizar_tabla()

    def actualizar_tabla(self):
        """Refresca las filas visibles en la tabla."""
        try:
            datos_tabla = self.modelo.obtener_todos()
            self.tabla_controller.cargar_datos(datos_tabla)
        except sqlite3.Error as error:
            messagebox.showerror("Error de base de datos", mensaje_error_sqlite(error))

    def cargar_cliente_seleccionado(self, _event):
        """Carga los datos de la fila seleccionada en las cajas del formulario."""
        tabla = self.vista.tabla_clientes.tabla
        item_id = tabla.identify_row(_event.y)
        if not item_id:
            return

        tabla.selection_set(item_id)
        valores = tabla.item(item_id)["values"]
        if valores:
            self.documento_seleccionado = str(valores[0])

            self.vista.txt_documento.limpiar()
            self.vista.txt_documento.establecer_texto(str(valores[0]))

            self.vista.txt_nombre.limpiar()
            self.vista.txt_nombre.establecer_texto(str(valores[1]))

            self.vista.txt_telefono.limpiar()
            self.vista.txt_telefono.establecer_texto(str(valores[2]))

            self.vista.txt_direccion.limpiar()
            self.vista.txt_direccion.establecer_texto(str(valores[3]))

    def registrar_cliente(self):
        """Lee el formulario, guarda en el modelo y limpia las cajas."""
        doc = self.vista.txt_documento.obtener_texto()
        nombre = self.vista.txt_nombre.obtener_texto()
        tel = self.vista.txt_telefono.obtener_texto()
        dir_cli = self.vista.txt_direccion.obtener_texto()

        doc = doc.strip()
        nombre = nombre.strip()
        if not (doc and nombre):
            messagebox.showerror(
                "Datos incompletos", "Documento y nombre son obligatorios."
            )
            return

        try:
            exito = self.modelo.agregar_cliente(doc, nombre, tel, dir_cli)
        except ValidacionError as error:
            messagebox.showerror("Datos inválidos", str(error))
            return
        except sqlite3.Error as error:
            messagebox.showerror("Error de base de datos", mensaje_error_sqlite(error))
            return
        if not exito:
            messagebox.showwarning(
                "Atención",
                "Ya existe un cliente con ese documento. Verifica los datos antes de guardar.",
            )
            return

        self.actualizar_tabla()
        self.limpiar_formulario()

    def modificar_cliente(self):
        """Procesa la actualización del cliente seleccionado."""
        if not self.documento_seleccionado:
            messagebox.showwarning(
                "Selecciona un cliente", "Selecciona una fila antes de actualizar."
            )
            return

        doc = self.vista.txt_documento.obtener_texto()
        nombre = self.vista.txt_nombre.obtener_texto()
        tel = self.vista.txt_telefono.obtener_texto()
        direccion = self.vista.txt_direccion.obtener_texto()

        doc = doc.strip()
        nombre = nombre.strip()
        if not (doc and nombre):
            messagebox.showerror(
                "Datos incompletos", "Documento y nombre son obligatorios."
            )
            return

        try:
            exito = self.modelo.actualizar_cliente(
                self.documento_seleccionado, doc, nombre, tel, direccion
            )
        except ValidacionError as error:
            messagebox.showerror("Datos inválidos", str(error))
            return
        except RegistroNoEncontradoError as error:
            messagebox.showwarning("Cliente no encontrado", str(error))
            self.limpiar_formulario()
            return
        except sqlite3.Error as error:
            messagebox.showerror("Error de base de datos", mensaje_error_sqlite(error))
            return

        if not exito:
            messagebox.showwarning(
                "Atención",
                "Ese documento ya pertenece a otro cliente. Cambia el número antes de guardar.",
            )
            return

        self.actualizar_tabla()
        self.limpiar_formulario()

    def eliminar_cliente(self):
        """Elimina el cliente actualmente seleccionado."""
        if not self.documento_seleccionado:
            messagebox.showwarning(
                "Selecciona un cliente", "Selecciona una fila antes de eliminar."
            )
            return

        respuesta = messagebox.askyesno(
            "Confirmar",
            f"¿Deseas eliminar al cliente {self.documento_seleccionado}?",
        )
        if not respuesta:
            return

        try:
            exito = self.modelo.eliminar_cliente(self.documento_seleccionado)
        except sqlite3.Error as error:
            messagebox.showerror("Error de base de datos", mensaje_error_sqlite(error))
            return
        if exito:
            self.actualizar_tabla()
            self.limpiar_formulario()
        else:
            messagebox.showwarning("Cliente no encontrado", "El cliente ya no existe.")
            self.limpiar_formulario()

    def limpiar_formulario(self):
        """Limpia las cajas y borra la selección actual."""
        self.documento_seleccionado = None
        self.vista.txt_documento.limpiar()
        self.vista.txt_nombre.limpiar()
        self.vista.txt_telefono.limpiar()
        self.vista.txt_direccion.limpiar()
