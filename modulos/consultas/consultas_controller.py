import os
import sys
import subprocess
from tkinter import filedialog, messagebox, simpledialog

from database.errores import DatabaseError
from modulos.clientes.clientes_model import ClientesModel
from modulos.consultas.consultas_model import ConsultasModel
from servicios.pdf_service import PDFService


class ConsultasController:
    """Controla la lógica de reportes y consultas."""

    def __init__(self, modelo, vista, clientes_model=None, solo_lectura=False):
        self.modelo = modelo
        self.vista = vista
        self.clientes_model = clientes_model or ClientesModel()
        self.solo_lectura = solo_lectura
        self.sugerencias_cliente = []
        self.indice_cliente = -1
        self.cliente_seleccionado = None
        self.consulta_actual = "pendientes"

        self.vista.btn_pendientes.configure(command=self.mostrar_notas_pendientes)
        self.vista.btn_periodo.configure(command=self.consultar_periodo)
        self.vista.btn_cliente.configure(command=self.consultar_notas_cliente)
        boton_bajo_stock = getattr(self.vista, "btn_bajo_stock", None)
        if boton_bajo_stock is None:
            boton_bajo_stock = self.vista.btn_reposicion
        boton_bajo_stock.configure(command=self.consultar_bajo_stock)
        for atributo, consulta in (
            ("btn_sin_movimiento", self.consultar_sin_movimiento),
            ("btn_proveedor", self.consultar_por_proveedor),
            ("btn_marca", self.consultar_por_marca),
        ):
            boton = getattr(self.vista, atributo, None)
            if boton is not None:
                boton.configure(command=consulta)
        self.vista.btn_imprimir.configure(command=self.imprimir_resultado_actual)
        self.vista.btn_cambiar_pago.configure(
            command=self.cambiar_pago_nota_seleccionada
        )
        self.vista.btn_anular_nota.configure(command=self.anular_nota_seleccionada)
        self.vista.tabla_reportes.tabla.bind(
            "<<TreeviewSelect>>", self.actualizar_acciones_nota
        )
        self.vista.txt_cliente.bind("<KeyRelease>", self._al_escribir_cliente)
        self.vista.txt_cliente.bind(
            "<Down>", lambda _event: self._mover_sugerencia_cliente(1)
        )
        self.vista.txt_cliente.bind(
            "<Up>", lambda _event: self._mover_sugerencia_cliente(-1)
        )
        self.vista.txt_cliente.bind("<Return>", self._confirmar_cliente)
        self.vista.txt_fecha_inicio.bind(
            "<Return>", lambda _event: self.consultar_periodo()
        )
        self.vista.txt_fecha_fin.bind(
            "<Return>", lambda _event: self.consultar_periodo()
        )
        self.vista.txt_dias_analisis.bind(
            "<Return>", lambda _event: self.consultar_sin_movimiento()
        )
        for atributo, consulta in (
            ("txt_proveedor", self.consultar_por_proveedor),
            ("txt_marca", self.consultar_por_marca),
        ):
            entrada = getattr(self.vista, atributo, None)
            if entrada is not None:
                entrada.bind("<Return>", lambda _event, accion=consulta: accion())
        self.establecer_solo_lectura(solo_lectura)
        self.consultar_notas_pendientes()

    def establecer_solo_lectura(self, solo_lectura):
        """Restringe las acciones que cambian el estado de una nota."""
        self.solo_lectura = solo_lectura
        if solo_lectura:
            self.vista.btn_cambiar_pago.cambiar_estado(False)
            self.vista.btn_anular_nota.cambiar_estado(False)

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
        texto = self.vista.txt_cliente.obtener_texto().strip()
        self.cliente_seleccionado = None
        self.indice_cliente = -1
        if not texto:
            self.sugerencias_cliente = []
            self.vista.ocultar_sugerencias_clientes()
            return
        try:
            self.sugerencias_cliente = self.clientes_model.buscar_sugerencias(texto, 6)
        except DatabaseError as error:
            messagebox.showerror("Error de base de datos", str(error))
            return
        self.vista.mostrar_sugerencias_clientes(
            self.sugerencias_cliente, self.seleccionar_cliente
        )

    def _mover_sugerencia_cliente(self, direccion):
        if self.sugerencias_cliente:
            if self.indice_cliente < 0:
                self.indice_cliente = (
                    0 if direccion > 0 else len(self.sugerencias_cliente) - 1
                )
            else:
                self.indice_cliente = (self.indice_cliente + direccion) % len(
                    self.sugerencias_cliente
                )
            self.vista.resaltar_sugerencia_cliente(self.indice_cliente)
        return "break"

    def _confirmar_cliente(self, _event=None):
        if self.sugerencias_cliente:
            indice = max(self.indice_cliente, 0)
            self.seleccionar_cliente(*self.sugerencias_cliente[indice])
        return "break"

    def seleccionar_cliente(self, documento, nombre):
        self.cliente_seleccionado = documento
        self.sugerencias_cliente = []
        self.indice_cliente = -1
        self.vista.txt_cliente.establecer_texto(documento)
        self.vista.ocultar_sugerencias_clientes()
        self.consultar_notas_cliente()

    def mostrar_notas_pendientes(self):
        self.vista.txt_cliente.limpiar()
        self.vista.txt_fecha_inicio.limpiar()
        self.vista.txt_fecha_fin.limpiar()
        self.vista.ocultar_sugerencias_clientes()
        self.cliente_seleccionado = None
        self.sugerencias_cliente = []
        self.indice_cliente = -1
        self.consultar_notas_pendientes()

    def _nota_seleccionada(self):
        tabla = self.vista.tabla_reportes.tabla
        seleccion = tabla.selection()
        columnas = list(self.vista.tabla_reportes.columnas)
        if not seleccion or "ID" not in columnas:
            return None
        valores = tabla.item(seleccion[0], "values")
        try:
            venta_id = int(valores[columnas.index("ID")])
        except (TypeError, ValueError):
            return None
        return venta_id, dict(zip(columnas, valores))

    def actualizar_acciones_nota(self, _event=None):
        nota = self._nota_seleccionada()
        activo = (
            not self.solo_lectura
            and nota is not None
            and nota[1].get("Registro", "Activa") != "Anulada"
        )
        self.vista.btn_cambiar_pago.cambiar_estado(activo)
        self.vista.btn_anular_nota.cambiar_estado(activo)
        if activo:
            texto_boton = (
                "Revertir pago"
                if nota[1].get("Situación") == "Pagada"
                else "Marcar como pagada"
            )
            self.vista.btn_cambiar_pago.actualizar_texto(texto_boton)
        return "break"

    def cambiar_pago_nota_seleccionada(self):
        if self.solo_lectura:
            messagebox.showwarning(
                "Acceso restringido", "El consultor solo puede consultar."
            )
            return
        nota = self._nota_seleccionada()
        if nota is None or nota[1].get("Registro", "Activa") == "Anulada":
            messagebox.showwarning("Atención", "Selecciona una nota activa.")
            return
        venta_id, datos = nota
        esta_pagada = datos.get("Situación") == "Pagada"
        if esta_pagada:
            try:
                dias_credito = int(datos.get("Días crédito", 0) or 0)
            except (TypeError, ValueError):
                dias_credito = 0
            if dias_credito == 0:
                detalle = (
                    "Al revertir este contado, la nota quedará vencida de inmediato."
                )
            else:
                detalle = (
                    "La nota volverá a vigente o vencida según su vencimiento original."
                )
            pregunta = f"¿Revertir el pago de la nota Nº {venta_id:05d}?\n\n{detalle}"
        else:
            pregunta = f"¿Marcar la nota Nº {venta_id:05d} como pagada?"

        if not messagebox.askyesno("Confirmar pago", pregunta):
            return

        try:
            nuevo_estado = self.modelo.alternar_pago_nota(venta_id)
        except (ValueError, RuntimeError, DatabaseError) as error:
            messagebox.showerror("Error", str(error))
            return
        mensaje = (
            "La nota quedó pagada."
            if nuevo_estado == "Pagado"
            else "Se revirtió el pago y la nota volvió a la cuenta por cobrar."
        )
        messagebox.showinfo("Nota actualizada", mensaje)
        self._refrescar_consulta_actual()

    def anular_nota_seleccionada(self):
        if self.solo_lectura:
            messagebox.showwarning(
                "Acceso restringido", "El consultor solo puede consultar."
            )
            return
        nota = self._nota_seleccionada()
        if nota is None or nota[1].get("Registro", "Activa") == "Anulada":
            messagebox.showwarning(
                "Atención", "Selecciona una nota activa para anular."
            )
            return
        venta_id, datos = nota
        motivo = simpledialog.askstring(
            "Motivo de anulación",
            f"Indica el motivo para anular la nota Nº {venta_id:05d}:",
            parent=self.vista.winfo_toplevel(),
        )
        if not motivo or not motivo.strip():
            return

        aviso_pago = (
            "La nota figura pagada. El sistema repondrá el inventario, pero el reembolso "
            "de dinero no quedará registrado.\n\n"
            if datos.get("Situación") == "Pagada"
            else ""
        )
        if not messagebox.askyesno(
            "Confirmar anulación",
            f"{aviso_pago}¿Anular la nota Nº {venta_id:05d} y reponer todo su inventario?",
            parent=self.vista.winfo_toplevel(),
        ):
            return

        try:
            anulada = self.modelo.anular_venta(venta_id, motivo)
        except (ValueError, RuntimeError, DatabaseError) as error:
            messagebox.showerror("Error", str(error))
            return
        if not anulada:
            messagebox.showinfo("Información", "La nota ya estaba anulada.")
            return
        messagebox.showinfo(
            "Nota anulada",
            "La nota se conservó en el historial con su motivo y se repuso el inventario.",
        )
        self._refrescar_consulta_actual()

    def _refrescar_consulta_actual(self):
        if self.consulta_actual == "pendientes":
            self.consultar_notas_pendientes()
        elif self.consulta_actual == "cliente":
            self.consultar_notas_cliente()
        elif self.consulta_actual == "bajo_stock":
            self.consultar_bajo_stock()
        elif self.consulta_actual == "sin_movimiento":
            self.consultar_sin_movimiento()
        elif self.consulta_actual == "proveedor":
            self.consultar_por_proveedor()
        elif self.consulta_actual == "marca":
            self.consultar_por_marca()
        else:
            self.consultar_periodo()

    def consultar_notas_pendientes(self):
        self.consulta_actual = "pendientes"
        try:
            datos = self.modelo.notas_pendientes_por_pagar()
        except (ValueError, RuntimeError, DatabaseError) as error:
            messagebox.showerror("Error", str(error))
            return

        columnas = [
            "ID",
            "Fecha",
            "Documento",
            "Cliente",
            "Total",
            "Estado",
            "Saldo pendiente",
            "Días crédito",
            "Vencimiento",
            "Días restantes",
            "Situación",
        ]
        datos = self._formatear_montos(columnas, datos)
        self.vista.mostrar_tabla(columnas, datos)
        self.vista.ultimo_resultado = {"columnas": columnas, "filas": datos}
        self.actualizar_acciones_nota()

    @staticmethod
    def _formatear_montos(columnas, filas):
        """Formatea sólo los importes numéricos antes de mostrarlos en la tabla."""
        columnas_monetarias = {"Total", "Saldo pendiente"}
        indices = [
            indice
            for indice, columna in enumerate(columnas)
            if columna in columnas_monetarias
        ]
        filas_formateadas = []
        for fila in filas:
            valores = list(fila)
            for indice in indices:
                if isinstance(valores[indice], (int, float)):
                    valores[indice] = ConsultasModel.formatear_moneda(valores[indice])
            filas_formateadas.append(tuple(valores))
        return filas_formateadas

    @staticmethod
    def _columnas_historial():
        return [
            "ID",
            "Fecha",
            "Documento",
            "Cliente",
            "Total",
            "Estado",
            "Días crédito",
            "Vencimiento",
            "Días restantes",
            "Situación",
            "Registro",
            "Motivo anulación",
        ]

    @staticmethod
    def _filas_historial(notas):
        claves = (
            "venta_id",
            "fecha",
            "cliente_documento",
            "cliente_nombre",
            "total",
            "estado",
            "dias_credito",
            "fecha_vencimiento",
            "dias_restantes",
            "estado_vencimiento",
            "registro",
            "motivo_anulacion",
        )
        filas = [tuple(nota[clave] for clave in claves) for nota in notas]
        return ConsultasController._formatear_montos(
            ConsultasController._columnas_historial(), filas
        )

    def consultar_periodo(self):
        self.consulta_actual = "periodo"
        fecha_inicio = self.vista.txt_fecha_inicio.obtener_texto().strip()
        fecha_fin = self.vista.txt_fecha_fin.obtener_texto().strip()
        self.vista.txt_cliente.limpiar()
        self.vista.ocultar_sugerencias_clientes()
        self.cliente_seleccionado = None
        self.sugerencias_cliente = []
        self.indice_cliente = -1
        try:
            notas = self.modelo.obtener_historial_notas(fecha_inicio, fecha_fin)
        except (ValueError, RuntimeError, DatabaseError) as error:
            messagebox.showerror("Error en consulta", str(error))
            return

        columnas = self._columnas_historial()
        filas = self._filas_historial(notas)
        self.vista.mostrar_tabla(columnas, filas)
        self.vista.ultimo_resultado = {"columnas": columnas, "filas": filas}
        self.actualizar_acciones_nota()

    def consultar_notas_cliente(self):
        self.consulta_actual = "cliente"
        cliente = self.cliente_seleccionado
        texto = self.vista.txt_cliente.obtener_texto().strip()
        if not cliente and texto:
            try:
                coincidencias = self.clientes_model.buscar_sugerencias(texto, 6)
            except DatabaseError as error:
                messagebox.showerror("Error de base de datos", str(error))
                return
            exactas = [
                (documento, nombre)
                for documento, nombre in coincidencias
                if documento.casefold() == texto.casefold()
                or nombre.casefold() == texto.casefold()
            ]
            if len(exactas) == 1:
                cliente = exactas[0][0]
                self.cliente_seleccionado = cliente
        if not cliente:
            messagebox.showwarning(
                "Atención", "Debes indicar el documento del cliente."
            )
            return

        try:
            notas = self.modelo.obtener_historial_notas(
                self.vista.txt_fecha_inicio.obtener_texto(),
                self.vista.txt_fecha_fin.obtener_texto(),
                cliente,
            )
        except (ValueError, RuntimeError, DatabaseError) as error:
            messagebox.showerror("Error en consulta", str(error))
            return

        columnas = self._columnas_historial()
        filas = self._filas_historial(notas)
        self.vista.mostrar_tabla(columnas, filas)
        self.vista.ultimo_resultado = {"columnas": columnas, "filas": filas}
        self.actualizar_acciones_nota()

    def consultar_bajo_stock(self):
        """Muestra productos cuya existencia está en o bajo el mínimo definido."""
        self.consulta_actual = "bajo_stock"
        try:
            productos = self.modelo.obtener_productos_bajo_stock()
        except (ValueError, RuntimeError, DatabaseError) as error:
            messagebox.showerror("Error en consulta", str(error))
            return
        columnas = ["Código", "Producto", "Stock", "Mínimo"]
        filas = [
            (
                producto["codigo"],
                producto["nombre"],
                producto["stock"],
                producto["stock_minimo"],
            )
            for producto in productos
        ]
        self._mostrar_resultado_productos(columnas, filas)

    def consultar_sin_movimiento(self):
        """Muestra productos activos sin ventas durante el período indicado."""
        self.consulta_actual = "sin_movimiento"
        dias = self.vista.txt_dias_analisis.obtener_texto().strip()
        try:
            productos = self.modelo.obtener_productos_sin_movimiento(dias)
        except (ValueError, RuntimeError, DatabaseError) as error:
            messagebox.showerror("Error en consulta", str(error))
            return
        columnas = ["Código", "Producto", "Stock", "Última venta"]
        filas = [
            (
                producto["codigo"],
                producto["nombre"],
                producto["stock"],
                producto["ultima_venta"] or "Sin ventas",
            )
            for producto in productos
        ]
        self._mostrar_resultado_productos(columnas, filas)

    def consultar_por_proveedor(self):
        """Muestra productos filtrados por el proveedor escrito en el filtro."""
        self.consulta_actual = "proveedor"
        try:
            productos = self.modelo.obtener_productos_por_proveedor(
                self.vista.txt_proveedor.obtener_texto()
            )
        except (ValueError, RuntimeError, DatabaseError) as error:
            messagebox.showerror("Error en consulta", str(error))
            return
        self._mostrar_productos_con_catalogo(productos)

    def consultar_por_marca(self):
        """Muestra productos filtrados por la marca escrita en el filtro."""
        self.consulta_actual = "marca"
        try:
            productos = self.modelo.obtener_productos_por_marca(
                self.vista.txt_marca.obtener_texto()
            )
        except (ValueError, RuntimeError, DatabaseError) as error:
            messagebox.showerror("Error en consulta", str(error))
            return
        self._mostrar_productos_con_catalogo(productos)

    def _mostrar_productos_con_catalogo(self, productos):
        columnas = [
            "Código",
            "Producto",
            "Marca",
            "Proveedor",
            "Stock",
            "Mínimo",
            "Estado",
        ]
        filas = [
            (
                producto["codigo"],
                producto["nombre"],
                producto["marca"],
                producto["proveedor"],
                producto["stock"],
                producto["stock_minimo"],
                producto["estado"],
            )
            for producto in productos
        ]
        self._mostrar_resultado_productos(columnas, filas)

    def _mostrar_resultado_productos(self, columnas, filas):
        self.vista.mostrar_tabla(columnas, filas)
        self.vista.ultimo_resultado = {"columnas": columnas, "filas": filas}
        self.actualizar_acciones_nota()

    def imprimir_resultado_actual(self):
        """Guarda en PDF el resultado que se muestra actualmente en la tabla."""
        resultado = self.vista.ultimo_resultado or {}
        columnas = resultado.get("columnas", [])
        filas = resultado.get("filas", [])
        if not columnas:
            messagebox.showwarning(
                "Atención", "Primero realiza una consulta para generar el reporte."
            )
            return

        titulos = {
            "pendientes": "Notas pendientes de pago",
            "periodo": "Historial de notas",
            "cliente": "Historial de notas por cliente",
            "bajo_stock": "Inventario bajo stock mínimo",
            "sin_movimiento": "Productos sin movimiento",
            "proveedor": "Productos por proveedor",
            "marca": "Productos por marca",
        }
        titulo = titulos.get(self.consulta_actual, "Reporte de consultas")
        nombre = f"{titulo.replace(' ', '_')}.pdf"
        ruta = filedialog.asksaveasfilename(
            title="Guardar reporte para imprimir",
            initialfile=nombre,
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
        )
        if not ruta:
            return
        try:
            PDFService.generar_reporte_consulta(ruta, titulo, columnas, filas)
            if sys.platform == "win32":
                os.startfile(ruta)
            elif sys.platform == "darwin":
                subprocess.run(["open", ruta], check=True)
            else:
                subprocess.run(["xdg-open", ruta], check=True)
        except (OSError, subprocess.SubprocessError) as error:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {error}")
            return
        messagebox.showinfo("Reporte generado", "El PDF se abrió para su impresión.")
