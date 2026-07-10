"""
Customer Model - CRUD operations
"""
from config.database import get_connection

class CustomerModel:
    @staticmethod
    def all():
        with get_connection() as conn:
            cursor = conn.execute("SELECT * FROM customers ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def create(customer_data):
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO customers (name, email, phone, address)
                VALUES (?, ?, ?, ?)
            """, (customer_data['name'], customer_data.get('email'), 
                  customer_data.get('phone'), customer_data.get('address')))
            return cursor.lastrowid
    
    @staticmethod
    def total_spent(customer_id):
        with get_connection() as conn:
            cursor = conn.execute("""
                SELECT COALESCE(SUM(total_amount), 0) as total 
                FROM sales WHERE customer_id = ?
            """, (customer_id,))
            return cursor.fetchone()['total']
