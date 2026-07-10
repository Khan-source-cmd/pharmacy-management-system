"""
Input validation utilities
"""
import re
from tkinter import messagebox

class Validator:
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}₹'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_price(price):
        try:
            return float(price) >= 0
        except:
            return False
    
    @staticmethod
    def validate_quantity(qty):
        try:
            return int(qty) > 0
        except:
            return False
    
    @staticmethod
    def validate_date(date_str):
        try:
            from datetime import datetime
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except:
            return False
    
    @staticmethod
    def show_validation_error(field):
        messagebox.showerror("Validation Error", f"{field} is invalid")
