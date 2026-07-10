"""
Suppliers Management - Screenshot #7
"""
import tkinter as tk
from config.theme import THEME, FONTS

class SuppliersView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=THEME['card_bg'])
        self.setup_suppliers()
    
    def setup_suppliers(self):
        """Suppliers management UI"""
        title = tk.Label(self, text="Supplier Management", font=('Segoe UI', 24, 'bold'),
                        fg=THEME['text_primary'], bg=THEME['card_bg'])
        title.pack(pady=(30, 10))
        
        subtitle = tk.Label(self, text="Keep track of your medicine suppliers and their contact information.",
                           font=FONTS['body'], fg=THEME['text_secondary'], bg=THEME['card_bg'])
        subtitle.pack(pady=(0, 25))
        
        # Sample suppliers table
        table_frame = tk.Frame(self, bg='white', relief='solid', bd=1, height=500)
        table_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        suppliers = [
            {"name": "Global Pharma Inc.", "contact": "Sarah Connor", 
             "email": "global@pharma.com", "phone": "555-0101"},
            {"name": "MediHealth Distributors", "contact": "Mike Ross", 
             "email": "mike@medihealth.com", "phone": "555-0102"}
        ]
        
        # Headers
        header_frame = tk.Frame(table_frame, bg=THEME['text_primary'], height=45)
        header_frame.pack(fill='x')
        headers = ["Supplier Name", "Contact Person", "Email", "Phone", "Actions"]
        for header in headers:
            tk.Label(header_frame, text=header, font=FONTS['heading'], fg='white',
                    bg=THEME['text_primary']).pack(side='left', padx=15, pady=15)
        
        for supplier in suppliers:
            row_frame = tk.Frame(table_frame, bg='#F8F9FA', height=50)
            row_frame.pack(fill='x', pady=2)
            tk.Label(row_frame, text=supplier['name'], font=FONTS['body']).pack(side='left', padx=20, pady=15)
            tk.Label(row_frame, text=supplier['contact'], font=FONTS['body']).pack(side='left', padx=10, pady=15)
            tk.Label(row_frame, text=supplier['email'], font=FONTS['body']).pack(side='left', padx=10, pady=15)
            tk.Label(row_frame, text=supplier['phone'], font=FONTS['body']).pack(side='left', padx=10, pady=15)
            tk.Button(row_frame, text="⋮", font=('Segoe UI', 14), bg='#F8F9FA', 
                     fg=THEME['text_secondary'], relief='flat').pack(side='right', padx=20, pady=15)
