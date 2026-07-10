#!/usr/bin/env python3
"""
Database Configuration and Connection Management
Simplified database wrapper for the pharmacy management system
"""
import sqlite3
import os
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from config.constants import DB_PATH

class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create medicines table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS medicines (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        batch_number TEXT,
                        expiry_date DATE NOT NULL,
                        quantity INTEGER DEFAULT 0,
                        reorder_level INTEGER DEFAULT 10,
                        price DECIMAL(10,2) NOT NULL,
                        supplier_id INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create sales table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sales (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        invoice_number TEXT UNIQUE NOT NULL,
                        customer_id INTEGER,
                        sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        subtotal DECIMAL(10,2),
                        tax_amount DECIMAL(10,2),
                        discount_amount DECIMAL(10,2) DEFAULT 0,
                        total_amount DECIMAL(10,2),
                        payment_method TEXT DEFAULT 'cash',
                        created_by_user_id INTEGER
                    )
                """)
                
                # Create sale_items table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sale_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sale_id INTEGER,
                        medicine_id INTEGER,
                        quantity INTEGER NOT NULL,
                        unit_price DECIMAL(10,2) NOT NULL,
                        line_total DECIMAL(10,2) NOT NULL,
                        FOREIGN KEY(sale_id) REFERENCES sales(id),
                        FOREIGN KEY(medicine_id) REFERENCES medicines(id)
                    )
                """)
                
                # Create customers table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE,
                        phone TEXT,
                        address TEXT,
                        total_spent DECIMAL(10,2) DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_purchase DATETIME
                    )
                """)
                
                # Create suppliers table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS suppliers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        contact_person TEXT,
                        email TEXT UNIQUE,
                        phone TEXT,
                        address TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT DEFAULT 'staff' CHECK(role IN ('admin', 'staff')),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_login DATETIME,
                        is_active BOOLEAN DEFAULT 1
                    )
                """)
                
                # Create medicines table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS medicines (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        batch_number TEXT,
                        expiry_date DATE NOT NULL,
                        quantity INTEGER DEFAULT 0,
                        reorder_level INTEGER DEFAULT 10,
                        price DECIMAL(10,2) NOT NULL,
                        supplier_id INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert sample data if tables are empty
                self._insert_sample_data(cursor)
                
                conn.commit()
                print("Database initialized successfully")
                
        except Exception as e:
            print(f"Database initialization failed: {e}")
            raise
    
    def _insert_sample_data(self, cursor):
        """Insert sample data for demonstration"""
        
        # Check if medicines table is empty
        cursor.execute("SELECT COUNT(*) FROM medicines")
        if cursor.fetchone()[0] == 0:
            medicines = [
                ("Paracetamol 500mg", "Analgesics", "BATCH001", "2026-12-31", 25, 10, 1.50),
                ("Amoxicillin 250mg", "Antibiotics", "BATCH002", "2026-06-15", 8, 10, 3.75),
                ("Ibuprofen 200mg", "Analgesics", "BATCH003", "2025-11-30", 45, 10, 2.25),
                ("Lisinopril 10mg", "Cardiovascular", "BATCH004", "2026-09-20", 32, 10, 4.50),
                ("Metformin 500mg", "Antidiabetics", "BATCH005", "2026-03-10", 18, 10, 2.80),
                ("Salbutamol Inhaler", "Respiratory", "BATCH006", "2026-08-05", 12, 10, 8.99),
                ("Cetirizine 10mg", "Antihistamines", "BATCH007", "2026-07-22", 60, 10, 1.20),
                ("Atorvastatin 20mg", "Cardiovascular", "BATCH008", "2025-12-15", 5, 10, 6.75),
            ]
            
            for med in medicines:
                cursor.execute("""
                    INSERT INTO medicines (name, category, batch_number, expiry_date, quantity, reorder_level, price)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, med)
        
        # Check if users table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            import bcrypt
            # Insert admin user
            admin_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
            cursor.execute("""
                INSERT INTO users (email, password_hash, role) 
                VALUES (?, ?, ?)
            """, ("admin@medisys.com", admin_hash, "admin"))
            
            # Insert staff user
            staff_hash = bcrypt.hashpw("staff123".encode(), bcrypt.gensalt()).decode()
            cursor.execute("""
                INSERT INTO users (email, password_hash, role) 
                VALUES (?, ?, ?)
            """, ("staff@medisys.com", staff_hash, "staff"))
    
    @contextmanager
    def get_connection(self):
        """Get database connection"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.commit()
                conn.close()

# Global database instance
db_config = DatabaseConfig()

def get_connection():
    """Get database connection for legacy compatibility"""
    return db_config.get_connection()

def execute_query(query: str, params: tuple = ()) -> List[sqlite3.Row]:
    """Execute a SELECT query and return results"""
    with db_config.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def execute_update(query: str, params: tuple = ()) -> int:
    """Execute an INSERT, UPDATE, or DELETE query and return affected rows"""
    with db_config.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.rowcount