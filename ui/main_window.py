"""
Main Window with Sidebar - Exact screenshot layout
Dashboard, Inventory, Sales, Customers, Suppliers, Reports
"""
import tkinter as tk
from tkinter import ttk
from config.theme import THEME, FONTS
from config.database import get_connection
from components.sidebar import Sidebar
from .dashboard import DashboardView
from .inventory import InventoryView
from .sales import SalesView
from .customers import CustomersView
from .suppliers import SuppliersView
from .reports import ReportsView

class MainWindow:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.current_view = None
        
        # Configure root
        self.root.title(f"MediSys - Dashboard | {user['role'].title()}")
        self.root.configure(bg=THEME['sidebar_bg'])
        
        self.setup_main_layout()
        self.show_dashboard()
    
    def setup_main_layout(self):
        """Create main layout: sidebar + content area"""
        # Main container
        main_container = tk.Frame(self.root, bg=THEME['sidebar_bg'])
        main_container.pack(fill='both', expand=True)
        
        # Sidebar (left panel - exact screenshot width)
        self.sidebar = Sidebar(main_container, self.user, self.switch_view)
        self.sidebar.pack(side='left', fill='y', padx=(20, 0))
        
        # Content area (right panel)
        content_frame = tk.Frame(main_container, bg='white')
        content_frame.pack(side='right', fill='both', expand=True, padx=(20, 20), pady=20)
        
        # Content container with shadow effect
        self.content_frame = tk.Frame(content_frame, bg=THEME['card_bg'], 
                                    relief='solid', bd=1)
        self.content_frame.pack(fill='both', expand=True, pady=(20, 0))
    
    def switch_view(self, view_name):
        """Switch between different views"""
        # Destroy current view
        if self.current_view:
            self.current_view.destroy()
        
        # Create new view
        if view_name == 'dashboard':
            self.current_view = DashboardView(self.content_frame)
        elif view_name == 'inventory':
            self.current_view = InventoryView(self.content_frame)
        elif view_name == 'sales':
            self.current_view = SalesView(self.content_frame)
        elif view_name == 'customers':
            self.current_view = CustomersView(self.content_frame)
        elif view_name == 'suppliers':
            self.current_view = SuppliersView(self.content_frame)
        elif view_name == 'reports':
            self.current_view = ReportsView(self.content_frame)
        
        self.current_view.pack(fill='both', expand=True, padx=30, pady=30)
    
    def show_dashboard(self):
        """Show dashboard as default"""
        self.sidebar.select_item('dashboard')
        self.switch_view('dashboard')
