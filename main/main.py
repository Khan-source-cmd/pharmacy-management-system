#!/usr/bin/env python3
"""
MediSys Pharmacy Management System - Main Entry Point
Exact replica of screenshot UI design
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox
import sqlite3
from config.database import init_database, get_db_connection
from config.theme import THEME
from ui.login import LoginWindow
from ui.main_window import MainWindow

def main():
    # Initialize database with demo data
    init_database()
    
    # Create root window
    root = tk.Tk()
    root.title("MediSys - Pharmacy Management System")
    root.geometry("1400x900")
    root.minsize(1200, 800)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (1400 // 2)
    y = (root.winfo_screenheight() // 2) - (900 // 2)
    root.geometry(f"1400x900+{x}+{y}")
    
    # Apply MediSys theme
    root.configure(bg=THEME['sidebar_bg'])
    
    # Start with login
    login = LoginWindow(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()
