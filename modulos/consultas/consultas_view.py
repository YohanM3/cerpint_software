import customtkinter as ctk
from datetime import datetime
from decimal import Decimal, InvalidOperation

from componentes.boton.boton_view import BotonView
from componentes.entrada.entrada_view import EntradaView
from componentes.tabla.tabla_view import TablaView
from config.estilos import (
    COLOR_FONDO,
    FUENTE_TITULO,
    COLOR_PRIMARIO,
    COLOR_PRIMARIO_HOVER,
)


class ConsultasView(ctk.CTkFrame):
    """Vista de reportes y consultas del sistema."""

    def __init__(self, master):
        super().__init__(master=master, fg_color=COLOR_FONDO)

        self.lbl_titulo = ctk.CTkLabel(
            self,
            text="Consultas",
            font=FUENTE_TITULO,
        )
        self.lbl_titulo.pack(pady=10)

        self.frame_filtros = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_filtros.pack(fill="x", padx=20, pady=(0, 10))
        self.frame_filtros.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(self.frame_filtros, text="Fecha desde").grid(
            row=0, column=0, sticky="w", padx=5
        )
        ctk.CTkLabel(self.frame_filtros, text="Fecha hasta").grid(
            row=0, column=1, sticky="w", padx=5
        )
        ctk.CTkLabel(self.frame_filtros, text="Cliente (opcional)").grid(
            row=0, column=2, sticky="w", padx=5
        )
        ctk.CTkLabel(self.frame_filtros, text="Ventas recientes (días)").grid(
            row=0, column=3, sticky="w", padx=5
        )

        self.txt_fecha_inicio = EntradaView(
            self.frame_filtros, placeholder="YYYY-MM-DD", width=145
        )
        self.txt_fecha_inicio.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.txt_fecha_fin = EntradaView(
            self.frame_filtros, placeholder="YYYY-MM-DD", width=145
        )
        self.txt_fecha_fin.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.txt_cliente = EntradaView(
            self.frame_filtros,
            placeholder="Documento o nombre",
            width=240,
        )
        self.txt_cliente.grid(row=1, column=2, sticky="ew", padx=5, pady=5)
        self.txt_dias_analisis = EntradaView(
            self.frame_filtros, placeholder="30", width=80
        )
        self.txt_dias_analisis.insert(0, "30")
        self.txt_dias_analisis.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        self.frame_sugerencias_clientes = ctk.CTkFrame(
            self.frame_filtros,
            fg_color="#FFFFFF",
            border_color=COLOR_PRIMARIO,
            border_width=1,
        )
        self.frame_sugerencias_clientes.grid(row=2, column=2, sticky="ew", padx=5)
        self.frame_sugerencias_clientes.grid_remove()

        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.pack(fill="x", padx=20, pady=(0, 10))
        self.frame_acciones.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.btn_pendientes = BotonView(
            self.frame_acciones,
            texto="Pendientes",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
            width=170,
        )
        self.btn_pendientes.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.btn_periodo = BotonView(
            self.frame_acciones,
            texto="Todas las notas / período",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
            width=210,
        )
        self.btn_periodo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.btn_cliente = BotonView(
            self.frame_acciones,
            texto="Historial del cliente",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
            width=190,
        )
        self.btn_cliente.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        self.btn_reposicion = BotonView(
            self.frame_acciones,
            texto="Urgencias de compra",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
            width=190,
        )
        self.btn_reposicion.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        self.frame_acciones_nota = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones_nota.pack(fill="x", padx=25, pady=(0, 10))
        self.btn_anular_nota = BotonView(
            self.frame_acciones_nota,
            texto="Anular nota",
            fg_color="#C0392B",
            hover_color="#A93226",
            width=150,
            state="disabled",
        )
        self.btn_anular_nota.pack(side="right", padx=(8, 0))
        self.btn_cambiar_pago = BotonView(
            self.frame_acciones_nota,
            texto="Marcar como pagada",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
            width=190,
            state="disabled",
        )
        self.btn_cambiar_pago.pack(side="right")

        self.lbl_estado_resultado = ctk.CTkLabel(
            self,
            text="",
            anchor="w",
            text_color="#5B6470",
        )
        self.lbl_estado_resultado.pack(fill="x", padx=25, pady=(0, 5))

        self.tabla_reportes = TablaView(
            self,
            columnas=[
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
            ],
        )
        self.tabla_reportes.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.ultimo_resultado = None
        self._orden_direcciones = {}
        self.bind(
            "<Map>",
            lambda _event: self.after_idle(self.enfocar_cliente),
            add="+",
        )

    def enfocar_cliente(self):
        if self.winfo_ismapped():
            self.txt_cliente.focus_set()
            self.txt_cliente.icursor("end")

    def mostrar_sugerencias_clientes(self, sugerencias, callback):
        for widget in self.frame_sugerencias_clientes.winfo_children():
            widget.destroy()
        if not sugerencias:
            self.ocultar_sugerencias_clientes()
            return
        self.frame_sugerencias_clientes.grid()
        for documento, nombre in sugerencias:
            boton = ctk.CTkButton(
                self.frame_sugerencias_clientes,
                text=f"{documento} - {nombre}",
                anchor="w",
                fg_color="#FFFFFF",
                text_color="#1A1A1A",
                hover_color="#FFE0D2",
                command=lambda doc=documento, nom=nombre: callback(doc, nom),
            )
            boton.pack(fill="x", padx=5, pady=2)

    def resaltar_sugerencia_cliente(self, indice):
        for posicion, boton in enumerate(
            self.frame_sugerencias_clientes.winfo_children()
        ):
            seleccionado = posicion == indice
            boton.configure(
                fg_color="#FFC49C" if seleccionado else "#FFFFFF",
                border_width=1 if seleccionado else 0,
                border_color=COLOR_PRIMARIO,
            )

    def ocultar_sugerencias_clientes(self):
        self.frame_sugerencias_clientes.grid_remove()

    @staticmethod
    def _clave_orden(valor):
        if isinstance(valor, (int, float, Decimal)):
            numero = Decimal(str(valor))
            if numero.is_finite():
                return 0, numero

        texto = str(valor).strip()
        try:
            return 1, datetime.fromisoformat(texto)
        except ValueError:
            pass
        try:
            numero = Decimal(texto.replace(",", "."))
            if numero.is_finite():
                return 0, numero
        except InvalidOperation:
            pass
        return 2, texto.casefold()

    @classmethod
    def _ordenar_filas(cls, filas, indice, descendente=False):
        filas = [tuple(fila) for fila in filas]
        con_valor = [
            fila
            for fila in filas
            if fila[indice] is not None and str(fila[indice]).strip()
        ]
        sin_valor = [
            fila
            for fila in filas
            if fila[indice] is None or not str(fila[indice]).strip()
        ]
        con_valor.sort(
            key=lambda fila: cls._clave_orden(fila[indice]), reverse=descendente
        )
        return con_valor + sin_valor

    def _ordenar_columna(self, columna):
        tabla = self.tabla_reportes.tabla
        indice = self.tabla_reportes.columnas.index(columna)
        filas = [tabla.item(item_id, "values") for item_id in tabla.get_children()]
        seleccion = tabla.selection()
        valores_seleccionados = (
            tuple(tabla.item(seleccion[0], "values")) if seleccion else None
        )
        descendente = self._orden_direcciones.get(columna) == "asc"
        self._orden_direcciones[columna] = "desc" if descendente else "asc"
        filas = self._ordenar_filas(filas, indice, descendente)

        self.tabla_reportes.limpiar_tabla()
        for fila in filas:
            item_id = tabla.insert("", "end", values=fila)
            if valores_seleccionados == tuple(fila):
                tabla.selection_set(item_id)
                tabla.focus(item_id)

        if self.ultimo_resultado is not None:
            self.ultimo_resultado["filas"] = filas
        self._actualizar_encabezados_orden()

    def _actualizar_encabezados_orden(self):
        for columna in self.tabla_reportes.columnas:
            direccion = self._orden_direcciones.get(columna)
            indicador = (
                " ▲" if direccion == "asc" else " ▼" if direccion == "desc" else ""
            )
            self.tabla_reportes.tabla.heading(
                columna,
                text=f"{columna}{indicador}",
                command=lambda nombre=columna: self._ordenar_columna(nombre),
            )

    def mostrar_tabla(self, columnas, filas):
        self.tabla_reportes.columnas = columnas
        self.tabla_reportes.tabla.configure(columns=columnas)
        self._orden_direcciones = {}
        anchos = {
            "ID": 50,
            "Fecha": 115,
            "Documento": 95,
            "Cliente": 140,
            "Total": 75,
            "Estado": 80,
            "Saldo pendiente": 90,
            "Días crédito": 70,
            "Vencimiento": 85,
            "Días restantes": 85,
            "Situación": 95,
            "Registro": 75,
            "Motivo anulación": 150,
            "Código": 90,
            "Producto": 150,
            "Stock": 60,
            "Mínimo": 65,
            "Vendidos": 70,
            "Promedio/día": 90,
            "Cobertura días": 90,
            "Prioridad": 105,
        }
        for col in columnas:
            self.tabla_reportes.tabla.column(
                col, width=anchos.get(col, 120), anchor="center"
            )
        self._actualizar_encabezados_orden()

        self.tabla_reportes.limpiar_tabla()
        for fila in filas:
            self.tabla_reportes.tabla.insert("", "end", values=fila)
        if filas:
            self.lbl_estado_resultado.configure(
                text=f"{len(filas)} nota(s) encontrada(s)."
            )
        else:
            self.lbl_estado_resultado.configure(
                text="No hay resultados para esta consulta."
            )
