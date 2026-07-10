"""
Reusable Add/Edit forms (Medicine, Customer, Supplier)
"""
import tkinter as tk
from tkinter import ttk
from config.theme import THEME, FONTS
from utils.validation import Validator
from utils.notifications import Notification

class FormDialog(tk.Toplevel):
    def __init__(self, parent, title, fields, data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x500")
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.fields = fields
        self.data = data or {}
        self.setup_form()
    
    def setup_form(self):
        """Generic form layout"""
        # Header
        header = tk.Label(self, text=self.title, font=FONTS['subtitle'],
                         fg=THEME['text_primary'], bg='white')
        header.pack(pady=30)
        
        # Form fields
        form_frame = tk.Frame(self, bg='white')
        form_frame.pack(fill='x', padx=40, pady=20)
        
        self.entries = {}
        for field_name, field_config in self.fields.items():
            frame = tk.Frame(form_frame, bg='white')
            frame.pack(fill='x', pady=15)
            
            label = tk.Label(frame, text=field_config['label'], 
                           font=FONTS['body'], fg=THEME['text_primary'], bg='white')
            label.pack(anchor='w')
            
            if field_config['type'] == 'text':
                entry = tk.Entry(frame, font=FONTS['body'], relief='solid', bd=1)
            elif field_config['type'] == 'number':
                entry = tk.Entry(frame, font=FONTS['body'], relief='solid', bd=1)
            elif field_config['type'] == 'date':
                entry = tk.Entry(frame, font=FONTS['body'], relief='solid', bd=1)
            elif field_config['type'] == 'combo':
                entry = ttk.Combobox(frame, font=FONTS['body'], state='readonly')
                entry['values'] = field_config['options']
            
            entry.pack(fill='x', pady=(5, 0))
            self.entries[field_name] = entry
            
            if field_name in self.data:
                entry.insert(0, self.data[field_name])
        
        # Buttons
        btn_frame = tk.Frame(self, bg='white')
        btn_frame.pack(pady=30)
        
        save_btn = tk.Button(btn_frame, text="Save", font=FONTS['heading'],
                           bg=THEME['primary_green'], fg='white', relief='flat',
                           command=self.save_form)
        save_btn.pack(side='right', padx=10)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=FONTS['body'],
                             bg=THEME['text_secondary'], fg='white', relief='flat',
                             command=self.destroy)
        cancel_btn.pack(side='right')
    
    def save_form(self):
        """Validate and save form"""
        form_data = {}
        for field, entry in self.entries.items():
            value = entry.get().strip()
            form_data[field] = value
        
        # Basic validation
        if not form_data.get('name'):
            Notification.warning("Name is required")
            return
        
        self.result = form_data
        self.destroy()
