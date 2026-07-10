"""
Database initialization - Execute SQL files
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "pharmacy.db")

def init_database():
    """Initialize database by running SQL files"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Run schema.sql
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)

    # Run demo_data.sql
    demo_path = os.path.join(os.path.dirname(__file__), "migrations", "demo_data.sql")
    with open(demo_path, 'r') as f:
        demo_sql = f.read()
        cursor.executescript(demo_sql)

    conn.commit()
    conn.close()
    print("✅ Database initialized with schema + demo data!")

if __name__ == "__main__":
    init_database()
