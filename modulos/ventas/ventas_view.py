import customtkinter as ctk
from componentes.boton.boton_view import BotonView
from componentes.entrada.entrada_view import EntradaView
from componentes.tabla.tabla_view import TablaView
from config.estilos import (
    COLOR_FONDO,
    FUENTE_TITULO,
    COLOR_PRIMARIO,
    COLOR_EXITO,
    COLOR_EXITO_HOVER,
    COLOR_PELIGRO,
    COLOR_PELIGRO_HOVER,
)


class VentasView(ctk.CTkFrame):
    """Interfaz gráfica del módulo de Ventas con búsqueda en tiempo real."""

    def __init__(self, master):
        super().__init__(master=master, fg_color=COLOR_FONDO)

        self.lbl_titulo = ctk.CTkLabel(
            self, text="Nueva Nota de Entrega", font=FUENTE_TITULO
        )
        self.lbl_titulo.pack(pady=10)

        self.frame_cliente = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_cliente.pack(pady=5, fill="x", padx=20)

        self.txt_cliente_buscar = EntradaView(
            self.frame_cliente,
            placeholder="Buscar Cliente (RIF, Cédula o Nombre)...",
            width=300,
        )
        self.txt_cliente_buscar.pack(side="left", padx=5)

        self.lbl_cliente_activo = ctk.CTkLabel(
            self.frame_cliente,
            text="Cliente: (Ninguno seleccionado)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="orange",
        )
        self.lbl_cliente_activo.pack(side="left", padx=15)

        self.frame_sugerencias = ctk.CTkFrame(
            self, fg_color="#FFFFFF", border_color=COLOR_PRIMARIO, border_width=1
        )

        self.frame_form = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_form.pack(pady=10, fill="x", padx=20)

        for i in range(4):
            self.frame_form.grid_columnconfigure(i, weight=1)

        self.txt_codigo = EntradaView(
            self.frame_form, placeholder="Cód. o Nombre Producto"
        )
        self.txt_codigo.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.txt_nombre = EntradaView(self.frame_form, placeholder="Descripción")
        self.txt_nombre.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.txt_precio = EntradaView(self.frame_form, placeholder="Precio Unit. ($)")
        self.txt_precio.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        self.txt_cantidad = EntradaView(self.frame_form, placeholder="Cantidad")
        self.txt_cantidad.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.pack(fill="x", padx=20, pady=(0, 10))
        self.frame_acciones.grid_columnconfigure(0, weight=1)

        self.btn_agregar = BotonView(
            self.frame_acciones,
            texto="Agregar Item",
            fg_color=COLOR_PRIMARIO,
            width=180,
        )
        self.btn_agregar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.frame_sugerencias_prod = ctk.CTkFrame(
            self, fg_color="#FFFFFF", border_color=COLOR_PRIMARIO, border_width=1
        )

        self.tabla_ventas = TablaView(
            self, columnas=["Código", "Producto", "Cant.", "P. Unitario", "Subtotal"]
        )
        self.tabla_ventas.pack(pady=10, fill="both", expand=True, padx=20)
        self.tabla_ventas.tabla.bind("<ButtonRelease-1>", self._on_click_tabla_venta)
        self.tabla_ventas.tabla.bind(
            "<Double-Button-1>", self._on_doble_click_tabla_venta
        )

        self.frame_footer = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_footer.pack(pady=10, fill="x", padx=20)

        self.lbl_total = ctk.CTkLabel(
            self.frame_footer, text="Total: $0.00", font=FUENTE_TITULO
        )
        self.lbl_total.pack(side="left", padx=10)

        self.frame_estado_pago = ctk.CTkFrame(self.frame_footer, fg_color="transparent")
        self.frame_estado_pago.pack(side="left", padx=10)
        ctk.CTkLabel(self.frame_estado_pago, text="Estado de pago").pack(
            side="left", padx=(0, 6)
        )
        self.menu_estado_pago = ctk.CTkOptionMenu(
            self.frame_estado_pago,
            values=["Contado", "A Credito"],
            width=140,
            command=self.actualizar_campo_dias_credito,
        )
        self.menu_estado_pago.set("A Credito")
        self.menu_estado_pago.pack(side="left")

        self.frame_dias_credito = ctk.CTkFrame(
            self.frame_footer, fg_color="transparent"
        )
        self.frame_dias_credito.pack(side="left", padx=8)
        ctk.CTkLabel(self.frame_dias_credito, text="Días crédito").pack(
            side="left", padx=(0, 5)
        )
        self.txt_dias_credito = EntradaView(
            self.frame_dias_credito,
            width=60,
            placeholder="30",
        )
        self.txt_dias_credito.insert(0, "30")
        self.txt_dias_credito.pack(side="left")
        self.actualizar_campo_dias_credito("A Credito")

        self.btn_quitar_item = BotonView(
            self.frame_footer,
            texto="Quitar item",
            fg_color=COLOR_PELIGRO,
            hover_color=COLOR_PELIGRO_HOVER,
            width=140,
        )
        self.btn_quitar_item.pack(side="right", padx=10)

        self.btn_cancelar = BotonView(
            self.frame_footer,
            texto="Cancelar venta",
            fg_color=COLOR_PELIGRO,
            hover_color=COLOR_PELIGRO_HOVER,
            width=160,
        )
        self.btn_cancelar.pack(side="right", padx=10)

        self.btn_procesar = BotonView(
            self.frame_footer,
            texto="Emitir Nota de Entrega",
            fg_color=COLOR_EXITO,
            hover_color=COLOR_EXITO_HOVER,
            width=180,
        )
        self.btn_procesar.pack(side="right", padx=10)

        self.seleccionado = None
        self.bind(
            "<Map>",
            lambda _event: self.after_idle(self.enfocar_busqueda_cliente),
            add="+",
        )

        self.bloquear_articulos()

    def mostrar_sugerencias(self, lista_clientes, callback):
        """Despliega la lista interactiva de clientes coincidentes."""
        for w in self.frame_sugerencias.winfo_children():
            w.destroy()

        if not lista_clientes:
            self.ocultar_sugerencias()
            return

        self.frame_sugerencias.pack(
            fill="x", padx=25, pady=(0, 5), before=self.frame_form
        )

        for doc, nombre in lista_clientes:
            btn = ctk.CTkButton(
                self.frame_sugerencias,
                text=f"{doc} - {nombre}",
                anchor="w",
                fg_color="#FFFFFF",
                text_color="#1A1A1A",
                hover_color="#FFE0D2",
                command=lambda d=doc, n=nombre: callback(d, n),
            )
            btn.pack(fill="x", padx=5, pady=2)

    def resaltar_sugerencia_cliente(self, indice):
        self._resaltar_sugerencia(self.frame_sugerencias, indice)

    def enfocar_busqueda_cliente(self):
        if self.winfo_ismapped():
            self.txt_cliente_buscar.focus_set()
            self.txt_cliente_buscar.icursor("end")

    def ocultar_sugerencias(self):
        self.frame_sugerencias.pack_forget()

    def mostrar_sugerencias_productos(self, lista_productos, callback):
        """Despliega la lista interactiva de productos coincidentes."""
        for w in self.frame_sugerencias_prod.winfo_children():
            w.destroy()

        if not lista_productos:
            self.ocultar_sugerencias_productos()
            return

        self.frame_sugerencias_prod.pack(
            fill="x", padx=25, pady=(0, 5), before=self.frame_acciones
        )

        for cod, nom, prec, stock in lista_productos:
            btn = ctk.CTkButton(
                self.frame_sugerencias_prod,
                text=f"{cod} | {nom} - ${prec:.2f} (Stock: {stock})",
                anchor="w",
                fg_color="#FFFFFF",
                text_color="#1A1A1A",
                hover_color="#FFE0D2",
                command=lambda c=cod, n=nom, p=prec: callback(c, n, p),
            )
            btn.pack(fill="x", padx=5, pady=2)

    def resaltar_sugerencia_producto(self, indice):
        self._resaltar_sugerencia(self.frame_sugerencias_prod, indice)

    @staticmethod
    def _resaltar_sugerencia(frame, indice):
        for posicion, boton in enumerate(frame.winfo_children()):
            seleccionado = posicion == indice
            boton.configure(
                fg_color="#FFC49C" if seleccionado else "#FFFFFF",
                border_width=1 if seleccionado else 0,
                border_color=COLOR_PRIMARIO,
            )

    def ocultar_sugerencias_productos(self):
        self.frame_sugerencias_prod.pack_forget()

    def limpiar_formulario_articulo(self):
        self.txt_codigo.limpiar()
        self.txt_nombre.configure(state="normal")
        self.txt_nombre.limpiar()
        self.txt_nombre.configure(state="disabled")
        self.txt_precio.configure(state="normal")
        self.txt_precio.limpiar()
        self.txt_precio.configure(state="disabled")
        self.txt_cantidad.limpiar()

    def _on_click_tabla_venta(self, event):
        item_id = self.tabla_ventas.tabla.identify_row(event.y)
        if not item_id:
            return
        valores = self.tabla_ventas.tabla.item(item_id, "values")
        if not valores:
            return
        codigo = str(valores[0])
        self.seleccionado = codigo

    def _on_doble_click_tabla_venta(self, event):
        item_id = self.tabla_ventas.tabla.identify_row(event.y)
        if not item_id:
            return
        valores = self.tabla_ventas.tabla.item(item_id, "values")
        if not valores:
            return
        self.seleccionado = str(valores[0])
        self.master.focus_set()

    def bloquear_busqueda_cliente(self, bloquear: bool):
        self.txt_cliente_buscar.configure(state="disabled" if bloquear else "normal")

    def bloquear_articulos(self):
        self.txt_codigo.configure(state="disabled")
        self.txt_nombre.configure(state="disabled")
        self.txt_precio.configure(state="disabled")
        self.txt_cantidad.configure(state="disabled")
        self.btn_agregar.cambiar_estado(activo=False)

    def desbloquear_articulos(self):
        self.txt_codigo.configure(state="normal")
        self.txt_nombre.configure(state="disabled")
        self.txt_precio.configure(state="disabled")
        self.txt_cantidad.configure(state="normal")
        self.btn_agregar.cambiar_estado(activo=True)

    def actualizar_campo_dias_credito(self, estado=None):
        estado_actual = estado or self.menu_estado_pago.get()
        editable = estado_actual.casefold() in {"a credito", "a crédito"}
        self.txt_dias_credito.configure(state="normal" if editable else "disabled")

    def restablecer_dias_credito(self):
        self.menu_estado_pago.set("A Credito")
        self.txt_dias_credito.configure(state="normal")
        self.txt_dias_credito.delete(0, "end")
        self.txt_dias_credito.insert(0, "30")
        self.actualizar_campo_dias_credito("A Credito")
