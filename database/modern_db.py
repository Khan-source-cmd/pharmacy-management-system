#!/usr/bin/env python3
"""
Modern Database Layer with SQLite3 and Advanced Features
- Connection pooling
- Transaction management
- Query builders
- Data validation
- Audit logging
"""
import sqlite3
import bcrypt
import json
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import List, Dict, Optional, Any
import threading
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import from our new config
from config.constants import DB_PATH

class DatabaseManager:
    """Advanced database manager with connection pooling and transaction support"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.connection_pool = []
        self.pool_lock = threading.Lock()
        self.max_connections = 10
        self.init_database()
    
    def init_database(self):
        """Initialize database with all tables and sample data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create tables
                self._create_tables(cursor)
                
                # Run migrations
                self._run_migrations(cursor)
                
                # Insert sample data if tables are empty
                self._insert_sample_data(cursor)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _create_tables(self, cursor):
        """Create all database tables"""
        
        # Users table
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
        
        # Medicines table
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
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
            )
        """)
        
        # Customers table
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
        
        # Suppliers table
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
        
        # Sales table
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
                created_by_user_id INTEGER,
                FOREIGN KEY(customer_id) REFERENCES customers(id),
                FOREIGN KEY(created_by_user_id) REFERENCES users(id)
            )
        """)
        
        # Sale items table
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
        
        # Purchases table (for inventory tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER,
                medicine_id INTEGER,
                purchase_date DATE DEFAULT CURRENT_DATE,
                quantity INTEGER NOT NULL,
                unit_cost DECIMAL(10,2) NOT NULL,
                total_cost DECIMAL(10,2) NOT NULL,
                batch_number TEXT,
                expiry_date DATE,
                received_by_user_id INTEGER,
                FOREIGN KEY(supplier_id) REFERENCES suppliers(id),
                FOREIGN KEY(medicine_id) REFERENCES medicines(id),
                FOREIGN KEY(received_by_user_id) REFERENCES users(id)
            )
        """)
        
        # Audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id INTEGER,
                action TEXT NOT NULL,
                old_values TEXT,
                new_values TEXT,
                user_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_medicines_expiry ON medicines(expiry_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id)")
        
        # Create triggers for audit logging
        self._create_audit_triggers(cursor)
    
    def _create_audit_triggers(self, cursor):
        """Create triggers for automatic audit logging"""
        
        # Medicine audit trigger
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS medicine_audit_trigger
            AFTER UPDATE ON medicines
            FOR EACH ROW
            BEGIN
                INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, user_id)
                VALUES ('medicines', NEW.id, 'UPDATE', 
                       json_object('quantity', OLD.quantity, 'price', OLD.price),
                       json_object('quantity', NEW.quantity, 'price', NEW.price),
                       (SELECT id FROM users WHERE email = 'system'));
            END;
        """)
    
    def _run_migrations(self, cursor):
        """Run database migrations"""
        try:
            # Check if pharmacy_settings table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='pharmacy_settings'
            """)
            
            if not cursor.fetchone():
                # Run pharmacy settings migration
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pharmacy_settings (
                        id INTEGER PRIMARY KEY,
                        pharmacy_name TEXT NOT NULL DEFAULT 'YOUR PHARMACY NAME',
                        address TEXT NOT NULL DEFAULT 'Your Address Here',
                        city TEXT NOT NULL DEFAULT 'City',
                        pincode TEXT NOT NULL DEFAULT 'PINCODE',
                        gstin TEXT DEFAULT '',
                        license_number TEXT DEFAULT '',
                        phone TEXT DEFAULT '',
                        email TEXT DEFAULT '',
                        logo_path TEXT DEFAULT '',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert default pharmacy settings
                cursor.execute("""
                    INSERT OR REPLACE INTO pharmacy_settings (
                        id, pharmacy_name, address, city, pincode, gstin, license_number, phone, email
                    ) VALUES (
                        1, 'YOUR PHARMACY NAME', 'Your Address Here', 'City', 'PINCODE', '', '', '', ''
                    )
                """)
                
                # Create trigger to update updated_at timestamp
                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS update_pharmacy_settings_timestamp
                    AFTER UPDATE ON pharmacy_settings
                    FOR EACH ROW
                    BEGIN
                        UPDATE pharmacy_settings SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                    END
                """)
                
                logger.info("Pharmacy settings migration completed")
                
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
    
    def _insert_sample_data(self, cursor):
        """Insert sample data for demonstration"""
        
        # Check if users table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
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
        
        # Check if suppliers table is empty
        cursor.execute("SELECT COUNT(*) FROM suppliers")
        if cursor.fetchone()[0] == 0:
            suppliers = [
                ("Global Pharma Inc.", "Sarah Connor", "sarah@globalpharma.com", "555-0101", "123 Pharma St"),
                ("MediHealth Distributors", "Mike Ross", "mike@medihealth.com", "555-0102", "456 Health Ave"),
                ("HealthPlus Supplies", "Lisa Thompson", "lisa@healthplus.com", "555-0103", "789 Medical Blvd"),
            ]
            
            for sup in suppliers:
                cursor.execute("""
                    INSERT INTO suppliers (name, contact_person, email, phone, address)
                    VALUES (?, ?, ?, ?, ?)
                """, sup)
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool"""
        conn = None
        try:
            with self.pool_lock:
                if self.connection_pool:
                    conn = self.connection_pool.pop()
                else:
                    conn = sqlite3.connect(self.db_path)
                    conn.row_factory = sqlite3.Row
            
            yield conn
            
            # Only commit if no exception occurred
            conn.commit()
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                with self.pool_lock:
                    if len(self.connection_pool) < self.max_connections:
                        self.connection_pool.append(conn)
                    else:
                        conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT, UPDATE, or DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, email, role, is_active, last_login, password_hash
                    FROM users 
                    WHERE email = ? AND is_active = 1
                """, (email,))

                user = cursor.fetchone()
                if user and bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
                    # Update last login
                    cursor.execute("""
                        UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                    """, (user['id'],))
                    
                    return dict(user)
                return None
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
    
    def get_medicines(self, search: str = "", category: str = "", low_stock: bool = False) -> List[Dict]:
        """Get medicines with optional filtering"""
        query = """
            SELECT m.id, m.name, m.category, m.batch_number, m.expiry_date,
                   m.quantity, m.reorder_level, m.price, m.created_at,
                   s.name as supplier_name,
                   m.drawer_number,
                   m.shelf_location,
                   CASE 
                       WHEN m.quantity <= m.reorder_level THEN 'Low Stock'
                       WHEN m.quantity = 0 THEN 'Out of Stock'
                       ELSE 'In Stock'
                   END as stock_status,
                   CASE 
                       WHEN m.expiry_date < date('now') THEN 'Expired'
                       WHEN m.expiry_date <= date('now', '+30 days') THEN 'Near Expiry'
                       ELSE 'Valid'
                   END as expiry_status
            FROM medicines m
            LEFT JOIN suppliers s ON m.supplier_id = s.id
            WHERE 1=1
        """
        params = []
        
        if search:
            query += " AND (m.name LIKE ? OR m.category LIKE ? OR m.batch_number LIKE ?)"
            search_like = f"%{search}%"
            params.extend([search_like, search_like, search_like])
        
        if category:
            query += " AND m.category = ?"
            params.append(category)
        
        if low_stock:
            query += " AND m.quantity <= m.reorder_level"
        
        query += " ORDER BY m.name"
        
        results = self.execute_query(query, tuple(params))
        return [dict(row) for row in results]
    
    def get_sales_summary(self, days: int = 7) -> Dict:
        """Get sales summary for dashboard"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total revenue
                cursor.execute("""
                    SELECT COALESCE(SUM(total_amount), 0) as total_revenue
                    FROM sales 
                    WHERE sale_date >= date('now', '-%s days')
                """ % days)
                total_revenue = cursor.fetchone()[0]
                
                # Total medicines
                cursor.execute("SELECT COUNT(*) FROM medicines")
                total_medicines = cursor.fetchone()[0]
                
                # Low stock count
                cursor.execute("""
                    SELECT COUNT(*) FROM medicines 
                    WHERE quantity <= reorder_level
                """)
                low_stock_count = cursor.fetchone()[0]
                
                # Expired medicines
                cursor.execute("""
                    SELECT COUNT(*) FROM medicines 
                    WHERE expiry_date < date('now')
                """)
                expired_count = cursor.fetchone()[0]
                
                return {
                    'total_revenue': total_revenue,
                    'total_medicines': total_medicines,
                    'low_stock_count': low_stock_count,
                    'expired_count': expired_count
                }
        except Exception as e:
            logger.error(f"Failed to get sales summary: {e}")
            return {'total_revenue': 0, 'total_medicines': 0, 'low_stock_count': 0, 'expired_count': 0}
    
    def create_sale(self, customer_id: Optional[int], items: List[Dict], 
                   discount: float = 0, payment_method: str = "cash", user_id: int = 1) -> int:
        """Create a new sale with items"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Generate invoice number
                invoice_number = f"INV{datetime.now().strftime('%Y%m%d')}{self._get_next_invoice_suffix(cursor)}"
                
                # Calculate totals
                subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
                tax_amount = subtotal * 0.05  # 5% tax
                total_amount = subtotal + tax_amount - discount
                
                # Insert sale
                cursor.execute("""
                    INSERT INTO sales (invoice_number, customer_id, subtotal, tax_amount, 
                                     discount_amount, total_amount, payment_method, created_by_user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (invoice_number, customer_id, subtotal, tax_amount, discount, total_amount, 
                      payment_method, user_id))
                
                # Get the sale ID immediately after insertion
                sale_id = cursor.lastrowid
                
                # Validate that we got a valid sale ID
                if not sale_id:
                    raise Exception("Failed to get sale ID after insertion")
                
                # Insert sale items and update inventory
                for item in items:
                    line_total = item['quantity'] * item['unit_price']
                    
                    cursor.execute("""
                        INSERT INTO sale_items (sale_id, medicine_id, quantity, unit_price, line_total)
                        VALUES (?, ?, ?, ?, ?)
                    """, (sale_id, item['medicine_id'], item['quantity'], item['unit_price'], line_total))
                    
                    # Update medicine quantity
                    cursor.execute("""
                        UPDATE medicines SET quantity = quantity - ? WHERE id = ?
                    """, (item['quantity'], item['medicine_id']))
                
                # Update customer total spent
                if customer_id:
                    cursor.execute("""
                        UPDATE customers SET total_spent = total_spent + ?, last_purchase = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (total_amount, customer_id))
                
                # Verify the sale was created successfully
                cursor.execute("SELECT id FROM sales WHERE id = ?", (sale_id,))
                if not cursor.fetchone():
                    raise Exception(f"Sale {sale_id} not found after creation")
                
                return sale_id
                
        except Exception as e:
            logger.error(f"Failed to create sale: {e}")
            raise
    
    def _get_next_invoice_suffix(self, cursor) -> str:
        """Get next invoice number suffix"""
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM sales 
                WHERE date(sale_date) = date('now')
            """)
            result = cursor.fetchone()
            count = (result[0] if result else 0) + 1
            return f"{count:03d}"
        except Exception as e:
            logger.error(f"Error getting invoice suffix: {e}")
            # Fallback to timestamp-based suffix
            return datetime.now().strftime("%H%M%S")
    
    def get_recent_sales(self, limit: int = 10) -> List[Dict]:
        """Get recent sales for dashboard"""
        query = """
            SELECT s.invoice_number, 
                   COALESCE(c.name, 'Walk-in Customer') as customer_name,
                   s.sale_date, s.total_amount
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.id
            ORDER BY s.sale_date DESC
            LIMIT ?
        """
        results = self.execute_query(query, (limit,))
        return [dict(row) for row in results]
    
    def get_predictive_stock_analysis(self) -> List[Dict]:
        """Get predictive stock analysis"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Calculate average daily sales for each medicine (last 30 days)
                query = """
                    SELECT m.id, m.name, m.quantity,
                           COALESCE(AVG(sd.daily_sales), 0) as avg_daily_sales
                    FROM medicines m
                    LEFT JOIN (
                        SELECT si.medicine_id, 
                               SUM(si.quantity) / 30.0 as daily_sales
                        FROM sale_items si
                        JOIN sales s ON si.sale_id = s.id
                        WHERE s.sale_date >= date('now', '-30 days')
                        GROUP BY si.medicine_id
                    ) sd ON m.id = sd.medicine_id
                    GROUP BY m.id, m.name, m.quantity
                """
                
                results = cursor.execute(query).fetchall()
                analysis = []
                
                for row in results:
                    medicine_id = row[0]
                    name = row[1]
                    current_stock = row[2]
                    avg_daily_sales = row[3] if row[3] else 0
                    
                    if avg_daily_sales > 0:
                        days_until_out = current_stock / avg_daily_sales
                    else:
                        days_until_out = 999  # Never run out if no sales
                    
                    # Determine status
                    if days_until_out < 7:
                        status = "🔴 Critical"
                    elif days_until_out < 15:
                        status = "🟡 Review"
                    else:
                        status = "🟢 OK"
                    
                    analysis.append({
                        'medicine_name': name,
                        'current_stock': current_stock,
                        'avg_daily_sales': round(avg_daily_sales, 1),
                        'days_until_out': f"{int(days_until_out)} days",
                        'status': status
                    })
                
                return analysis
                
        except Exception as e:
            logger.error(f"Failed to get predictive analysis: {e}")
            return []

# Global database instance
db = DatabaseManager()

# Convenience functions for the UI

def log_audit(table_name: str, record_id: Optional[int], action: str, old_values: Optional[Dict] = None, new_values: Optional[Dict] = None, user_id: Optional[int] = None) -> bool:
    """Insert a record into the audit_log table."""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                table_name,
                record_id,
                action,
                json.dumps(old_values) if old_values is not None else None,
                json.dumps(new_values) if new_values is not None else None,
                user_id,
            ))
        return True
    except Exception as e:
        logger.error(f"Error logging audit entry: {e}")
        return False

def authenticate_user(email: str, password: str):
    return db.authenticate_user(email, password)

def get_medicines(search: str = "", category: str = "", low_stock: bool = False):
    return db.get_medicines(search, category, low_stock)

def get_sales_summary(days: int = 7):
    return db.get_sales_summary(days)

def create_sale(customer_id, items, discount=0, payment_method="cash", user_id=1):
    return db.create_sale(customer_id, items, discount, payment_method, user_id)

def get_recent_sales(limit: int = 10):
    return db.get_recent_sales(limit)

def get_predictive_stock_analysis():
    return db.get_predictive_stock_analysis()

def create_medicine(name, category, quantity, price, expiry_date=None, batch_number=None, supplier_id=None, drawer_number=None, shelf_location=None):
    """Create a new medicine record"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO medicines (name, category, batch_number, expiry_date, quantity, price, supplier_id, drawer_number, shelf_location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, category, batch_number, expiry_date, quantity, price, supplier_id, drawer_number, shelf_location))
            # Don't call conn.commit() here - the context manager handles it
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error creating medicine: {e}")
        return None

def update_medicine(medicine_id, name=None, category=None, quantity=None, price=None, expiry_date=None):
    """Update medicine record"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            updates = []
            params = []
            
            if name:
                updates.append("name = ?")
                params.append(name)
            if category:
                updates.append("category = ?")
                params.append(category)
            if quantity is not None:
                updates.append("quantity = ?")
                params.append(quantity)
            if price is not None:
                updates.append("price = ?")
                params.append(price)
            if expiry_date:
                updates.append("expiry_date = ?")
                params.append(expiry_date)
            
            if updates:
                params.append(medicine_id)
                query = f"UPDATE medicines SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount > 0
            return False
    except Exception as e:
        logger.error(f"Error updating medicine: {e}")
        return False

def delete_medicine(medicine_id):
    """Delete medicine record"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error deleting medicine: {e}")
        return False

def get_customers(search: str = "") -> List[Dict]:
    """Get customers with optional filtering"""
    query = """
        SELECT id, name, email, phone, address, total_spent
        FROM customers
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (name LIKE ? OR email LIKE ? OR phone LIKE ?)"
        search_like = f"%{search}%"
        params.extend([search_like, search_like, search_like])

    query += " ORDER BY name"

    results = db.execute_query(query, tuple(params))
    return [dict(row) for row in results]

def get_suppliers(search: str = "") -> List[Dict]:
    """Get suppliers with optional filtering"""
    query = """
        SELECT id, name, contact_person, email, phone
        FROM suppliers
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (name LIKE ? OR contact_person LIKE ? OR email LIKE ? OR phone LIKE ?)"
        search_like = f"%{search}%"
        params.extend([search_like, search_like, search_like, search_like])

    query += " ORDER BY name"

    results = db.execute_query(query, tuple(params))
    return [dict(row) for row in results]

def create_customer(name: str, email: str, phone: str, address: str = "") -> int:
    """Create a new customer record"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO customers (name, email, phone, address)
                VALUES (?, ?, ?, ?)
            """, (name, email, phone, address))
            # Don't call conn.commit() here - the context manager handles it
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        return None

def create_supplier(name: str, contact_person: str, email: str, phone: str) -> int:
    """Create a new supplier record"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO suppliers (name, contact_person, email, phone)
                VALUES (?, ?, ?, ?)
            """, (name, contact_person, email, phone))
            # Don't call conn.commit() here - the context manager handles it
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error creating supplier: {e}")
        return None

def get_inventory_summary():
    """Get current inventory summary with real-time data"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    m.name,
                    m.category,
                    m.quantity,
                    m.expiry_date,
                    m.reorder_level,
                    s.name as supplier_name
                FROM medicines m
                LEFT JOIN suppliers s ON m.supplier_id = s.id
                ORDER BY m.name
            """)
            
            medicines = []
            for row in cursor.fetchall():
                # Determine stock status
                quantity = row[2]
                reorder_level = row[4] if row[4] else 10  # Default reorder level
                
                if quantity <= 0:
                    stock_status = "Out of Stock"
                elif quantity <= reorder_level:
                    stock_status = "Low Stock"
                else:
                    stock_status = "In Stock"
                
                # Determine expiry status
                expiry_date = row[3]
                expiry_status = "Valid"
                if expiry_date:
                    try:
                        from datetime import datetime
                        expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
                        today = datetime.now()
                        days_diff = (expiry - today).days
                        
                        if days_diff < 0:
                            expiry_status = "Expired"
                        elif days_diff <= 90:  # 3 months
                            expiry_status = "Near Expiry"
                    except:
                        pass
                
                medicines.append({
                    'name': row[0],
                    'category': row[1],
                    'quantity': quantity,
                    'stock_status': stock_status,
                    'expiry_status': expiry_status,
                    'expiry_date': expiry_date,
                    'reorder_level': reorder_level,
                    'supplier_name': row[5] if row[5] else 'N/A'
                })
            
            return medicines
    except Exception as e:
        logger.error(f"Error getting inventory summary: {e}")
        return []

# Add missing report-specific functions
def get_daily_sales_report(start_date: str, end_date: str) -> List[Dict]:
    """Get daily sales report data"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DATE(sale_date) as date, 
                       COUNT(*) as transactions,
                       SUM(total_amount) as total_revenue,
                       AVG(total_amount) as avg_transaction
                FROM sales 
                WHERE DATE(sale_date) BETWEEN ? AND ?
                GROUP BY DATE(sale_date)
                ORDER BY date DESC
            """, (start_date, end_date))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error getting daily sales report: {e}")
        return []

def get_monthly_sales_report(start_date: str, end_date: str) -> List[Dict]:
    """Get monthly sales report data"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT strftime('%Y-%m', sale_date) as month,
                       COUNT(*) as transactions,
                       SUM(total_amount) as total_revenue,
                       AVG(total_amount) as avg_transaction
                FROM sales 
                WHERE DATE(sale_date) BETWEEN ? AND ?
                GROUP BY strftime('%Y-%m', sale_date)
                ORDER BY month DESC
            """, (start_date, end_date))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error getting monthly sales report: {e}")
        return []

def get_customer_analytics_report(start_date: str, end_date: str) -> List[Dict]:
    """Get customer analytics report data"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.name, c.phone, COUNT(s.id) as transactions, 
                       SUM(s.total_amount) as total_spent,
                       AVG(s.total_amount) as avg_transaction
                FROM customers c
                LEFT JOIN sales s ON c.id = s.customer_id
                WHERE DATE(s.sale_date) BETWEEN ? AND ? OR s.id IS NULL
                GROUP BY c.id
                ORDER BY total_spent DESC
            """, (start_date, end_date))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error getting customer analytics report: {e}")
        return []

def get_purchase_history_report(start_date: str, end_date: str) -> List[Dict]:
    """Get purchase history report data"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.purchase_date, m.name, p.quantity, p.unit_cost, s.name as supplier
                FROM purchases p
                JOIN medicines m ON p.medicine_id = m.id
                JOIN suppliers s ON p.supplier_id = s.id
                WHERE DATE(p.purchase_date) BETWEEN ? AND ?
                ORDER BY p.purchase_date DESC
            """, (start_date, end_date))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error getting purchase history report: {e}")
        return []

def get_customer_purchase_history(search_term: str) -> Optional[Dict]:
    """
    Get customer's purchase history by phone number or name.
    This allows staff to look up what medicines a customer has purchased before.
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # First, try to find the customer by phone (exact match) or name (partial match)
            # Phone is more precise, so we prioritize that
            cursor.execute("""
                SELECT id, name, email, phone, address, total_spent, created_at, last_purchase
                FROM customers
                WHERE phone = ? OR name LIKE ?
                LIMIT 1
            """, (search_term, f"%{search_term}%"))
            
            customer = cursor.fetchone()
            
            if not customer:
                return None
            
            customer_id = customer[0]
            customer_data = {
                'id': customer_id,
                'name': customer[1],
                'email': customer[2],
                'phone': customer[3],
                'address': customer[4],
                'total_spent': customer[5],
                'created_at': customer[6],
                'last_purchase': customer[7],
                'purchases': []
            }
            
            # Now get all purchases for this customer
            cursor.execute("""
                SELECT s.id, s.invoice_number, s.sale_date, s.total_amount, s.payment_method
                FROM sales s
                WHERE s.customer_id = ?
                ORDER BY s.sale_date DESC
            """, (customer_id,))
            
            sales = cursor.fetchall()
            
            for sale in sales:
                sale_id = sale[0]
                
                # Get items for this sale
                cursor.execute("""
                    SELECT si.quantity, si.unit_price, si.line_total, m.name
                    FROM sale_items si
                    JOIN medicines m ON si.medicine_id = m.id
                    WHERE si.sale_id = ?
                """, (sale_id,))
                
                items = cursor.fetchall()
                items_list = []
                for item in items:
                    items_list.append({
                        'medicine_name': item[3],
                        'quantity': item[0],
                        'unit_price': item[1],
                        'line_total': item[2]
                    })
                
                customer_data['purchases'].append({
                    'sale_id': sale_id,
                    'invoice_number': sale[1],
                    'sale_date': sale[2],
                    'total_amount': sale[3],
                    'payment_method': sale[4],
                    'items': items_list
                })
            
            return customer_data
            
    except Exception as e:
        logger.error(f"Error getting customer purchase history: {e}")
        return None

def get_customer_purchase_history_summary(search_term: str) -> List[Dict]:
    """
    Get customer purchase history summary for the lookup table.
    Returns a list of customers with their purchase counts, total spent, and recent medicines.
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Search for customers by phone or name
            cursor.execute("""
                SELECT c.id, c.name, c.phone, c.total_spent
                FROM customers c
                WHERE c.phone LIKE ? OR c.name LIKE ?
                ORDER BY c.total_spent DESC
            """, (f"%{search_term}%", f"%{search_term}%"))
            
            customers = cursor.fetchall()
            results = []
            
            for customer in customers:
                customer_id = customer[0]
                name = customer[1]
                phone = customer[2]
                total_spent = customer[3]
                
                # Get purchase count
                cursor.execute("""
                    SELECT COUNT(*) FROM sales WHERE customer_id = ?
                """, (customer_id,))
                purchase_count = cursor.fetchone()[0]
                
                # Get recent medicines purchased (last 3 purchases)
                cursor.execute("""
                    SELECT DISTINCT m.name
                    FROM sales s
                    JOIN sale_items si ON s.id = si.sale_id
                    JOIN medicines m ON si.medicine_id = m.id
                    WHERE s.customer_id = ?
                    ORDER BY s.sale_date DESC
                    LIMIT 5
                """, (customer_id,))
                
                medicines = [row[0] for row in cursor.fetchall()]
                medicines_str = ", ".join(medicines) if medicines else "No medicines"
                
                results.append({
                    'id': customer_id,
                    'name': name,
                    'phone': phone,
                    'total_spent': total_spent,
                    'purchase_count': purchase_count,
                    'medicines': medicines_str
                })
            
            return results
            
    except Exception as e:
        logger.error(f"Error getting customer purchase history summary: {e}")
        return []
def get_all_users() -> List[Dict]:
    """Get all users (admin only)"""
    try:
        query = """
            SELECT id, email, role, is_active, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        """
        results = db.execute_query(query)
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return []

def create_user(email: str, password: str, role: str = "staff", performed_by: Optional[int] = None) -> int:
    """Create a new user with bcrypt-hashed password"""
    try:
        if role not in ["admin", "staff"]:
            raise ValueError("Role must be 'admin' or 'staff'")
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Hash the password
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            
            cursor.execute("""
                INSERT INTO users (email, password_hash, role, is_active)
                VALUES (?, ?, ?, 1)
            """, (email, password_hash, role))
            user_id = cursor.lastrowid
            
            # Audit log
            try:
                log_audit('users', user_id, 'CREATE', None,
                          {'email': email, 'role': role}, performed_by)
            except Exception:
                pass
            
            return user_id
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None

def delete_user(user_id: int, performed_by: Optional[int] = None) -> bool:
    """Delete a user (admin only)"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            success = cursor.rowcount > 0
            if success:
                try:
                    log_audit('users', user_id, 'DELETE', None, None, performed_by)
                except Exception:
                    pass
            return success
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return False

def update_user_password(user_id: int, new_password: str, performed_by: Optional[int] = None) -> bool:
    """Reset a user's password (admin only)"""
    try:
        password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET password_hash = ? WHERE id = ?
            """, (password_hash, user_id))
            success = cursor.rowcount > 0
            if success:
                try:
                    log_audit('users', user_id, 'PASSWORD_RESET', None, None, performed_by)
                except Exception:
                    pass
            return success
    except Exception as e:
        logger.error(f"Error updating user password: {e}")
        return False