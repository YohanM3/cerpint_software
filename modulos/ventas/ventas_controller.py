# modulos/ventas/ventas_controller.py

import os
import subprocess
import sys
from decimal import Decimal
from tkinter import filedialog, messagebox

from modulos.ventas.ventas_model import VentasModel
from servicios.pdf_service import PDFService


class VentasController:
    def __init__(self, modelo, vista, clientes_model=None, inventario_model=None):
        self.modelo = modelo
        self.vista = vista
        self.clientes_model = clientes_model
        self.inventario_model = inventario_model
        self.cliente_actual = None
        self.sugerencias_clientes = []
        self.indice_cliente = -1
        self.sugerencias_productos = []
        self.indice_producto = -1

        if hasattr(self.vista, "txt_cliente_buscar"):
            self.vista.txt_cliente_buscar.bind(
                "<KeyRelease>", self._al_escribir_cliente
            )
            self.vista.txt_cliente_buscar.bind(
                "<Down>", lambda _event: self._mover_sugerencia_cliente(1)
            )
            self.vista.txt_cliente_buscar.bind(
                "<Up>", lambda _event: self._mover_sugerencia_cliente(-1)
            )
            self.vista.txt_cliente_buscar.bind("<Return>", self._confirmar_cliente)

        if hasattr(self.vista, "txt_codigo"):
            self.vista.txt_codigo.bind("<KeyRelease>", self._al_escribir_producto)
            self.vista.txt_codigo.bind(
                "<Down>", lambda _event: self._mover_sugerencia_producto(1)
            )
            self.vista.txt_codigo.bind(
                "<Up>", lambda _event: self._mover_sugerencia_producto(-1)
            )
            self.vista.txt_codigo.bind("<Return>", self._confirmar_producto)

        if hasattr(self.vista, "txt_cantidad"):
            self.vista.txt_cantidad.bind("<Return>", self._agregar_producto_con_enter)

        if hasattr(self.vista, "btn_agregar"):
            self.vista.btn_agregar.configure(command=self.agregar_producto_desde_form)

        if hasattr(self.vista, "btn_cancelar"):
            self.vista.btn_cancelar.configure(command=self.vaciar_carrito)

        if hasattr(self.vista, "btn_quitar_item"):
            self.vista.btn_quitar_item.configure(command=self.quitar_item_seleccionado)

        if hasattr(self.vista, "btn_procesar"):
            self.vista.btn_procesar.configure(command=self.procesar_venta)

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

    def _al_escribir_cliente(self, event):
        if self._es_tecla_de_navegacion(event):
            return "break"
        self._buscar_cliente()

    def _al_escribir_producto(self, event):
        if self._es_tecla_de_navegacion(event):
            return "break"
        self._buscar_producto()

    def _buscar_cliente(self):
        if self.clientes_model is None:
            return
        texto = self.vista.txt_cliente_buscar.obtener_texto().strip()
        if not texto:
            self.sugerencias_clientes = []
            self.indice_cliente = -1
            self.vista.ocultar_sugerencias()
            self.vista.lbl_cliente_activo.configure(
                text="Cliente: (Ninguno seleccionado)",
                text_color="orange",
            )
            self.cliente_actual = None
            return
        self.sugerencias_clientes = self.clientes_model.buscar_sugerencias(texto, 5)
        self.indice_cliente = -1
        self.vista.mostrar_sugerencias(
            self.sugerencias_clientes, self.seleccionar_cliente
        )

    def _mover_sugerencia_cliente(self, direccion):
        if self.sugerencias_clientes:
            if self.indice_cliente < 0:
                self.indice_cliente = (
                    0 if direccion > 0 else len(self.sugerencias_clientes) - 1
                )
            else:
                self.indice_cliente = (self.indice_cliente + direccion) % len(
                    self.sugerencias_clientes
                )
            self.vista.resaltar_sugerencia_cliente(self.indice_cliente)
        return "break"

    def _confirmar_cliente(self, _event=None):
        if self.sugerencias_clientes:
            indice = max(self.indice_cliente, 0)
            self.seleccionar_cliente(*self.sugerencias_clientes[indice])
        return "break"

    def seleccionar_cliente(self, documento: str, nombre: str):
        self.cliente_actual = documento
        self.vista.txt_cliente_buscar.limpiar()
        self.vista.txt_cliente_buscar.insert(0, f"{documento} - {nombre}")
        self.vista.lbl_cliente_activo.configure(
            text=f"Cliente: {documento} - {nombre}",
            text_color="green",
        )
        self.vista.ocultar_sugerencias()
        self.sugerencias_clientes = []
        self.indice_cliente = -1
        if hasattr(self.vista, "desbloquear_articulos"):
            self.vista.desbloquear_articulos()
        if hasattr(self.vista, "txt_codigo"):
            self.vista.txt_codigo.focus_set()

    def _buscar_producto(self):
        if self.inventario_model is None:
            return
        texto = self.vista.txt_codigo.obtener_texto().strip()
        if not texto:
            self.sugerencias_productos = []
            self.indice_producto = -1
            self.vista.ocultar_sugerencias_productos()
            return
        self.sugerencias_productos = self.inventario_model.buscar_sugerencias(texto, 5)
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
            codigo, nombre, precio, _stock = self.sugerencias_productos[indice]
            self.seleccionar_producto(codigo, nombre, precio)
        return "break"

    def _agregar_producto_con_enter(self, _event=None):
        self.agregar_producto_desde_form()
        return "break"

    def seleccionar_producto(self, codigo: str, nombre: str, precio: float):
        self.vista.txt_codigo.limpiar()
        self.vista.txt_codigo.insert(0, codigo)
        self.vista.txt_nombre.configure(state="normal")
        self.vista.txt_nombre.limpiar()
        self.vista.txt_nombre.insert(0, nombre)
        self.vista.txt_nombre.configure(state="disabled")
        self.vista.txt_precio.configure(state="normal")
        self.vista.txt_precio.limpiar()
        self.vista.txt_precio.insert(0, f"{precio:.2f}")
        self.vista.txt_precio.configure(state="disabled")
        self.vista.ocultar_sugerencias_productos()
        if hasattr(self.vista, "txt_cantidad"):
            self.vista.txt_cantidad.focus_set()

    def agregar_producto_desde_form(self):
        codigo = self.vista.txt_codigo.obtener_texto().strip()
        cantidad_texto = self.vista.txt_cantidad.obtener_texto().strip()
        if not codigo or not cantidad_texto:
            messagebox.showwarning("Atención", "Completa el código y la cantidad.")
            return
        try:
            cantidad = int(cantidad_texto)
        except ValueError:
            messagebox.showwarning("Atención", "La cantidad debe ser un entero válido.")
            return

        try:
            producto = self.inventario_model.obtener_por_codigo_o_nombre(codigo)
            if producto is None:
                raise ValueError("El producto no existe en el inventario.")
            codigo_bd, nombre, precio, stock = producto
            cantidad_en_carrito = sum(
                item["cantidad"]
                for item in self.modelo.carrito
                if item["codigo"] == codigo_bd
            )
            disponible = max(0, stock - cantidad_en_carrito)
            if disponible == 0:
                raise ValueError(
                    "El producto está agotado o no tiene unidades disponibles."
                )
            if cantidad > disponible:
                raise ValueError(
                    f"Stock insuficiente: solo quedan {disponible} unidad(es) disponibles."
                )
            self.modelo.agregar_item(codigo_bd, nombre, cantidad, precio)
            self.vista.limpiar_formulario_articulo()
            self._actualizar_tabla_venta()
            self.vista.txt_codigo.focus_set()
        except Exception as error:
            messagebox.showwarning("Atención", str(error))

    def _actualizar_tabla_venta(self):
        if hasattr(self.vista, "tabla_ventas"):
            self.vista.tabla_ventas.limpiar_tabla()
            for fila in self.modelo.obtener_items_tabla():
                self.vista.tabla_ventas.tabla.insert("", "end", values=fila)
        if hasattr(self.vista, "lbl_total"):
            total = self.modelo.calcular_total()
            self.vista.lbl_total.configure(text=f"Total: ${float(total):.2f}")

    def vaciar_carrito(self):
        self.modelo.vaciar_carrito()
        self._actualizar_tabla_venta()
        if hasattr(self.vista, "limpiar_formulario_venta"):
            self.vista.limpiar_formulario_venta()
        if hasattr(self.vista, "menu_estado_pago"):
            self.vista.menu_estado_pago.set("A Credito")
        if hasattr(self.vista, "restablecer_dias_credito"):
            self.vista.restablecer_dias_credito()

    def eliminar_item_pedido(self, codigo: str):
        if not codigo:
            return
        if self.modelo.eliminar_item(codigo):
            self._actualizar_tabla_venta()
        if hasattr(self.vista, "limpiar_formulario_articulo"):
            self.vista.limpiar_formulario_articulo()
        if hasattr(self.vista, "seleccionado"):
            self.vista.seleccionado = None

    def quitar_item_seleccionado(self):
        codigo = getattr(self.vista, "seleccionado", None)
        if not codigo:
            messagebox.showwarning(
                "Atención", "Selecciona un producto de la tabla para quitarlo."
            )
            return

        nombre = None
        for item in self.modelo.carrito:
            if item["codigo"] == codigo:
                nombre = item["producto"]
                break

        if nombre:
            confirmacion = messagebox.askyesno(
                "Confirmar",
                f"¿Deseas quitar el producto '{nombre}' del pedido?",
            )
            if not confirmacion:
                return

        self.eliminar_item_pedido(codigo)

    def limpiar_nuevo_pedido(self):
        self.cliente_actual = None
        if hasattr(self.vista, "txt_cliente_buscar"):
            self.vista.txt_cliente_buscar.limpiar()
        if hasattr(self.vista, "lbl_cliente_activo"):
            self.vista.lbl_cliente_activo.configure(
                text="Cliente: (Ninguno seleccionado)",
                text_color="orange",
            )
        if hasattr(self.vista, "limpiar_formulario_articulo"):
            self.vista.limpiar_formulario_articulo()
        if hasattr(self.vista, "limpiar_formulario_venta"):
            self.vista.limpiar_formulario_venta()
        if hasattr(self.vista, "tabla_ventas"):
            self.vista.tabla_ventas.limpiar_tabla()
        if hasattr(self.vista, "lbl_total"):
            self.vista.lbl_total.configure(text="Total: $0.00")
        if hasattr(self.modelo, "vaciar_carrito"):
            self.modelo.vaciar_carrito()
        if hasattr(self.vista, "menu_estado_pago"):
            self.vista.menu_estado_pago.set("A Credito")
        if hasattr(self.vista, "restablecer_dias_credito"):
            self.vista.restablecer_dias_credito()

    def procesar_venta(self):
        if not self.cliente_actual:
            messagebox.showwarning(
                "Atención", "Seleccione un cliente para realizar la nota."
            )
            return
        if not self.modelo.carrito:
            messagebox.showwarning("Atención", "El carrito de ventas está vacío.")
            return
        try:
            selector_estado = getattr(self.vista, "menu_estado_pago", None)
            estado_pago = (
                selector_estado.get()
                if selector_estado is not None
                and callable(getattr(selector_estado, "get", None))
                else "Pagado"
            )
            campo_dias_credito = getattr(self.vista, "txt_dias_credito", None)
            dias_credito = (
                campo_dias_credito.obtener_texto()
                if campo_dias_credito is not None
                else 30
            )
            venta_id, cliente_data, items_proc, total_proc = (
                self.modelo.procesar_venta_bd(
                    self.cliente_actual,
                    estado=estado_pago,
                    dias_credito=dias_credito,
                )
            )
            if venta_id is None:
                return None

            parent_widget = None
            if hasattr(self.vista, "winfo_toplevel"):
                try:
                    parent_widget = self.vista.winfo_toplevel()
                except Exception:
                    parent_widget = None

            resultado = self.procesar_y_generar_pdf(
                self.cliente_actual,
                items_proc,
                total_proc,
                parent_widget=parent_widget,
                venta_id=venta_id,
                cliente_data=cliente_data,
            )
            self.limpiar_nuevo_pedido()
            return resultado
        except Exception as error:
            messagebox.showerror("Error en Venta", str(error))
            return None

    @staticmethod
    def _normalizar_item_pdf(item):
        nombre = item.get("nombre")
        if nombre is None:
            nombre = item.get("producto", "")
        return {
            "codigo": item.get("codigo", ""),
            "nombre": nombre,
            "cantidad": item.get("cantidad", 0),
            "precio": Decimal(str(item.get("precio", 0))),
            "subtotal": Decimal(str(item.get("subtotal", 0))),
        }

    @staticmethod
    def procesar_y_generar_pdf(
        cliente_id,
        items,
        total,
        parent_widget=None,
        venta_id=None,
        cliente_data=None,
    ):
        if not cliente_id:
            messagebox.showerror(
                "Error", "Debe seleccionar un cliente.", parent=parent_widget
            )
            return False
        if not items:
            messagebox.showerror(
                "Error", "El carrito está vacío.", parent=parent_widget
            )
            return False
        try:
            if venta_id is None or cliente_data is None:
                modelo = VentasModel()
                modelo.carrito = [
                    {
                        "codigo": item.get("codigo", ""),
                        "producto": item.get("nombre") or item.get("producto", ""),
                        "cantidad": item.get("cantidad", 0),
                        "precio": Decimal(str(item.get("precio", 0))),
                        "subtotal": Decimal(str(item.get("subtotal", 0))),
                    }
                    for item in items
                ]
                venta_id, cliente_data, items_proc, total_proc = (
                    modelo.procesar_venta_bd(cliente_id)
                )
            else:
                items_proc = [
                    VentasController._normalizar_item_pdf(item) for item in items
                ]
                total_proc = total

            items_pdf = [
                {
                    "codigo": item["codigo"],
                    "nombre": item.get("nombre") or item.get("producto", ""),
                    "cantidad": item["cantidad"],
                    "precio": float(item["precio"]),
                    "subtotal": float(item["subtotal"]),
                }
                for item in items_proc
            ]

            nombre_sugerido = f"Nota_Entrega_{venta_id:05d}.pdf"
            filepath = filedialog.asksaveasfilename(
                title="Guardar Nota de Entrega",
                initialfile=nombre_sugerido,
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf")],
            )
            if not filepath:
                messagebox.showwarning(
                    "Atención",
                    "La venta fue registrada pero el PDF no se guardó.",
                    parent=parent_widget,
                )
                return True
            PDFService.generar_nota_entrega(
                filepath, venta_id, cliente_data, items_pdf, total_proc
            )
            if sys.platform == "win32":
                os.startfile(filepath)
            elif sys.platform == "darwin":
                subprocess.run(["open", filepath])
            else:
                subprocess.run(["xdg-open", filepath])
            messagebox.showinfo(
                "Éxito",
                f"Nota de Entrega Nº {venta_id:05d} registrada y emitida correctamente.",
                parent=parent_widget,
            )
            return True
        except Exception as e:
            messagebox.showerror("Error en Venta", str(e), parent=parent_widget)
            return False

    @staticmethod
    def consultar_historial_cliente(cliente_id):
        return VentasModel.obtener_ventas_por_cliente(cliente_id)

    @staticmethod
    def obtener_detalle_nota(venta_id):
        return VentasModel.obtener_detalle_venta(venta_id)
