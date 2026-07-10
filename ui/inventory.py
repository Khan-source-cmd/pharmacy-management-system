"""
Medicine Inventory - Screenshot #6
Name | Category | Stock Status | Expiry Status | Quantity | Price | Actions
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config.theme import THEME, FONTS
from config.database import get_connection, get_medicines
import sqlite3

class InventoryView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=THEME['card_bg'])
        self.medicines = []
        self.load_medicines()
        self.setup_inventory()
    
    def load_medicines(self):
        """Load medicines from database using new get_medicines function"""
        try:
            self.medicines = get_medicines()
        except Exception as e:
            print(f"Error loading medicines: {e}")
            self.medicines = []
    
    def setup_inventory(self):
        """Create inventory UI matching screenshot #6"""
        # Header
        header_frame = tk.Frame(self, bg=THEME['card_bg'])
        header_frame.pack(fill='x', pady=(25, 20))
        
        title = tk.Label(header_frame, text="Medicine Inventory", 
                        font=('Segoe UI', 24, 'bold'), fg=THEME['text_primary'],
                        bg=THEME['card_bg'])
        title.pack()
        
        subtitle = tk.Label(header_frame, text="Manage your pharmacy's medicine stock, including adding, editing, and tracking items.",
                           font=FONTS['body'], fg=THEME['text_secondary'], bg=THEME['card_bg'])
        subtitle.pack(pady=(8, 25))
        
        # Controls row
        controls_frame = tk.Frame(self, bg=THEME['card_bg'])
        controls_frame.pack(fill='x', pady=(0, 25))
        
        # Search box
        search_frame = tk.Frame(controls_frame, bg=THEME['card_bg'])
        search_frame.pack(side='left')
        tk.Label(search_frame, text="Search:", font=FONTS['heading'], 
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(side='left', padx=(0, 10))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               font=FONTS['body'], relief='solid', bd=1, width=25)
        search_entry.pack(side='left', padx=(0, 20))
        search_entry.bind('<KeyRelease>', self.filter_medicines)
        
        # Add Medicine button (green - matches screenshot)
        add_btn = tk.Button(controls_frame, text="Add Medicine", 
                           font=FONTS['heading'], bg=THEME['primary_green'],
                           fg='white', relief='flat', cursor='hand2', height=2,
                           command=self.show_add_dialog)
        add_btn.pack(side='right')
        add_btn.bind('<Enter>', lambda e: add_btn.configure(bg=THEME['hover_green']))
        add_btn.bind('<Leave>', lambda e: add_btn.configure(bg=THEME['primary_green']))
        
        # Inventory table with scrollbar
        table_container = tk.Frame(self, bg=THEME['card_bg'], relief='solid', bd=1)
        table_container.pack(fill='both', expand=True)
        
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(table_container, bg=THEME['card_bg'])
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=THEME['card_bg'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.refresh_table()
    
    def refresh_table(self):
        """Refresh inventory table"""
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Table header
        header_frame = tk.Frame(self.scrollable_frame, bg=THEME['text_primary'], height=45)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        headers = ["Name", "Category", "Drawer", "Shelf", "Stock Status", "Expiry Status", "Quantity", "Price", "Actions"]
        for i, header in enumerate(headers):
            lbl = tk.Label(header_frame, text=header, font=FONTS['heading'],
                          fg='white', bg=THEME['text_primary'], anchor='w')
            if i < 4:
                lbl.pack(side='left', padx=10, pady=15)
            elif i == 8:
                lbl.pack(side='right', padx=15, pady=15)
            else:
                lbl.pack(side='left', padx=10, pady=15)
        
        # All medicine rows (show all medicines now)
        for med in self.medicines:
            self.create_medicine_row(med)
    
    def create_medicine_row(self, medicine):
        """Create single medicine row"""
        row_frame = tk.Frame(self.scrollable_frame, height=50)
        row_frame.pack(fill='x', pady=2)
        
        # Row background (alternating)
        row_frame.configure(bg='#F8F9FA')
        
        # Name
        name_lbl = tk.Label(row_frame, text=medicine['name'], font=FONTS['body'],
                           fg=THEME['text_primary'], bg='#F8F9FA', anchor='w')
        name_lbl.pack(side='left', padx=20, pady=15)
        
        # Category
        cat_lbl = tk.Label(row_frame, text=medicine['category'], font=FONTS['body'],
                          fg=THEME['text_primary'], bg='#F8F9FA', anchor='w')
        cat_lbl.pack(side='left', padx=10, pady=15)
        
        # Drawer Number
        drawer_lbl = tk.Label(row_frame, text=medicine.get('drawer_number', 'N/A'), font=FONTS['body'],
                             fg=THEME['text_primary'], bg='#F8F9FA', anchor='w')
        drawer_lbl.pack(side='left', padx=10, pady=15)
        
        # Shelf Location
        shelf_lbl = tk.Label(row_frame, text=medicine.get('shelf_location', 'N/A'), font=FONTS['body'],
                            fg=THEME['text_primary'], bg='#F8F9FA', anchor='w')
        shelf_lbl.pack(side='left', padx=10, pady=15)
        
        # Status badges (matching screenshot colors)
        stock_status = "Low Stock" if medicine['quantity'] <= medicine['reorder_level'] else "In Stock"
        stock_color = THEME['warning'] if stock_status == "Low Stock" else THEME['success']
        stock_badge = tk.Label(row_frame, text=stock_status, font=FONTS['small'],
                             fg='white', bg=stock_color, relief='solid', bd=1)
        stock_badge.pack(side='left', padx=10, pady=15)
        
        # Expiry badge (simplified)
        expiry_badge = tk.Label(row_frame, text="Valid", font=FONTS['small'],
                              fg='white', bg=THEME['success'], relief='solid', bd=1)
        expiry_badge.pack(side='left', padx=5, pady=15)
        
        # Quantity & Price
        qty_lbl = tk.Label(row_frame, text=str(medicine['quantity']), font=FONTS['body'],
                          fg=THEME['text_primary'], bg='#F8F9FA')
        qty_lbl.pack(side='left', padx=10, pady=15)
        
        price_lbl = tk.Label(row_frame, text=f"₹{medicine['price']:.2f}", font=FONTS['body'],
                            fg=THEME['text_primary'], bg='#F8F9FA')
        price_lbl.pack(side='left', padx=10, pady=15)
        
        # Actions (3 dots)
        actions_btn = tk.Button(row_frame, text="⋮", font=('Segoe UI', 14),
                              bg='#F8F9FA', fg=THEME['text_secondary'], 
                              relief='flat', width=3,
                              command=lambda: self.show_actions_menu(medicine))
        actions_btn.pack(side='right', padx=20, pady=15)
    
    def show_add_dialog(self):
        """Show add medicine dialog"""
        AddMedicineDialog(self, self.refresh_table)
    
    def show_actions_menu(self, medicine):
        """Show edit/delete menu"""
        action = messagebox.askquestion("Actions", 
                                      f"What would you like to do with {medicine['name']}?",
                                      icon='question')
        if action == 'yes':  # Edit
            EditMedicineDialog(self, medicine, self.refresh_table)
        elif action == 'no':  # Delete
            self.delete_medicine(medicine)
    
    def delete_medicine(self, medicine):
        """Delete medicine from database"""
        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to delete {medicine['name']}?"):
            try:
                with get_connection() as conn:
                    conn.execute("DELETE FROM medicines WHERE id = ?", (medicine['id'],))
                    messagebox.showinfo("Success", f"{medicine['name']} deleted successfully!")
                    self.refresh_table()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete medicine: {e}")
    
    def filter_medicines(self, event=None):
        """Filter medicines by search"""
        pass  # Implement in future batch


class AddMedicineDialog(tk.Toplevel):
    """Dialog for adding new medicines"""
    
    def __init__(self, parent, refresh_callback):
        super().__init__(parent)
        self.refresh_callback = refresh_callback
        self.title("Add Medicine")
        self.geometry("400x500")
        self.configure(bg=THEME['card_bg'])
        
        # Center the dialog
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        # Title
        title = tk.Label(self, text="Add New Medicine", font=('Segoe UI', 16, 'bold'),
                        fg=THEME['text_primary'], bg=THEME['card_bg'])
        title.pack(pady=20)
        
        # Form fields
        form_frame = tk.Frame(self, bg=THEME['card_bg'])
        form_frame.pack(fill='both', expand=True, padx=20)
        
        # Name
        tk.Label(form_frame, text="Medicine Name:", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.name_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.name_var, font=FONTS['body'],
                relief='solid', bd=1).pack(fill='x', pady=(0, 15))
        
        # Category
        tk.Label(form_frame, text="Category:", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.category_var = tk.StringVar()
        categories = ['Analgesics', 'Antibiotics', 'Cardiovascular', 'Antidiabetics', 
                     'Respiratory', 'Antihistamines']
        ttk.Combobox(form_frame, textvariable=self.category_var, values=categories,
                    font=FONTS['body'], state='readonly').pack(fill='x', pady=(0, 15))
        
        # Batch Number
        tk.Label(form_frame, text="Batch Number:", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.batch_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.batch_var, font=FONTS['body'],
                relief='solid', bd=1).pack(fill='x', pady=(0, 15))
        
        # Expiry Date
        tk.Label(form_frame, text="Expiry Date (YYYY-MM-DD):", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.expiry_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.expiry_var, font=FONTS['body'],
                relief='solid', bd=1).pack(fill='x', pady=(0, 15))
        
        # Quantity
        tk.Label(form_frame, text="Quantity:", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.qty_var = tk.StringVar(value="0")
        tk.Entry(form_frame, textvariable=self.qty_var, font=FONTS['body'],
                relief='solid', bd=1).pack(fill='x', pady=(0, 15))
        
        # Drawer Number
        tk.Label(form_frame, text="Drawer Number:", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.drawer_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.drawer_var, font=FONTS['body'],
                relief='solid', bd=1).pack(fill='x', pady=(0, 15))
        
        # Shelf Location
        tk.Label(form_frame, text="Shelf Location:", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.shelf_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.shelf_var, font=FONTS['body'],
                relief='solid', bd=1).pack(fill='x', pady=(0, 15))
        
        # Price
        tk.Label(form_frame, text="Price:", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.price_var = tk.StringVar(value="0.00")
        tk.Entry(form_frame, textvariable=self.price_var, font=FONTS['body'],
                relief='solid', bd=1).pack(fill='x', pady=(0, 15))
        
        # Buttons
        btn_frame = tk.Frame(self, bg=THEME['card_bg'])
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        save_btn = tk.Button(btn_frame, text="Save", font=FONTS['heading'],
                           bg=THEME['primary_green'], fg='white', relief='flat',
                           command=self.save_medicine)
        save_btn.pack(side='left', padx=(0, 10))
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=FONTS['heading'],
                             bg=THEME['text_secondary'], fg='white', relief='flat',
                             command=self.destroy)
        cancel_btn.pack(side='left')
    
    def save_medicine(self):
        """Save new medicine to database"""
        try:
            name = self.name_var.get().strip()
            category = self.category_var.get().strip()
            batch = self.batch_var.get().strip()
            expiry = self.expiry_var.get().strip()
            qty = int(self.qty_var.get())
            price = float(self.price_var.get())
            drawer = self.drawer_var.get().strip()
            shelf = self.shelf_var.get().strip()
            
            if not all([name, category, batch, expiry]):
                messagebox.showerror("Error", "Please fill all required fields")
                return
            
            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO medicines (name, category, batch_number, expiry_date, 
                                         quantity, reorder_level, price, drawer_number, shelf_location)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, category, batch, expiry, qty, 10, price, drawer, shelf))
                
                messagebox.showinfo("Success", "Medicine added successfully!")
                self.refresh_callback()
                self.destroy()
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid quantity and price")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add medicine: {e}")


class EditMedicineDialog(tk.Toplevel):
    """Dialog for editing medicines"""
    
    def __init__(self, parent, medicine, refresh_callback):
        super().__init__(parent)
        self.medicine = medicine
        self.refresh_callback = refresh_callback
        self.title("Edit Medicine")
        self.geometry("400x500")
        self.configure(bg=THEME['card_bg'])
        
        # Center the dialog
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        # Title
        title = tk.Label(self, text="Edit Medicine", font=('Segoe UI', 16, 'bold'),
                        fg=THEME['text_primary'], bg=THEME['card_bg'])
        title.pack(pady=20)
        
        # Form fields
        form_frame = tk.Frame(self, bg=THEME['card_bg'])
        form_frame.pack(fill='both', expand=True, padx=20)
        
        # Name
        tk.Label(form_frame, text="Medicine Name:", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.name_var = tk.StringVar(value=self.medicine['name'])
        tk.Entry(form_frame, textvariable=self.name_var, font=FONTS['body'],
                relief='solid', bd=1).pack(fill='x', pady=(0, 15))
        
        # Category
        tk.Label(form_frame, text="Category:", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.category_var = tk.StringVar(value=self.medicine['category'])
        categories = ['Analgesics', 'Antibiotics', 'Cardiovascular', 'Antidiabetics', 
                     'Respiratory', 'Antihistamines']
        ttk.Combobox(form_frame, textvariable=self.category_var, values=categories,
                    font=FONTS['body'], state='readonly').pack(fill='x', pady=(0, 15))
        
        # Batch Number
        tk.Label(form_frame, text="Batch Number:", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.batch_var = tk.StringVar(value=self.medicine['batch_number'])
        tk.Entry(form_frame, textvariable=self.batch_var, font=FONTS['body'],
                relief='solid', bd=1).pack(fill='x', pady=(0, 15))
        
        # Expiry Date
        tk.Label(form_frame, text="Expiry Date (YYYY-MM-DD):", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.expiry_var = tk.StringVar(value=self.medicine['expiry_date'])
        tk.Entry(form_frame, textvariable=self.expiry_var, font=FONTS['body'],
                relief='solid', bd=1).pack(fill='x', pady=(0, 15))
        
        # Quantity
        tk.Label(form_frame, text="Quantity:", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.qty_var = tk.StringVar(value=str(self.medicine['quantity']))
        tk.Entry(form_frame, textvariable=self.qty_var, font=FONTS['body'],
                relief='solid', bd=1).pack(fill='x', pady=(0, 15))
        
        # Drawer Number
        tk.Label(form_frame, text="Drawer Number:", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.drawer_var = tk.StringVar(value=self.medicine.get('drawer_number', ''))
        tk.Entry(form_frame, textvariable=self.drawer_var, font=FONTS['body'],
                relief='solid', bd=1).pack(fill='x', pady=(0, 15))
        
        # Shelf Location
        tk.Label(form_frame, text="Shelf Location:", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.shelf_var = tk.StringVar(value=self.medicine.get('shelf_location', ''))
        tk.Entry(form_frame, textvariable=self.shelf_var, font=FONTS['body'],
                relief='solid', bd=1).pack(fill='x', pady=(0, 15))
        
        # Price
        tk.Label(form_frame, text="Price:", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(anchor='w')
        self.price_var = tk.StringVar(value=str(self.medicine['price']))
        tk.Entry(form_frame, textvariable=self.price_var, font=FONTS['body'],
                relief='solid', bd=1).pack(fill='x', pady=(0, 15))
        
        # Buttons
        btn_frame = tk.Frame(self, bg=THEME['card_bg'])
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        save_btn = tk.Button(btn_frame, text="Save", font=FONTS['heading'],
                           bg=THEME['primary_green'], fg='white', relief='flat',
                           command=self.update_medicine)
        save_btn.pack(side='left', padx=(0, 10))
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=FONTS['heading'],
                             bg=THEME['text_secondary'], fg='white', relief='flat',
                             command=self.destroy)
        cancel_btn.pack(side='left')
    
    def update_medicine(self):
        """Update medicine in database"""
        try:
            name = self.name_var.get().strip()
            category = self.category_var.get().strip()
            batch = self.batch_var.get().strip()
            expiry = self.expiry_var.get().strip()
            qty = int(self.qty_var.get())
            price = float(self.price_var.get())
            drawer = self.drawer_var.get().strip()
            shelf = self.shelf_var.get().strip()
            
            if not all([name, category, batch, expiry]):
                messagebox.showerror("Error", "Please fill all required fields")
                return
            
            with get_connection() as conn:
                conn.execute("""
                    UPDATE medicines SET name=?, category=?, batch_number=?, 
                                     expiry_date=?, quantity=?, price=?,
                                     drawer_number=?, shelf_location=?
                    WHERE id=?
                """, (name, category, batch, expiry, qty, price, drawer, shelf, self.medicine['id']))
                
                messagebox.showinfo("Success", "Medicine updated successfully!")
                self.refresh_callback()
                self.destroy()
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid quantity and price")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update medicine: {e}")
