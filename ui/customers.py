"""
Customers Management - Screenshot #4
"""
import tkinter as tk
from config.theme import THEME, FONTS

class CustomersView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=THEME['card_bg'])
        self.setup_customers()
    
    def setup_customers(self):
        """Customers management UI"""
        # Header
        title = tk.Label(self, text="Customer Management", font=('Segoe UI', 24, 'bold'),
                        fg=THEME['text_primary'], bg=THEME['card_bg'])
        title.pack(pady=(30, 10))
        
        subtitle = tk.Label(self, text="View and manage customer details and their transaction history.",
                           font=FONTS['body'], fg=THEME['text_secondary'], bg=THEME['card_bg'])
        subtitle.pack(pady=(0, 25))
        
        # Placeholder table
        table_frame = tk.Frame(self, bg='white', relief='solid', bd=1, height=500)
        table_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Sample customers data (screenshot #4)
        customers = [
            {"name": "John Doe", "email": "john@example.com", "phone": "123-456-7890", "total": "₹125.75"},
            {"name": "Jane Smith", "email": "jane@example.com", "phone": "098-765-4321", "total": "₹89.50"}
        ]
        
        # Headers
        header_frame = tk.Frame(table_frame, bg=THEME['text_primary'], height=45)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        headers = ["Name", "Email", "Phone", "Total Spent", "Actions"]
        for header in headers:
            lbl = tk.Label(header_frame, text=header, font=FONTS['heading'],
                          fg='white', bg=THEME['text_primary'])
            lbl.pack(side='left', padx=15, pady=15)
        
        # Customer rows
        for customer in customers:
            row_frame = tk.Frame(table_frame, bg='#F8F9FA', height=50)
            row_frame.pack(fill='x', pady=2)
            
            tk.Label(row_frame, text=customer['name'], font=FONTS['body']).pack(side='left', padx=20, pady=15)
            tk.Label(row_frame, text=customer['email'], font=FONTS['body']).pack(side='left', padx=10, pady=15)
            tk.Label(row_frame, text=customer['phone'], font=FONTS['body']).pack(side='left', padx=10, pady=15)
            tk.Label(row_frame, text=customer['total'], font=FONTS['body']).pack(side='left', padx=10, pady=15)
            actions_btn = tk.Button(row_frame, text="⋮", font=('Segoe UI', 14),
                                  bg='#F8F9FA', fg=THEME['text_secondary'], relief='flat')
            actions_btn.pack(side='right', padx=20, pady=15)
