import customtkinter as ctk

from componentes.boton.boton_view import BotonView
from componentes.entrada.entrada_view import EntradaView
from componentes.tabla.tabla_view import TablaView
from config.estilos import (
    COLOR_EXITO,
    COLOR_EXITO_HOVER,
    COLOR_FONDO,
    COLOR_SECUNDARIO,
    COLOR_SECUNDARIO_HOVER,
    FUENTE_TITULO,
)


class InventarioView(ctk.CTkFrame):
    """Vista de inventario centrada en consultar el catálogo de productos."""

    def __init__(self, master):
        super().__init__(master=master, fg_color=COLOR_FONDO)

        self.lbl_titulo = ctk.CTkLabel(
            self, text="Inventario de Productos", font=FUENTE_TITULO
        )
        self.lbl_titulo.pack(pady=10)

        self.frame_busqueda = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_busqueda.pack(fill="x", padx=20, pady=(0, 8))
        self.frame_busqueda.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.frame_busqueda,
            text="Buscar producto",
        ).grid(row=0, column=0, sticky="w")
        self.txt_buscar_producto = EntradaView(
            self.frame_busqueda,
            placeholder="Buscar por código o nombre de producto",
        )
        self.txt_buscar_producto.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        self.frame_sugerencias_productos = ctk.CTkFrame(
            self.frame_busqueda,
            fg_color="#FFFFFF",
            border_color=COLOR_SECUNDARIO,
            border_width=1,
        )
        self.frame_sugerencias_productos.grid(
            row=2, column=0, sticky="ew", padx=(0, 8), pady=(3, 0)
        )
        self.frame_sugerencias_productos.grid_remove()

        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.pack(fill="x", padx=20, pady=(0, 10))
        self.frame_acciones.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_crear = BotonView(
            self.frame_acciones,
            texto="Crear producto",
            fg_color=COLOR_EXITO,
            hover_color=COLOR_EXITO_HOVER,
        )
        self.btn_crear.grid(row=0, column=0, sticky="w", padx=5)

        self.btn_activar = BotonView(
            self.frame_acciones,
            texto="Activar producto",
            fg_color=COLOR_SECUNDARIO,
            hover_color=COLOR_SECUNDARIO_HOVER,
        )
        self.btn_activar.grid(row=0, column=1, padx=5)

        self.btn_desactivar = BotonView(
            self.frame_acciones,
            texto="Desactivar producto",
            fg_color="#C0392B",
            hover_color="#A93226",
        )
        self.btn_desactivar.grid(row=0, column=2, sticky="e", padx=5)

        self.tabla_inventario = TablaView(
            self,
            columnas=[
                "Código",
                "Producto",
                "Precio",
                "Existencia",
                "Marca",
                "Proveedor",
                "Stock mínimo",
                "Cód. empresa",
                "Estado",
            ],
        )
        self.tabla_inventario.pack(pady=(0, 10), fill="both", expand=True, padx=20)

        self.frame_form = ctk.CTkFrame(self, fg_color="transparent")
        for indice in range(4):
            self.frame_form.grid_columnconfigure(indice, weight=1)

        self.txt_codigo = EntradaView(
            self.frame_form, placeholder="Código interno: 4 letras-4 números (ej.: ABCD-0001)"
        )
        self.txt_codigo.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.txt_nombre = EntradaView(
            self.frame_form, placeholder="Nombre (ej.: Martillo de uña 16 oz)"
        )
        self.txt_nombre.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.txt_precio = EntradaView(
            self.frame_form, placeholder="Precio unitario (ej.: 12.50)"
        )
        self.txt_precio.grid(row=0, column=2, sticky="ew", padx=5, pady=5)
        self.txt_stock = EntradaView(
            self.frame_form, placeholder="Existencia actual (ej.: 25)"
        )
        self.txt_stock.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        self.txt_stock_minimo = EntradaView(
            self.frame_form, placeholder="Stock mínimo de alerta (ej.: 5)"
        )
        self.txt_stock_minimo.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.txt_proveedor = EntradaView(
            self.frame_form, placeholder="Proveedor (ej.: Distribuidora Norte)"
        )
        self.txt_proveedor.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.txt_marca = EntradaView(
            self.frame_form, placeholder="Marca (ej.: Truper)"
        )
        self.txt_marca.grid(row=1, column=2, sticky="ew", padx=5, pady=5)
        self.txt_codigo_empresa = EntradaView(
            self.frame_form, placeholder="Código de empresa del proveedor (ej.: TRU-4587)"
        )
        self.txt_codigo_empresa.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

        self.btn_guardar = BotonView(
            self.frame_form,
            texto="Guardar producto",
            fg_color=COLOR_EXITO,
            hover_color=COLOR_EXITO_HOVER,
        )
        self.btn_guardar.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.btn_actualizar = BotonView(
            self.frame_form,
            texto="Actualizar producto",
            fg_color=COLOR_SECUNDARIO,
            hover_color=COLOR_SECUNDARIO_HOVER,
        )
        self.btn_actualizar.grid(row=2, column=2, sticky="ew", padx=5, pady=5)

    def mostrar_formulario(self):
        self.frame_form.pack(fill="x", padx=20, pady=(0, 10))
        self.btn_crear.focus_set()

    def ocultar_formulario(self):
        self.frame_form.pack_forget()

    def mostrar_sugerencias_productos(self, sugerencias, callback):
        for widget in self.frame_sugerencias_productos.winfo_children():
            widget.destroy()
        if not sugerencias:
            self.ocultar_sugerencias_productos()
            return
        self.frame_sugerencias_productos.grid()
        for codigo, nombre, precio, stock in sugerencias:
            boton = ctk.CTkButton(
                self.frame_sugerencias_productos,
                text=f"{codigo} - {nombre} | Stock: {stock}",
                anchor="w",
                fg_color="#FFFFFF",
                text_color="#1A1A1A",
                hover_color="#E8EEF6",
                command=lambda valores=(codigo, nombre, precio, stock): callback(
                    *valores
                ),
            )
            boton.pack(fill="x", padx=5, pady=2)

    def resaltar_sugerencia_producto(self, indice):
        for posicion, boton in enumerate(
            self.frame_sugerencias_productos.winfo_children()
        ):
            seleccionado = posicion == indice
            boton.configure(
                fg_color="#D9EAF7" if seleccionado else "#FFFFFF",
                border_width=1 if seleccionado else 0,
                border_color=COLOR_SECUNDARIO,
            )

    def ocultar_sugerencias_productos(self):
        self.frame_sugerencias_productos.grid_remove()

    def establecer_solo_lectura(self, solo_lectura: bool):
        """Deshabilita todos los controles que cambian productos."""
        estado = "disabled" if solo_lectura else "normal"
        for entrada in (
            self.txt_codigo,
            self.txt_nombre,
            self.txt_precio,
            self.txt_stock,
            self.txt_stock_minimo,
            self.txt_proveedor,
            self.txt_marca,
            self.txt_codigo_empresa,
        ):
            entrada.configure(state=estado)
        for boton in (
            self.btn_crear,
            self.btn_guardar,
            self.btn_actualizar,
            self.btn_activar,
            self.btn_desactivar,
        ):
            boton.configure(state=estado)
