"""
Sales Model - Complete billing logic
"""
from config.database import get_connection
from config.constants import TAX_RATE, INVOICE_PREFIX
from datetime import datetime

class SaleModel:
    @staticmethod
    def recent_sales(limit=5):
        with get_connection() as conn:
            cursor = conn.execute("""
SELECT s.*, c.name as customer_name, s.discount_amount as discount
FROM sales s
LEFT JOIN customers c ON s.customer_id = c.id
ORDER BY s.sale_date DESC LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def create_sale(invoice_data):
        """Create complete sale with line items"""
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO sales (invoice_number, customer_id, sale_date, 
                                 subtotal, tax_amount, discount_amount, total_amount,
                                 created_by_user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (invoice_data['invoice_number'], invoice_data.get('customer_id'),
                  datetime.now(), invoice_data['subtotal'], invoice_data['tax_amount'],
                  invoice_data.get('discount_amount', 0), invoice_data['total_amount'],
                  invoice_data['created_by_user_id']))
            
            sale_id = cursor.lastrowid
            
            # Add line items
            for item in invoice_data['items']:
                cursor.execute("""
                    INSERT INTO sale_items (sale_id, medicine_id, quantity, 
                                         unit_price, line_total)
                    VALUES (?, ?, ?, ?, ?)
                """, (sale_id, item['medicine_id'], item['quantity'],
                      item['unit_price'], item['line_total']))
            
            # Update medicine stock
            for item in invoice_data['items']:
                cursor.execute("""
                    UPDATE medicines SET quantity = quantity - ? 
                    WHERE id = ?
                """, (item['quantity'], item['medicine_id']))
            
            return sale_id
