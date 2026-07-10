"""
Base model class for all CRUD operations
"""
from config.database import get_connection

class BaseModel:
    TABLE_NAME = None
    
    @classmethod
    def all(cls):
        with get_connection() as conn:
            cursor = conn.execute(f"SELECT * FROM {cls.TABLE_NAME}")
            return [dict(row) for row in cursor.fetchall()]
    
    @classmethod
    def find(cls, id):
        with get_connection() as conn:
            cursor = conn.execute(f"SELECT * FROM {cls.TABLE_NAME} WHERE id = ?", (id,))
            return dict(cursor.fetchone()) if cursor.fetchone() else None
