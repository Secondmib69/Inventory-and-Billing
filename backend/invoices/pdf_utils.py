import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from barcode import Code128
from barcode.writer import ImageWriter

def generate_invoice_pdf(invoice):
    """
    Generates a PDF for a given Invoice instance.
    Returns a BytesIO buffer containing the PDF data.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    elements = []
    styles = getSampleStyleSheet()

    # 1. Header & Invoice Info
    elements.append(Paragraph(f"INVOICE", styles['Title']))
    elements.append(Spacer(1, 10*mm))
    
    header_data = [
        [f"Invoice Number: {invoice.invoice_number}", f"Customer: {invoice.customer_name}"],
        [f"Date: {invoice.created_at.strftime('%Y-%m-%d %H:%M')}", f"Status: Paid"]
    ]
    header_table = Table(header_data, colWidths=[85*mm, 85*mm])
    elements.append(header_table)
    elements.append(Spacer(1, 10*mm))

    # 2. The Items Table
    # Table Header
    data = [["Product", "Quantity", "Unit Price", "Total"]]
    
    # Table Rows
    for item in invoice.items.all():
        data.append([
            item.product.name,
            str(item.quantity),
            f"{item.unit_price:,} R",
            f"{item.item_total_price:,} R"
        ])

    # Grand Total Row
    data.append(["", "", "GRAND TOTAL:", f"{invoice.total_amount:,} R"])

    item_table = Table(data, colWidths=[70*mm, 30*mm, 35*mm, 35*mm])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 3), (-1, -1), 'RIGHT'), # Align prices to right
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey), # Grid for items
        ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'), # Bold for Total
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 20*mm))

    # 3. Barcode Generation (Code128)
    # We generate the barcode in memory as an image
    barcode_buffer = io.BytesIO()
    code = Code128(invoice.invoice_number, writer=ImageWriter())
    code.write(barcode_buffer, options={"write_text": False})
    barcode_buffer.seek(0)
    
    barcode_img = Image(barcode_buffer, width=50*mm, height=15*mm)
    elements.append(barcode_img)
    # elements.append(Paragraph(f"{invoice.invoice_number}", ParagraphStyle(name='Center', alignment=1)))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
