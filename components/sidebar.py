"""
Sidebar Navigation - EXACT screenshot #2 layout
Dashboard | Inventory | Sales | Customers | Suppliers | Reports
"""
import tkinter as tk
from tkinter import ttk
from config.theme import THEME, FONTS

class Sidebar(tk.Frame):
    def __init__(self, parent, user, switch_callback):
        super().__init__(parent, bg=THEME['sidebar_bg'])
        self.user = user
        self.switch_callback = switch_callback
        self.selected_item = None

        self.setup_sidebar()
    
    def setup_sidebar(self):
        """Create sidebar matching screenshot exactly"""
        # Sidebar header
        header_frame = tk.Frame(self, bg=THEME['sidebar_bg'], height=80)
        header_frame.pack(fill='x', pady=(20, 30))
        header_frame.pack_propagate(False)

        # MediSys logo
        logo_label = tk.Label(header_frame, text="MediSys",
                            font=('Segoe UI', 28, 'bold'),
                            fg=THEME['primary_green'], bg=THEME['sidebar_bg'])
        logo_label.pack()

        # Navigation items (EXACT order from screenshot)
        nav_items = [
            ('dashboard', 'Dashboard'),
            ('inventory', 'Inventory'),
            ('sales', 'Sales'),
            ('customers', 'Customers'),
            ('suppliers', 'Suppliers'),
            ('reports', 'Reports')
        ]

        # Role-based navigation (admin sees all, staff limited)
        if self.user['role'] == 'admin':
            nav_items.append(('predictive', 'Predictive Stock'))

        self.nav_buttons = {}
        for key, label in nav_items:
            btn = self.create_nav_button(key, label)
            self.nav_buttons[key] = btn

    def create_nav_button(self, key, label):
        """Create individual navigation button"""
        btn_frame = tk.Frame(self, bg=THEME['sidebar_bg'], height=50)
        btn_frame.pack(fill='x', pady=2)
        btn_frame.pack_propagate(False)

        # Button with hover effect
        btn = tk.Button(btn_frame, text=label, font=FONTS['heading'],
                       bg=THEME['sidebar_bg'], fg=THEME['text_primary'],
                       relief='flat', anchor='w', borderwidth=0,
                       command=lambda k=key: self.select_item(k))
        btn.pack(fill='x', padx=20, pady=10)

        # Hover effects
        btn.bind('<Enter>', lambda e, k=key: self.on_hover(k, True))
        btn.bind('<Leave>', lambda e, k=key: self.on_hover(k, False))

        return btn
    
    def select_item(self, item_key):
        """Select navigation item (highlight active)"""
        if self.selected_item:
            self.nav_buttons[self.selected_item].configure(
                bg=THEME['sidebar_bg'], fg=THEME['text_primary']
            )
        
        self.selected_item = item_key
        self.nav_buttons[item_key].configure(
            bg=THEME['primary_green'], fg='white'
        )
        self.switch_callback(item_key)
    
    def on_hover(self, item_key, enter):
        """Hover effect for nav buttons"""
        if item_key != self.selected_item:
            bg_color = THEME['light_green'] if enter else THEME['sidebar_bg']
            fg_color = 'white' if enter else THEME['text_primary']
            self.nav_buttons[item_key].configure(bg=bg_color, fg=fg_color)
