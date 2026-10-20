from decimal import Decimal, InvalidOperation
from tkinter import messagebox

from componentes.tabla.tabla_controller import TablaController
from componentes.tabla.tabla_model import TablaModel
from database.errores import (
    DatabaseError,
    RegistroNoEncontradoError,
    ValidacionError,
    mensaje_error_base_datos,
)


class InventarioController:
    """Controla las operaciones del módulo de Inventario."""

    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        self.codigo_seleccionado = None
        self.solo_lectura = False
        self.sugerencias_productos = []
        self.indice_producto = -1
        self.tabla_model = TablaModel(self.vista.tabla_inventario.columnas)
        self.tabla_controller = TablaController(
            self.tabla_model, self.vista.tabla_inventario
        )

        self.vista.btn_crear.configure(command=self.crear_producto)
        self.vista.btn_guardar.configure(command=self.registrar_producto)
        self.vista.btn_actualizar.configure(command=self.modificar_producto)
        self.vista.btn_activar.configure(
            command=lambda: self.cambiar_estado_producto(True)
        )
        self.vista.btn_desactivar.configure(
            command=lambda: self.cambiar_estado_producto(False)
        )

        self.vista.tabla_inventario.tabla.bind(
            "<ButtonRelease-1>", self.cargar_producto_seleccionado
        )
        self.vista.txt_buscar_producto.bind(
            "<KeyRelease>", self._buscar_producto
        )
        self.vista.txt_buscar_producto.bind(
            "<Down>", lambda _event: self._mover_sugerencia_producto(1)
        )
        self.vista.txt_buscar_producto.bind(
            "<Up>", lambda _event: self._mover_sugerencia_producto(-1)
        )
        self.vista.txt_buscar_producto.bind(
            "<Return>", self._confirmar_producto
        )

        self.actualizar_tabla()

    def actualizar_tabla(self):
        """Refresca las filas visibles en la tabla."""
        try:
            datos_tabla = self.modelo.obtener_todos()
            self.tabla_controller.cargar_datos(datos_tabla)
        except DatabaseError as error:
            messagebox.showerror("Error de base de datos", mensaje_error_base_datos(error))

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
        stock_minimo_texto = self.vista.txt_stock_minimo.obtener_texto().strip()
        try:
            stock_minimo = Decimal(stock_minimo_texto or "0")
        except InvalidOperation:
            raise ValidacionError("El stock mínimo debe ser numérico.") from None
        if not stock_minimo.is_finite() or stock_minimo < 0:
            raise ValidacionError("El stock mínimo debe ser no negativo.")
        return (
            codigo,
            nombre,
            precio,
            stock,
            stock_minimo,
            self.vista.txt_proveedor.obtener_texto().strip(),
            self.vista.txt_marca.obtener_texto().strip(),
            self.vista.txt_codigo_empresa.obtener_texto().strip(),
        )

    @staticmethod
    def _mostrar_error_bd(error):
        messagebox.showerror("Error de base de datos", mensaje_error_base_datos(error))

    @staticmethod
    def _es_tecla_de_navegacion(event):
        return event.keysym in {
            "Up",
            "Down",
            "Left",
            "Right",
            "Return",
            "Tab",
            "Escape",
            "Home",
            "End",
        }

    def _buscar_producto(self, event):
        if self._es_tecla_de_navegacion(event):
            return "break"
        texto = self.vista.txt_buscar_producto.obtener_texto().strip()
        if not texto:
            self.sugerencias_productos = []
            self.indice_producto = -1
            self.vista.ocultar_sugerencias_productos()
            return
        try:
            self.sugerencias_productos = self.modelo.buscar_sugerencias(texto, 6)
        except DatabaseError as error:
            self._mostrar_error_bd(error)
            return
        self.indice_producto = -1
        self.vista.mostrar_sugerencias_productos(
            self.sugerencias_productos, self.seleccionar_producto
        )

    def _mover_sugerencia_producto(self, direccion):
        if self.sugerencias_productos:
            if self.indice_producto < 0:
                self.indice_producto = (
                    0 if direccion > 0 else len(self.sugerencias_productos) - 1
                )
            else:
                self.indice_producto = (self.indice_producto + direccion) % len(
                    self.sugerencias_productos
                )
            self.vista.resaltar_sugerencia_producto(self.indice_producto)
        return "break"

    def _confirmar_producto(self, _event=None):
        if self.sugerencias_productos:
            indice = max(self.indice_producto, 0)
            self.seleccionar_producto(*self.sugerencias_productos[indice])
        return "break"

    def seleccionar_producto(self, codigo, nombre, precio, stock):
        """Carga en el formulario el producto elegido desde el autocompletado."""
        try:
            detalle = self.modelo.obtener_detalle_producto(codigo)
        except DatabaseError as error:
            self._mostrar_error_bd(error)
            return
        if detalle is None:
            messagebox.showwarning("Producto no encontrado", "El producto ya no existe.")
            return
        self.codigo_seleccionado = str(codigo)
        self.sugerencias_productos = []
        self.indice_producto = -1
        self.vista.txt_buscar_producto.establecer_texto(f"{codigo} - {nombre}")
        self.vista.ocultar_sugerencias_productos()
        if self.solo_lectura:
            return
        self.vista.mostrar_formulario()
        for entrada, valor in (
            (self.vista.txt_codigo, detalle[0]),
            (self.vista.txt_nombre, detalle[1]),
            (self.vista.txt_precio, detalle[2]),
            (self.vista.txt_stock, detalle[3]),
            (self.vista.txt_stock_minimo, detalle[4]),
            (self.vista.txt_proveedor, detalle[5]),
            (self.vista.txt_marca, detalle[6]),
            (self.vista.txt_codigo_empresa, detalle[7]),
        ):
            entrada.limpiar()
            entrada.establecer_texto(str(valor))

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
            if self.solo_lectura:
                return

            self.vista.mostrar_formulario()
            self.vista.txt_codigo.limpiar()
            self.vista.txt_codigo.establecer_texto(str(valores[0]))

            self.vista.txt_nombre.limpiar()
            self.vista.txt_nombre.establecer_texto(str(valores[1]))

            self.vista.txt_precio.limpiar()
            self.vista.txt_precio.establecer_texto(str(valores[2]))

            self.vista.txt_stock.limpiar()
            self.vista.txt_stock.establecer_texto(str(valores[3]))
            self.vista.txt_marca.limpiar()
            self.vista.txt_marca.establecer_texto(str(valores[4]))
            self.vista.txt_proveedor.limpiar()
            self.vista.txt_proveedor.establecer_texto(str(valores[5]))
            self.vista.txt_stock_minimo.limpiar()
            self.vista.txt_stock_minimo.establecer_texto(str(valores[6]))
            self.vista.txt_codigo_empresa.limpiar()
            self.vista.txt_codigo_empresa.establecer_texto(str(valores[7]))

    def crear_producto(self):
        """Muestra un formulario vacío para registrar un producto."""
        self.limpiar_formulario()
        self.vista.mostrar_formulario()

    def establecer_solo_lectura(self, solo_lectura: bool):
        """Configura los controles de Inventario para consulta sin escritura."""
        self.solo_lectura = solo_lectura
        self.vista.establecer_solo_lectura(solo_lectura)

    def registrar_producto(self):
        """Lee el formulario, guarda en el modelo y limpia las cajas."""
        try:
            (
                codigo,
                nombre,
                precio,
                stock,
                stock_minimo,
                proveedor,
                marca,
                codigo_empresa,
            ) = self._leer_datos_formulario()
            exito = self.modelo.agregar_producto(
                codigo,
                nombre,
                precio,
                stock,
                stock_minimo,
                proveedor,
                marca,
                codigo_empresa,
            )
        except ValidacionError as error:
            messagebox.showerror("Datos inválidos", str(error))
            return
        except DatabaseError as error:
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
            (
                nuevo_cod,
                nombre,
                precio,
                stock,
                stock_minimo,
                proveedor,
                marca,
                codigo_empresa,
            ) = self._leer_datos_formulario()
            exito = self.modelo.actualizar_producto(
                self.codigo_seleccionado,
                nuevo_cod,
                nombre,
                precio,
                stock,
                stock_minimo,
                proveedor,
                marca,
                codigo_empresa,
            )
        except ValidacionError as error:
            messagebox.showerror("Datos inválidos", str(error))
            return
        except RegistroNoEncontradoError as error:
            messagebox.showwarning("Producto no encontrado", str(error))
            self.limpiar_formulario()
            return
        except DatabaseError as error:
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

    def cambiar_estado_producto(self, activo: bool):
        """Activa o desactiva el producto actualmente seleccionado."""
        if not self.codigo_seleccionado:
            messagebox.showwarning(
                "Selecciona un producto",
                "Selecciona una fila antes de cambiar su estado.",
            )
            return

        try:
            exito = self.modelo.cambiar_estado_producto(
                self.codigo_seleccionado, activo
            )
        except DatabaseError as error:
            self._mostrar_error_bd(error)
            return
        if exito:
            self.actualizar_tabla()
            self.limpiar_formulario()
        else:
            messagebox.showwarning(
                "Estado sin cambios",
                "El producto ya tenía ese estado o no existe.",
            )

    def limpiar_formulario(self):
        """Limpia las cajas y borra la selección actual."""
        self.codigo_seleccionado = None
        self.vista.txt_codigo.limpiar()
        self.vista.txt_nombre.limpiar()
        self.vista.txt_precio.limpiar()
        self.vista.txt_stock.limpiar()
        self.vista.txt_stock_minimo.limpiar()
        self.vista.txt_proveedor.limpiar()
        self.vista.txt_marca.limpiar()
        self.vista.txt_codigo_empresa.limpiar()
        self.vista.ocultar_formulario()
