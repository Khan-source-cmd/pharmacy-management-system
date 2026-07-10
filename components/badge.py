"""
Status badges (In Stock, Low Stock, Expired) - Screenshot #6
"""
import tkinter as tk
from config.theme import THEME, FONTS

class StatusBadge(tk.Label):
    def __init__(self, parent, status, quantity=None, expiry_date=None):
        self.status = status.lower()
        self.quantity = quantity
        self.expiry_date = expiry_date
        
        color_map = {
            'in stock': THEME['success'],
            'low stock': THEME['warning'],
            'expired': THEME['danger'],
            'near expiry': '#FF9800',
            'valid': THEME['success']
        }
        
        bg_color = color_map.get(self.status, THEME['info'])
        fg_color = 'white'
        
        super().__init__(parent, text=status.title(), font=FONTS['small'],
                        fg=fg_color, bg=bg_color, relief='solid', bd=1,
                        padx=8, pady=2)
