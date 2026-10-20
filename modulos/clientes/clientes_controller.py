from tkinter import messagebox

from componentes.tabla.tabla_controller import TablaController
from componentes.tabla.tabla_model import TablaModel
from database.errores import (
    DatabaseError,
    RegistroNoEncontradoError,
    ValidacionError,
    mensaje_error_base_datos,
)


class ClientesController:
    """Controla las operaciones del módulo de Clientes."""

    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        self.documento_seleccionado = None
        self.solo_lectura = False
        self.clientes = []
        self.tabla_model = TablaModel(self.vista.tabla_clientes.columnas)
        self.tabla_controller = TablaController(
            self.tabla_model, self.vista.tabla_clientes
        )

        self.vista.btn_crear.configure(command=self.crear_cliente)
        self.vista.btn_guardar.configure(command=self.registrar_cliente)
        self.vista.btn_actualizar.configure(command=self.modificar_cliente)
        self.vista.btn_activar.configure(
            command=lambda: self.cambiar_estado_cliente(True)
        )
        self.vista.btn_desactivar.configure(
            command=lambda: self.cambiar_estado_cliente(False)
        )

        self.vista.tabla_clientes.tabla.bind(
            "<ButtonRelease-1>", self.cargar_cliente_seleccionado
        )
        self.vista.txt_busqueda.bind("<KeyRelease>", self.filtrar_clientes)

        self.actualizar_tabla()

    def actualizar_tabla(self):
        """Refresca las filas visibles en la tabla."""
        try:
            self.clientes = self.modelo.obtener_todos()
            self.filtrar_clientes()
        except DatabaseError as error:
            messagebox.showerror("Error de base de datos", mensaje_error_base_datos(error))

    def filtrar_clientes(self, _evento=None):
        """Filtra el listado por documento, nombre, teléfono o dirección."""
        filtro = self.vista.txt_busqueda.obtener_texto().strip().casefold()
        datos = [
            cliente
            for cliente in self.clientes
            if not filtro or filtro in " ".join(map(str, cliente)).casefold()
        ]
        self.tabla_controller.cargar_datos(datos)

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
            activo = str(valores[4]) == "Activo"
            self.vista.btn_activar.configure(
                state="disabled" if activo or self.solo_lectura else "normal"
            )
            self.vista.btn_desactivar.configure(
                state="disabled" if not activo or self.solo_lectura else "normal"
            )
            if self.solo_lectura:
                return

            self.vista.mostrar_formulario()
            self.vista.txt_documento.limpiar()
            self.vista.txt_documento.establecer_texto(str(valores[0]))

            self.vista.txt_nombre.limpiar()
            self.vista.txt_nombre.establecer_texto(str(valores[1]))

            self.vista.txt_telefono.limpiar()
            self.vista.txt_telefono.establecer_texto(str(valores[2]))

            self.vista.txt_direccion.limpiar()
            self.vista.txt_direccion.establecer_texto(str(valores[3]))

    def crear_cliente(self):
        """Muestra un formulario vacío para registrar un cliente."""
        self.limpiar_formulario()
        self.vista.mostrar_formulario()

    def establecer_solo_lectura(self, solo_lectura: bool):
        """Configura los controles de Clientes para consulta sin escritura."""
        self.solo_lectura = solo_lectura
        self.vista.establecer_solo_lectura(solo_lectura)

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
        except DatabaseError as error:
            messagebox.showerror("Error de base de datos", mensaje_error_base_datos(error))
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
        except DatabaseError as error:
            messagebox.showerror("Error de base de datos", mensaje_error_base_datos(error))
            return

        if not exito:
            messagebox.showwarning(
                "Atención",
                "Ese documento ya pertenece a otro cliente. Cambia el número antes de guardar.",
            )
            return

        self.actualizar_tabla()
        self.limpiar_formulario()

    def cambiar_estado_cliente(self, activo: bool):
        """Activa o desactiva el cliente seleccionado sin eliminarlo."""
        if not self.documento_seleccionado:
            messagebox.showwarning(
                "Selecciona un cliente", "Selecciona una fila antes de cambiar su estado."
            )
            return

        accion = "activar" if activo else "desactivar"
        respuesta = messagebox.askyesno(
            "Confirmar",
            f"¿Deseas {accion} al cliente {self.documento_seleccionado}?",
        )
        if not respuesta:
            return

        try:
            exito = self.modelo.cambiar_estado_cliente(
                self.documento_seleccionado, activo
            )
        except DatabaseError as error:
            messagebox.showerror("Error de base de datos", mensaje_error_base_datos(error))
            return
        if exito:
            self.actualizar_tabla()
            self.limpiar_formulario()
        else:
            messagebox.showwarning(
                "Estado sin cambios",
                "El cliente no existe o ya tiene ese estado.",
            )
            self.limpiar_formulario()

    def limpiar_formulario(self):
        """Limpia las cajas y borra la selección actual."""
        self.documento_seleccionado = None
        self.vista.btn_activar.configure(state="disabled")
        self.vista.btn_desactivar.configure(state="disabled")
        self.vista.txt_documento.limpiar()
        self.vista.txt_nombre.limpiar()
        self.vista.txt_telefono.limpiar()
        self.vista.txt_direccion.limpiar()
        self.vista.ocultar_formulario()
