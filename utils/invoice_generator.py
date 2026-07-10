#!/usr/bin/env python3
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from datetime import datetime
import os
import tempfile
import webbrowser

def get_invoice_data(bill_items, customer_id=None, discount=0.0, payment_method="Cash"):
    """Generate invoice metadata from bill data"""
    try:
        # Calculate totals
        subtotal = sum(item.get('total', 0) for item in bill_items)
        tax = subtotal * 0.05  # 5% tax
        total = subtotal + tax - discount
        
        # Generate invoice number (timestamp-based)
        timestamp = datetime.now()
        invoice_number = f"INV-{timestamp.strftime('%Y%m%d')}-{timestamp.strftime('%H%M%S')}"
        
        return {
            'invoice_number': invoice_number,
            'date': timestamp.strftime('%d/%m/%Y'),
            'time': timestamp.strftime('%I:%M %p'),
            'subtotal': subtotal,
            'tax': tax,
            'discount': discount,
            'total': total,
            'payment_method': payment_method,
            'customer_id': customer_id
        }
    except Exception as e:
        print(f"Error generating invoice data: {e}")
        return None

def open_pdf(pdf_path):
    """Open PDF file in default viewer"""
    try:
        if os.path.exists(pdf_path):
            webbrowser.open(pdf_path)
            return True
        else:
            print(f"PDF file not found: {pdf_path}")
            return False
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return False

def generate_invoice_pdf(bill_items, customer_info, pharmacy_settings, invoice_data):
    try:
        temp_dir = tempfile.gettempdir()
        pdf_filename = f"invoice_{invoice_data['invoice_number']}.pdf"
        pdf_path = os.path.join(temp_dir, pdf_filename)
        
        # Tightened margins for a more "official" look
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        story = []
        
        # --- MODERN MONOCHROME STYLES ---
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, textColor=colors.black, spaceAfter=2)
        subtitle_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=9, textColor=colors.grey, spaceAfter=10)
        normal_style = ParagraphStyle('Normal', fontSize=9, leading=12)
        label_style = ParagraphStyle('Label', fontSize=9, fontName='Helvetica-Bold')

        # 1. Header: Pharmacy Info
        p_name = Paragraph(f"<b>{pharmacy_settings['pharmacy_name'].upper()}</b>", title_style)
        story.append(p_name)
        
        # Build address line using the new settings structure
        address_parts = []
        if pharmacy_settings.get('address'):
            address_parts.append(pharmacy_settings['address'])
        if pharmacy_settings.get('city'):
            address_parts.append(pharmacy_settings['city'])
        if pharmacy_settings.get('pincode'):
            address_parts.append(pharmacy_settings['pincode'])
        
        address_line = ", ".join(address_parts)
        
        # Build additional info line
        additional_info_parts = []
        if pharmacy_settings.get('gstin'):
            additional_info_parts.append(f"GSTIN: {pharmacy_settings['gstin']}")
        if pharmacy_settings.get('license_number'):
            additional_info_parts.append(f"License: {pharmacy_settings['license_number']}")
        if pharmacy_settings.get('phone'):
            additional_info_parts.append(f"Phone: {pharmacy_settings['phone']}")
        if pharmacy_settings.get('email'):
            additional_info_parts.append(f"Email: {pharmacy_settings['email']}")
        
        additional_info = " | ".join(additional_info_parts)
        
        address = f"{address_line}<br/>{additional_info}"
        story.append(Paragraph(address, subtitle_style))
        story.append(Spacer(1, 15))

        # 2. Invoice Meta Table (Invisible borders for layout)
        meta_data = [
            [Paragraph(f"<b>BILL TO:</b><br/>{customer_info['name']}<br/>Ph: {customer_info['phone']}", normal_style),
             Paragraph(f"<b>INVOICE NO:</b> {invoice_data['invoice_number']}<br/><b>DATE:</b> {invoice_data['date']}<br/><b>TIME:</b> {invoice_data['time']}", normal_style)]
        ]
        meta_table = Table(meta_data, colWidths=[4*inch, 3*inch])
        meta_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        story.append(meta_table)
        story.append(Spacer(1, 20))

        # 3. Items Table
        # Added 'HSN' column - very common in professional medical invoices
        table_data = [['Item Description', 'Batch', 'Exp.', 'Qty', 'Rate', 'Amount']]
        
        for item in bill_items:
            table_data.append([
                item.get('medicine', ''),
                item.get('batch_number', ''),
                item.get('expiry_date', ''),
                item.get('quantity', 0),
                f"{item.get('price', 0):.2f}",
                f"{item.get('total', 0):.2f}"
            ])

        # Styling the table with professional grayscale
        item_table = Table(table_data, colWidths=[2.2*inch, 1.2*inch, 0.8*inch, 0.5*inch, 1*inch, 1*inch])
        item_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke), # Light gray header
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), # Thin subtle lines
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(item_table)

        # 4. Summary & Totals
        summary_data = [
            ['', 'Subtotal:', f"{invoice_data['subtotal']:.2f}"],
            ['', 'Tax (GST):', f"{invoice_data['tax']:.2f}"],
            ['', 'Discount:', f"-{invoice_data['discount']:.2f}"],
            ['', 'GRAND TOTAL:', f"Rs. {invoice_data['total']:.2f}"]
        ]
        summary_table = Table(summary_data, colWidths=[4.2*inch, 1*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (1, 3), (-1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 3), (-1, 3), 12),
            ('LINEABOVE', (1, 3), (-1, 3), 1, colors.black), # Bold line above total
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 40))

        # 5. Footer: Terms and Signature
        footer_data = [
            [Paragraph("<font size=8><b>Terms:</b><br/>1. Goods once sold will not be taken back.<br/>2. Consult a doctor before using medicines.</font>", normal_style),
             Paragraph("<br/><br/>_______________________<br/>Authorised Signatory", ParagraphStyle('Sign', fontSize=9, alignment=1))]
        ]
        footer_table = Table(footer_data, colWidths=[4*inch, 3*inch])
        story.append(footer_table)

        doc.build(story)
        return pdf_path
        
    except Exception as e:
        print(f"Error: {e}")
        return None