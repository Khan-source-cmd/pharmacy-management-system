"""
Medicine Model - CRUD operations + business logic
"""
from config.database import get_connection
from config.constants import LOW_STOCK_THRESHOLD, EXPIRY_WARNING_DAYS
from datetime import date, timedelta

class MedicineModel:
    @staticmethod
    def all():
        with get_connection() as conn:
            cursor = conn.execute("""
                SELECT *, 
                       CASE 
                           WHEN quantity <= reorder_level THEN 'Low Stock'
                           WHEN quantity = 0 THEN 'Out of Stock'
                           ELSE 'In Stock'
                       END as stock_status
                FROM medicines 
                ORDER BY name
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def create(medicine_data):
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO medicines (name, category, batch_number, expiry_date, 
                                     quantity, reorder_level, price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (medicine_data['name'], medicine_data['category'],
                  medicine_data['batch_number'], medicine_data['expiry_date'],
                  medicine_data['quantity'], medicine_data['reorder_level'],
                  medicine_data['price']))
            return cursor.lastrowid
    
    @staticmethod
    def low_stock_count():
        with get_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) as count FROM medicines 
                WHERE quantity <= reorder_level AND quantity > 0
            """)
            return cursor.fetchone()['count']
