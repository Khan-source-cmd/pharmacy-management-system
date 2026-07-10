"""
Supplier Model - CRUD operations
"""
from config.database import get_connection

class SupplierModel:
    @staticmethod
    def all():
        with get_connection() as conn:
            cursor = conn.execute("SELECT * FROM suppliers ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def create(supplier_data):
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO suppliers (name, contact_person, email, phone, address)
                VALUES (?, ?, ?, ?, ?)
            """, (supplier_data['name'], supplier_data.get('contact_person'),
                  supplier_data.get('email'), supplier_data.get('phone'),
                  supplier_data.get('address')))
            return cursor.lastrowid
