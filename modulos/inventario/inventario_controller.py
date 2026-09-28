import sqlite3
from decimal import Decimal, InvalidOperation
from tkinter import messagebox

from componentes.tabla.tabla_controller import TablaController
from componentes.tabla.tabla_model import TablaModel
from database.errores import (
    RegistroNoEncontradoError,
    ValidacionError,
    mensaje_error_sqlite,
)


class InventarioController:
    """Controla las operaciones del módulo de Inventario."""

    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        self.codigo_seleccionado = None
        self.tabla_model = TablaModel(self.vista.tabla_inventario.columnas)
        self.tabla_controller = TablaController(
            self.tabla_model, self.vista.tabla_inventario
        )

        self.vista.btn_guardar.configure(command=self.registrar_producto)
        self.vista.btn_actualizar.configure(command=self.modificar_producto)
        self.vista.btn_eliminar.configure(command=self.eliminar_producto)

        self.vista.tabla_inventario.tabla.bind(
            "<ButtonRelease-1>", self.cargar_producto_seleccionado
        )

        self.actualizar_tabla()

    def actualizar_tabla(self):
        """Refresca las filas visibles en la tabla."""
        try:
            datos_tabla = self.modelo.obtener_todos()
            self.tabla_controller.cargar_datos(datos_tabla)
        except sqlite3.Error as error:
            messagebox.showerror("Error de base de datos", mensaje_error_sqlite(error))

    def _leer_datos_formulario(self):
        codigo = self.vista.txt_codigo.obtener_texto().strip()
        nombre = self.vista.txt_nombre.obtener_texto().strip()
        precio_texto = self.vista.txt_precio.obtener_texto().strip()
        stock_texto = self.vista.txt_stock.obtener_texto().strip()
        if not all((codigo, nombre, precio_texto, stock_texto)):
            raise ValidacionError("Completa código, nombre, precio y stock.")
        try:
            precio = Decimal(precio_texto)
            stock = int(stock_texto)
        except (InvalidOperation, ValueError):
            raise ValidacionError(
                "Precio o stock tienen un formato inválido."
            ) from None
        if not precio.is_finite() or precio < 0:
            raise ValidacionError("El precio debe ser un número finito no negativo.")
        if stock < 0:
            raise ValidacionError("El stock no puede ser negativo.")
        return codigo, nombre, precio, stock

    @staticmethod
    def _mostrar_error_bd(error):
        messagebox.showerror("Error de base de datos", mensaje_error_sqlite(error))

    def cargar_producto_seleccionado(self, _event):
        """Carga la fila seleccionada de la tabla en los campos de texto."""
        tabla = self.vista.tabla_inventario.tabla
        item_id = tabla.identify_row(_event.y)
        if not item_id:
            return

        tabla.selection_set(item_id)
        valores = tabla.item(item_id)["values"]
        if valores:
            self.codigo_seleccionado = str(valores[0])

            self.vista.txt_codigo.limpiar()
            self.vista.txt_codigo.establecer_texto(str(valores[0]))

            self.vista.txt_nombre.limpiar()
            self.vista.txt_nombre.establecer_texto(str(valores[1]))

            self.vista.txt_precio.limpiar()
            self.vista.txt_precio.establecer_texto(str(valores[2]))

            self.vista.txt_stock.limpiar()
            self.vista.txt_stock.establecer_texto(str(valores[3]))

    def registrar_producto(self):
        """Lee el formulario, guarda en el modelo y limpia las cajas."""
        try:
            codigo, nombre, precio, stock = self._leer_datos_formulario()
            exito = self.modelo.agregar_producto(codigo, nombre, precio, stock)
        except ValidacionError as error:
            messagebox.showerror("Datos inválidos", str(error))
            return
        except sqlite3.Error as error:
            self._mostrar_error_bd(error)
            return
        if not exito:
            messagebox.showwarning(
                "Atención",
                "Ya existe un producto con ese código. Verifica el código antes de guardar.",
            )
            return

        self.actualizar_tabla()
        self.limpiar_formulario()

    def modificar_producto(self):
        """Procesa la actualización del producto seleccionado."""
        if not self.codigo_seleccionado:
            messagebox.showwarning(
                "Selecciona un producto", "Selecciona una fila antes de actualizar."
            )
            return

        try:
            nuevo_cod, nombre, precio, stock = self._leer_datos_formulario()
            exito = self.modelo.actualizar_producto(
                self.codigo_seleccionado, nuevo_cod, nombre, precio, stock
            )
        except ValidacionError as error:
            messagebox.showerror("Datos inválidos", str(error))
            return
        except RegistroNoEncontradoError as error:
            messagebox.showwarning("Producto no encontrado", str(error))
            self.limpiar_formulario()
            return
        except sqlite3.Error as error:
            self._mostrar_error_bd(error)
            return

        if not exito:
            messagebox.showwarning(
                "Atención",
                "Ese código ya pertenece a otro producto. Cambia el código antes de guardar.",
            )
            return

        self.actualizar_tabla()
        self.limpiar_formulario()

    def eliminar_producto(self):
        """Elimina el producto actualmente seleccionado."""
        if not self.codigo_seleccionado:
            messagebox.showwarning(
                "Selecciona un producto", "Selecciona una fila antes de eliminar."
            )
            return

        respuesta = messagebox.askyesno(
            "Confirmar",
            f"¿Deseas eliminar el producto {self.codigo_seleccionado}?",
        )
        if not respuesta:
            return

        try:
            exito = self.modelo.eliminar_producto(self.codigo_seleccionado)
        except sqlite3.Error as error:
            self._mostrar_error_bd(error)
            return
        if exito:
            self.actualizar_tabla()
            self.limpiar_formulario()
        else:
            messagebox.showwarning(
                "Producto no encontrado", "El producto ya no existe."
            )
            self.limpiar_formulario()

    def limpiar_formulario(self):
        """Limpia las cajas y borra la selección actual."""
        self.codigo_seleccionado = None
        self.vista.txt_codigo.limpiar()
        self.vista.txt_nombre.limpiar()
        self.vista.txt_precio.limpiar()
        self.vista.txt_stock.limpiar()
