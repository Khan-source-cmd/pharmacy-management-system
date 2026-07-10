"""
New Sale / Billing Screen - PERFECT MATCH screenshot #3
Create Invoice (left) + Bill Summary (right) - COMPLETE RECREATION
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.theme import THEME, FONTS
from config.database import get_connection
from config.constants import TAX_RATE
from datetime import datetime

class SalesView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#F8F9FA')
        self.bill_items = []
        self.total = 0.0
        self.subtotal = 0.0
        self.tax_amount = 0.0
        self.discount = 0.0
        self.setup_ui()
    
    def setup_ui(self):
        """Complete UI recreation - matches screenshot perfectly"""
        
        # MAIN HEADER
        header = tk.Label(self, text="New Sale", font=('Segoe UI', 28, 'bold'), 
                         fg='#2C3E50', bg='#F8F9FA')
        header.pack(pady=(30, 10))
        
        subtitle = tk.Label(self, text="Create a new invoice for a customer.", 
                           font=('Segoe UI', 14), fg='#7F8C8D', bg='#F8F9FA')
        subtitle.pack(pady=(0, 40))
        
        # MAIN CONTAINER (2 columns)
        main_container = tk.Frame(self, bg='#F8F9FA')
        main_container.pack(fill='both', expand=True, padx=40, pady=20)
        
        # LEFT PANEL - Create Invoice (600px wide)
        left_panel = tk.LabelFrame(main_container, text="Create Invoice", 
                                  font=('Segoe UI', 16, 'bold'), fg='#2C3E50',
                                  bg='white', relief='solid', bd=2, padx=30, pady=25)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 25), pady=10)
        left_panel.pack_propagate(False)
        left_panel.configure(width=650)
        
        self.setup_left_panel(left_panel)
        
        # RIGHT PANEL - Bill Summary (350px wide)
        right_panel = tk.LabelFrame(main_container, text="Bill Summary", 
                                   font=('Segoe UI', 16, 'bold'), fg='#2C3E50',
                                   bg='white', relief='solid', bd=2, padx=25, pady=25)
        right_panel.pack(side='right', fill='y', pady=10)
        right_panel.pack_propagate(False)
        right_panel.configure(width=380)
        
        self.setup_right_panel(right_panel)
    
    def setup_left_panel(self, parent):
        """Left panel - medicine input + bill table"""
        
        # Input row
        input_frame = tk.Frame(parent, bg='white')
        input_frame.pack(fill='x', pady=(0, 25))
        
        # Medicine dropdown
        tk.Label(input_frame, text="Medicine:", font=('Segoe UI', 12, 'bold'),
                fg='#2C3E50', bg='white').grid(row=0, column=0, sticky='w', padx=(0, 10))
        
        self.medicine_var = tk.StringVar()
        self.medicine_combo = ttk.Combobox(input_frame, textvariable=self.medicine_var,
                                     font=('Segoe UI', 11), width=28, state='readonly')
        self.medicine_combo.grid(row=0, column=1, padx=(0, 15), pady=5, sticky='w')
        self.load_medicines()
        
        # Quantity
        tk.Label(input_frame, text="Qty:", font=('Segoe UI', 12, 'bold'),
                fg='#2C3E50', bg='white').grid(row=0, column=2, sticky='w', padx=(0, 8))
        
        self.qty_var = tk.StringVar(value="1")
        qty_entry = tk.Entry(input_frame, textvariable=self.qty_var, width=6,
                            font=('Segoe UI', 11), relief='solid', bd=1, bg='#F8F9FA')
        qty_entry.grid(row=0, column=3, sticky='w', padx=(0, 20))
        
        # Buttons
        add_btn = tk.Button(input_frame, text="Add to Bill", font=('Segoe UI', 11, 'bold'),
                           bg='#27AE60', fg='white', relief='flat', padx=30, pady=8,
                           cursor='hand2', command=self.add_to_bill)
        add_btn.grid(row=0, column=4, sticky='w', padx=(0, 15))
        
        clear_btn = tk.Button(input_frame, text="Clear Bill", font=('Segoe UI', 10),
                             bg='#95A5A6', fg='white', relief='flat', padx=25, pady=8,
                             cursor='hand2', command=self.clear_bill)
        clear_btn.grid(row=0, column=5, sticky='w')
        
        # BILL TABLE
        table_container = tk.Frame(parent, bg='white', relief='solid', bd=1)
        table_container.pack(fill='both', expand=True, pady=(10, 0))
        
        self.table_header = tk.Frame(table_container, bg='#34495E', height=50)
        self.table_header.pack(fill='x')
        self.table_header.pack_propagate(False)
        
        # Create table headers
        self.create_table_headers()
        
        self.table_body = tk.Frame(table_container, bg='white')
        self.table_body.pack(fill='both', expand=True)
        
        # Initial empty state
        self.show_empty_state()
    
    def create_table_headers(self):
        """Create PERFECTLY VISIBLE table headers"""
        headers = [
            ("Medicine", 0, True),   # expand=True
            ("Qty", 8, False),
            ("Price", 10, False),
            ("Total", 10, False)
        ]
        
        for text, width, expand in headers:
            lbl = tk.Label(self.table_header, text=text, font=('Segoe UI', 12, 'bold'),
                          fg='white', bg='#34495E', width=width)
            if expand:
                lbl.pack(side='left', fill='x', expand=True, padx=(15, 10), pady=16, anchor='n')
            else:
                lbl.pack(side='left', padx=15, pady=16, anchor='n')
    
    def show_empty_state(self):
        """Show 'No items' message"""
        self.empty_label = tk.Label(self.table_body, text="No items in the bill.",
                                   font=('Segoe UI', 14), fg='#95A5A6', bg='white')
        self.empty_label.pack(expand=True)
    
    def setup_right_panel(self, parent):
        """Right panel - customer + totals"""
        
        # Customer
        tk.Label(parent, text="Customer:", font=('Segoe UI', 12, 'bold'),
                fg='#2C3E50', bg='white').pack(anchor='w', pady=(0, 5))
        
        self.customer_var = tk.StringVar(value="Walk-in Customer")
        customer_combo = ttk.Combobox(parent, textvariable=self.customer_var,
                                     font=('Segoe UI', 11), width=25, state='readonly')
        customer_combo['values'] = ['Walk-in Customer', 'John Doe', 'Jane Smith']
        customer_combo.pack(fill='x', pady=(0, 25))
        
        # Totals container
        totals_container = tk.Frame(parent, bg='white')
        totals_container.pack(fill='x', pady=(0, 20))
        
        # Subtotal
        subtotal_frame = tk.Frame(totals_container, bg='white')
        subtotal_frame.pack(fill='x', pady=3)
        tk.Label(subtotal_frame, text="Subtotal:", font=('Segoe UI', 12),
                fg='#2C3E50', bg='white').pack(side='left')
        self.subtotal_label = tk.Label(subtotal_frame, text="₹0.00", 
                                      font=('Segoe UI', 12, 'bold'), fg='#27AE60')
        self.subtotal_label.pack(side='right')
        
        # Tax
        tax_frame = tk.Frame(totals_container, bg='white')
        tax_frame.pack(fill='x', pady=3)
        tk.Label(tax_frame, text=f"Tax ({int(TAX_RATE*100)}%):", font=('Segoe UI', 12),
                fg='#2C3E50', bg='white').pack(side='left')
        self.tax_label = tk.Label(tax_frame, text="₹0.00", 
                                 font=('Segoe UI', 12, 'bold'), fg='#27AE60')
        self.tax_label.pack(side='right')
        
        # Discount
        disc_frame = tk.Frame(totals_container, bg='white')
        disc_frame.pack(fill='x', pady=3)
        tk.Label(disc_frame, text="Discount:", font=('Segoe UI', 12),
                fg='#2C3E50', bg='white').pack(side='left')
        self.discount_var = tk.StringVar(value="0.00")
        disc_entry = tk.Entry(disc_frame, textvariable=self.discount_var, width=10,
                             font=('Segoe UI', 11), relief='solid', bd=1, bg='#F8F9FA')
        disc_entry.pack(side='right', padx=(0, 5))
        disc_entry.bind('<KeyRelease>', self.update_totals)
        
        # TOTAL LINE (highlighted)
        total_line = tk.Frame(totals_container, bg='#ECF0F1', relief='solid', bd=1)
        total_line.pack(fill='x', pady=(15, 0))
        tk.Label(total_line, text="Total:", font=('Segoe UI', 16, 'bold'),
                fg='#2C3E50', bg='#ECF0F1').pack(side='left', padx=10, pady=12)
        self.total_label = tk.Label(total_line, text="₹0.00", 
                                   font=('Segoe UI', 16, 'bold'), fg='#27AE60')
        self.total_label.pack(side='right', padx=15, pady=12)
        
        # COMPLETE BUTTON
        complete_btn = tk.Button(parent, text="Complete Sale & Print Invoice",
                                font=('Segoe UI', 13, 'bold'), bg='#27AE60',
                                fg='white', relief='flat', height=2, cursor='hand2',
                                command=self.complete_sale)
        complete_btn.pack(fill='x', pady=(25, 0))
    
    def add_to_bill(self):
        """Add item to bill"""
        medicine = self.medicine_var.get()
        try:
            qty = int(self.qty_var.get() or 0)
        except:
            messagebox.showwarning("Error", "Invalid quantity")
            return
        
        if not medicine or qty <= 0:
            messagebox.showwarning("Invalid", "Select medicine and valid quantity")
            return
        
        # Parse medicine data
        parts = medicine.split(' - ')
        name = parts[0]
        price = float(parts[1].replace('₹', ''))
        line_total = price * qty
        
        self.bill_items.append({
            'name': name,
            'medicine': medicine,
            'quantity': qty,
            'price': price,
            'total': line_total
        })
        
        self.refresh_table()
        self.update_totals()
    
    def refresh_table(self):
        """Refresh bill table with perfect headers + data"""
        # Clear body
        for widget in self.table_body.winfo_children():
            widget.destroy()
        
        if not self.bill_items:
            self.show_empty_state()
            return
        
        # Create data rows
        for item in self.bill_items:
            row = tk.Frame(self.table_body, bg='white', relief='solid', bd=1)
            row.pack(fill='x', pady=2)
            
            # Medicine column (expand)
            med_label = tk.Label(row, text=item['name'], font=('Segoe UI', 11),
                               fg='#2C3E50', bg='white', anchor='w')
            med_label.pack(side='left', fill='x', expand=True, padx=(15, 10), pady=12)
            
            # Qty
            tk.Label(row, text=str(item['quantity']), font=('Segoe UI', 11, 'bold'),
                    fg='#2C3E50', bg='white', width=8).pack(side='left', padx=10, pady=12)
            
            # Price
            tk.Label(row, text=f"₹{item['price']:.2f}", font=('Segoe UI', 11, 'bold'),
                    fg='#27AE60', bg='white', width=10).pack(side='left', padx=10, pady=12)
            
            # Total (right aligned, green)
            tk.Label(row, text=f"₹{item['total']:.2f}", font=('Segoe UI', 11, 'bold'),
                    fg='#27AE60', bg='white', width=10).pack(side='right', padx=15, pady=12)
    
    def update_totals(self, event=None):
        """Update totals display"""
        self.subtotal = sum(item['total'] for item in self.bill_items)
        self.tax_amount = self.subtotal * TAX_RATE
        self.discount = float(self.discount_var.get() or 0)
        self.total = self.subtotal + self.tax_amount - self.discount
        
        self.subtotal_label.config(text=f"₹{self.subtotal:.2f}")
        self.tax_label.config(text=f"₹{self.tax_amount:.2f}")
        self.total_label.config(text=f"₹{self.total:.2f}")
    
    def load_medicines(self):
        """Load medicines from DB"""
        try:
            with get_connection() as conn:
                cursor = conn.execute("SELECT name, price FROM medicines ORDER BY name")
                medicines = [f"{row[0]} - ₹{row[1]:.2f}" for row in cursor.fetchall()]
                self.medicine_combo['values'] = medicines or [
                    'Paracetamol 500mg - ₹1.50', 'Amoxicillin 250mg - ₹3.75'
                ]
        except:
            self.medicine_combo['values'] = ['Amoxicillin 250mg - ₹3.75']
    
    def clear_bill(self):
        """Clear bill"""
        self.bill_items.clear()
        self.discount_var.set("0.00")
        self.refresh_table()
        self.update_totals()
    
    def complete_sale(self):
        """Complete sale transaction"""
        if not self.bill_items:
            messagebox.showwarning("Empty", "Add items first")
            return
        
        try:
            customer_name = self.customer_var.get()
            customer_id = None
            
            if customer_name != "Walk-in Customer":
                with get_connection() as conn:
                    cursor = conn.execute("SELECT id FROM customers WHERE name=?", (customer_name,))
                    result = cursor.fetchone()
                    if result:
                        customer_id = result[0]
            
            # Prepare items
            items = []
            for item in self.bill_items:
                with get_connection() as conn:
                    cursor = conn.execute("SELECT id FROM medicines WHERE name=?", 
                                        (item['name'],))
                    med_id = cursor.fetchone()
                    if med_id:
                        items.append((med_id[0], item['quantity'], item['price']))
            
            # Save to database
            with get_connection() as conn:
                invoice = f"INV{datetime.now().strftime('%Y%m%d')}{len(self.bill_items):03d}"
                conn.execute("""
                    INSERT INTO sales (invoice_number, customer_id, subtotal, tax_amount, 
                                     discount_amount, total_amount) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (invoice, customer_id, self.subtotal, self.tax_amount, 
                      self.discount, self.total))
                
                messagebox.showinfo("Success!", f"Sale complete!\nInvoice: {invoice}")
            
            self.clear_bill()
            
        except Exception as e:
            messagebox.showerror("Error", f"Sale failed: {e}")

# Test runner
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Pharmacy Sales")
    root.geometry("1200x750")
    root.minsize(1000, 600)
    
    app = SalesView(root)
    app.pack(fill='both', expand=True, padx=20, pady=20)
    
    root.mainloop()
