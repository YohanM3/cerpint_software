import os
from datetime import datetime
from html import escape
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


class PDFService:

    @staticmethod
    def _texto_pdf(valor) -> str:
        return escape(str(valor if valor is not None else ""))

    @staticmethod
    def generar_reporte_consulta(filepath, titulo, columnas, filas):
        """Genera un PDF imprimible con el resultado de una consulta."""
        doc = SimpleDocTemplate(
            filepath,
            pagesize=landscape(letter),
            rightMargin=24,
            leftMargin=24,
            topMargin=28,
            bottomMargin=28,
        )
        styles = getSampleStyleSheet()
        style_titulo = ParagraphStyle(
            "TituloReporte",
            parent=styles["Heading1"],
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#1a2a3a"),
        )
        style_normal = ParagraphStyle(
            "CeldaReporte", parent=styles["Normal"], fontSize=6.5, leading=8
        )
        style_encabezado = ParagraphStyle(
            "EncabezadoReporte",
            parent=style_normal,
            fontName="Helvetica-Bold",
            textColor=colors.white,
        )

        contenido = [
            Paragraph("FERRETERÍA CERPINT", style_titulo),
            Paragraph(PDFService._texto_pdf(titulo), styles["Heading2"]),
            Paragraph(f"Generado: {datetime.now():%Y-%m-%d %H:%M}", style_normal),
            Spacer(1, 10),
        ]
        datos_tabla = [
            [
                Paragraph(PDFService._texto_pdf(columna), style_encabezado)
                for columna in columnas
            ]
        ]
        for fila in filas:
            datos_tabla.append(
                [
                    Paragraph(PDFService._texto_pdf(valor), style_normal)
                    for valor in fila
                ]
            )

        ancho_disponible = 720
        ancho_columna = ancho_disponible / max(len(columnas), 1)
        tabla = Table(
            datos_tabla,
            colWidths=[ancho_columna] * len(columnas),
            repeatRows=1,
        )
        tabla.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a2a3a")),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d0d7de")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        contenido.append(tabla)
        doc.build(contenido)
        return str(Path(filepath))

    @staticmethod
    def generar_nota_entrega(filepath, venta_id, cliente_data, items, total):
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        style_title = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=16,
            leading=18,
            textColor=colors.HexColor("#1a2a3a"),
        )
        style_bold = ParagraphStyle(
            "BoldStyle",
            parent=styles["Normal"],
            fontSize=9,
            leading=11,
            fontName="Helvetica-Bold",
        )
        style_normal = ParagraphStyle(
            "NormalStyle", parent=styles["Normal"], fontSize=9, leading=11
        )
        style_right = ParagraphStyle(
            "RightStyle", parent=styles["Normal"], fontSize=9, leading=11, alignment=2
        )
        style_header_table = ParagraphStyle(
            "HeaderTable",
            parent=styles["Normal"],
            fontSize=9,
            leading=11,
            fontName="Helvetica-Bold",
            textColor=colors.white,
        )

        elements = []

        numero_serie = f"{venta_id:05d}"
        datos_credito = ""
        if cliente_data.get("fecha_vencimiento"):
            datos_credito = (
                f"<br/>Crédito: {cliente_data.get('dias_credito', 30)} días"
                f"<br/>Vence: {PDFService._texto_pdf(cliente_data['fecha_vencimiento'])}"
            )

        header_data = [
            [
                Paragraph(
                    "<b>FERRETERÍA CERPINT</b>",
                    style_normal,
                ),
                Paragraph(
                    f"<b>NOTA DE ENTREGA</b><br/><font color='red'><b>Nº {numero_serie}</b></font><br/>Fecha: {PDFService._texto_pdf(cliente_data.get('fecha_emision') or 'No disponible')}{datos_credito}",
                    style_right,
                ),
            ]
        ]
        t_header = Table(header_data, colWidths=[300, 240])
        t_header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        elements.append(t_header)
        elements.append(Spacer(1, 10))

        client_data = [
            [
                Paragraph(
                    f"<b>Cliente:</b> {PDFService._texto_pdf(cliente_data['nombre'])}",
                    style_normal,
                ),
                Paragraph(
                    f"<b>CI/RIF:</b> {PDFService._texto_pdf(cliente_data['documento'])}",
                    style_normal,
                ),
            ],
            [
                Paragraph(
                    f"<b>Teléfono:</b> {PDFService._texto_pdf(cliente_data['telefono'])}",
                    style_normal,
                ),
                Paragraph(
                    f"<b>Dirección:</b> {PDFService._texto_pdf(cliente_data['direccion'])}",
                    style_normal,
                ),
            ],
        ]
        t_client = Table(client_data, colWidths=[270, 270])
        t_client.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0f4f8")),
                    ("PADDING", (0, 0), (-1, -1), 6),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ]
            )
        )
        elements.append(t_client)
        elements.append(Spacer(1, 15))

        table_content = [
            [
                Paragraph("Código", style_header_table),
                Paragraph("Descripción", style_header_table),
                Paragraph("Cant.", style_header_table),
                Paragraph("P.Unit ($)", style_header_table),
                Paragraph("Total ($)", style_header_table),
            ]
        ]

        for item in items:
            table_content.append(
                [
                    Paragraph(PDFService._texto_pdf(item["codigo"]), style_normal),
                    Paragraph(PDFService._texto_pdf(item["nombre"]), style_normal),
                    Paragraph(str(item["cantidad"]), style_right),
                    Paragraph(f"{item['precio']:.2f}", style_right),
                    Paragraph(f"{item['subtotal']:.2f}", style_right),
                ]
            )

        t_products = Table(table_content, colWidths=[80, 260, 50, 75, 75])
        t_products.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a2a3a")),
                    ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        elements.append(t_products)
        elements.append(Spacer(1, 10))

        total_data = [
            [
                Paragraph("<b>TOTAL A PAGAR ($):</b>", style_right),
                Paragraph(f"<b>${total:.2f}</b>", style_right),
            ]
        ]
        t_total = Table(total_data, colWidths=[465, 75])
        t_total.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e6ecf2")),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elements.append(t_total)
        elements.append(Spacer(1, 30))

        firmas_data = [
            [
                Paragraph(
                    "___________________________<br/>Entregado Por", style_normal
                ),
                Paragraph(
                    "___________________________<br/>Recibido Conforme", style_normal
                ),
            ]
        ]
        t_firmas = Table(firmas_data, colWidths=[270, 270])
        t_firmas.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        elements.append(t_firmas)

        doc.build(elements)
