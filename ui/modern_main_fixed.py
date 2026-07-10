#!/usr/bin/env python3
"""
Modern PyQt6 Main Application Window - FIXED VERSION
Complete dashboard with sidebar navigation and KPI cards
Fixed visibility and data display issues
"""
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea,
                           QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                           QLineEdit, QDateEdit, QCheckBox, QGridLayout, QDialog, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QDate
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap, QIcon
import secrets
import matplotlib
matplotlib.use('QtAgg')  # Use QtAgg backend for matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import sys
import os
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QColor
# Add the project root to Python path to find the database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database functions
try:
    from database.modern_db import (authenticate_user, get_medicines, get_sales_summary, 
                                   get_recent_sales, get_predictive_stock_analysis, create_sale,
                                   create_medicine, update_medicine, delete_medicine,
                                   get_customers, get_suppliers, create_customer, create_supplier,
                                   get_daily_sales_report, get_monthly_sales_report, 
                                   get_customer_analytics_report, get_purchase_history_report,
                                   get_customer_purchase_history, log_audit)
    print("Database functions imported successfully")
except ImportError as e:
    print(f"Database import error: {e}")
    raise  # Re-raise the error instead of providing fallback

# Import animation utilities
try:
    from utils.animations import animation_manager, HoverEffects, LoadingAnimations
    print("Animation utilities imported successfully")
except ImportError as e:
    print(f"Animation import error: {e}")
    animation_manager = None

from datetime import datetime, timedelta

class ModernMainApp(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        # keep track of current role for rebuild detection
        self.previous_role = user.get('role') if user else None
        self.setWindowTitle("MediSys - Pharmacy Management System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Setup UI
        self.setup_ui()
        self.show_dashboard()
    
    def setup_ui(self):
        """Setup main application layout with toggleable sidebar"""
        # Main container
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout: sidebar + content
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar, 1)
        
        # Content area
        self.content_area = self.create_content_area()
        main_layout.addWidget(self.content_area, 4)
        
        # Sidebar toggle button (hamburger menu) - FIXED: Integrated with sidebar
        self.toggle_button = QPushButton("☰")
        self.toggle_button.setFixedSize(40, 40)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #1AAE4A;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #168f3c;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        
        # Sidebar state
        self.sidebar_visible = True

    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        if self.sidebar_visible:
            self.sidebar.hide()
            self.toggle_button.setText("☰")
        else:
            self.sidebar.show()
            self.toggle_button.setText("✕")
        self.sidebar_visible = not self.sidebar_visible

    
    def create_sidebar(self):
        """Create modern sidebar with navigation"""
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1AAE4A,
                    stop: 1 #0f5b26
                );
                border-right: 1px solid #168f3c;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(10)
        
        # Logo section
        logo_frame = QFrame()
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setSpacing(5)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo icon (using PNG version for better PyQt6 compatibility)
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            import os
            # Get the absolute path to the logo file
            current_dir = os.path.dirname(os.path.abspath(__file__))  # ui/ directory
            project_root = os.path.dirname(current_dir)  # pharmacy_management_system/
            logo_path = os.path.join(project_root, "assets", "icons", "logo.png")
            
            logo_pixmap = QPixmap(logo_path)
            if not logo_pixmap.isNull():
                # Scale logo to fit perfectly in 60x60px space for more compact appearance
                scaled_pixmap = logo_pixmap.scaled(60, 60, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
            else:
                # Fallback to placeholder if logo file not found
                logo_label.setText("LOGO")
                logo_label.setStyleSheet("""
                    QLabel {
                        background-color: white;
                        border-radius: 30px;
                        border: 3px solid rgba(255, 255, 255, 0.3);
                        color: #1AAE4A;
                        font-weight: bold;
                        font-size: 16px;
                    }
                """)
                logo_label.setFixedSize(60, 60)
        except:
            # Fallback to placeholder if any error occurs
            logo_label.setText("LOGO")
            logo_label.setStyleSheet("""
                QLabel {
                    background-color: white;
                    border-radius: 30px;
                    border: 3px solid rgba(255, 255, 255, 0.3);
                    color: #1AAE4A;
                    font-weight: bold;
                    font-size: 16px;
                }
            """)
            logo_label.setFixedSize(60, 60)
        
        app_title = QLabel("MediSys")
        app_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        app_title.setStyleSheet("color: white;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        user_info = QLabel(f"Welcome, {self.user['role'].title()}")
        user_info.setFont(QFont("Segoe UI", 10))
        user_info.setStyleSheet("color: #bdc3c7;")
        user_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(app_title)
        logo_layout.addWidget(user_info)
        
        layout.addWidget(logo_frame)
        
        # Navigation buttons
        nav_items = [
            ("📊", "Dashboard"),
            ("📦", "Inventory"),
            ("💰", "Sales"),
            ("👥", "Customers"),
            ("🏢", "Suppliers"),
            ("⚙️", "Settings"),
            ("📈", "Reports"),
            ("🔮", "Predictive"),
            ("📋", "Sales History")  # New Sales History section
        ]
        
        self.nav_buttons = {}
        # debug
        print(f"creating sidebar for role={self.user.get('role') if self.user else None}")
        # Determine admin status once
        is_admin = bool(self.user and self.user.get('role') == 'admin')

        for icon, text in nav_items:
            # Hide Settings nav for non-admin users
            if text == 'Settings' and not is_admin:
                continue
            btn = QPushButton(f"  {icon}  {text}")
            btn.setFont(QFont("Segoe UI", 12))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: rgba(255, 255, 255, 0.9);
                    border: none;
                    text-align: left;
                    padding: 12px 15px;
                    border-radius: 8px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: white;
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, t=text: self.switch_view(t))
            layout.addWidget(btn)
            self.nav_buttons[text] = btn
        
        # Logout button
        logout_btn = QPushButton("  🔑  Logout")
        logout_btn.setFont(QFont("Segoe UI", 12))
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.9);
                border: none;
                text-align: left;
                padding: 12px 15px;
                border-radius: 8px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        # Spacer to push logout to bottom
        layout.addStretch()
        
        return sidebar
    
    def create_content_area(self):
        """Create main content area - FIXED VERSION with proper header width and main scrollbar"""
        content = QFrame()
        content.setStyleSheet("background-color: #ecf0f1;")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for full coverage

        # Header - Fix width and alignment issues
        header = self.create_header()
        header.setContentsMargins(0, 0, 0, 0)  # Remove negative margins
        header.setMinimumWidth(800)  # Ensure adequate width for header text
        layout.addWidget(header)

        # Main content container with scrollbar for the entire page
        self.content_container = QScrollArea()
        self.content_container.setWidgetResizable(True)
        self.content_container.setMinimumHeight(600)  # Reduced height for better responsiveness
        self.content_container.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
                min-height: 600px;
            }
            QScrollBar:vertical {
                width: 16px;  /* Main scrollbar width - slightly wider for main content */
                background: #ecf0f1;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 8px;
                min-height: 60px;  /* Larger scroll handle for main content */
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;  /* Remove scroll arrows for cleaner look */
            }
            QScrollBar::handle:vertical:hover {
                background: #95a5a6;  /* Darker on hover for better interaction */
            }
        """)

        # Create a widget to hold all page content
        self.content_widget = QWidget()
        self.content_widget_layout = QVBoxLayout(self.content_widget)
        self.content_widget_layout.setContentsMargins(20, 20, 20, 20)  # Add padding inside content
        self.content_widget_layout.setSpacing(20)  # Space between sections

        # Set the content widget as the widget for the scroll area
        self.content_container.setWidget(self.content_widget)

        layout.addWidget(self.content_container)

        return content
    
    def create_header(self):
        """Create page header"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 15px 20px;
                border: 1px solid #d5dbdb;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        self.page_title = QLabel("Dashboard")
        self.page_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.page_title.setStyleSheet("color: #2c3e50;")
        
        self.page_subtitle = QLabel("Overview of your pharmacy operations")
        self.page_subtitle.setFont(QFont("Segoe UI", 11))
        self.page_subtitle.setStyleSheet("color: #7f8c8d;")
        
        layout.addWidget(self.page_title)
        layout.addWidget(self.page_subtitle)
        layout.addStretch()
        
        return header
    
    def switch_view(self, view_name):
        """Switch between different views - FIXED VERSION"""
        # Update sidebar selection
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.setStyleSheet(btn.styleSheet().replace("QPushButton:selected", "QPushButton:hover"))
            else:
                btn.setStyleSheet(btn.styleSheet().replace("QPushButton:hover", "QPushButton:selected"))
        
        # Update header
        self.page_title.setText(view_name)
        self.page_subtitle.setText(self.get_subtitle(view_name))
        
        # Create content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        if view_name == "Dashboard":
            self.create_dashboard_content(content_layout)
        elif view_name == "Inventory":
            self.create_inventory_content(content_layout)
        elif view_name == "Sales":
            self.create_sales_content(content_layout)
        elif view_name == "Customers":
            self.create_customers_content(content_layout)
        elif view_name == "Suppliers":
            self.create_suppliers_content(content_layout)
        elif view_name == "Settings":
            self.create_settings_content(content_layout)
        elif view_name == "Reports":
            self.create_reports_content(content_layout)
        elif view_name == "Predictive":
            self.create_predictive_content(content_layout)
        elif view_name == "Sales History":
            self.create_sales_history_content(content_layout)
        
        self.content_container.setWidget(content_widget)
        
        # CRITICAL FIX: Make sure everything is visible
        QTimer.singleShot(100, self.ensure_content_visibility)
    
    def ensure_content_visibility(self):
        """Ensure all content is visible - CRITICAL FIX"""
        # Make sure the main window is visible
        if not self.isVisible():
            self.show()
        
        # Make sure the content container is visible
        if not self.content_container.isVisible():
            self.content_container.setVisible(True)
        
        # Make sure the content widget is visible
        content_widget = self.content_container.widget()
        if content_widget and not content_widget.isVisible():
            content_widget.setVisible(True)
    
    def get_subtitle(self, view_name):
        """Get subtitle for each view"""
        subtitles = {
            "Dashboard": "Overview of your pharmacy operations",
            "Inventory": "Manage your medicine stock and inventory",
            "Sales": "Process sales and manage invoices",
            "Customers": "Customer records and transaction history",
            "Suppliers": "Supplier information and contacts",
            "Reports": "Generate and export reports",
            "Predictive": "Stock predictions and analytics"
        }
        return subtitles.get(view_name, "Application dashboard")
    
    def create_dashboard_content(self, layout):
        """Create dashboard with KPI cards and charts - FIXED VERSION with scrolling"""
        # Create a scrollable dashboard container
        dashboard_scroll = QScrollArea()
        dashboard_scroll.setWidgetResizable(True)
        dashboard_scroll.setMinimumHeight(600)
        dashboard_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
                min-height: 600px;
            }
            QScrollBar:vertical {
                width: 14px;
                background: #ecf0f1;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 7px;
                min-height: 50px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Dashboard content widget
        dashboard_content = QWidget()
        dashboard_content_layout = QVBoxLayout(dashboard_content)
        dashboard_content_layout.setSpacing(20)
        
        # Get real data from database with enhanced debugging
        try:
            print("DEBUG: Fetching sales summary from database...")
            summary = get_sales_summary(7)  # Last 7 days
            print(f"DEBUG: Sales summary retrieved: {summary}")
        except Exception as e:
            print(f"ERROR: Failed to get sales summary: {e}")
            print("DEBUG: Using fallback values")
            summary = {'total_revenue': 0, 'total_medicines': 0, 'low_stock_count': 0, 'expired_count': 0}
        
        # KPI Cards with animations
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(20)
        
        # Total Revenue Card
        revenue_card = self.create_kpi_card("Total Revenue", f"₹{summary['total_revenue']:.2f}", "+12.5% from last month", "revenue")
        kpi_layout.addWidget(revenue_card)
        
        # Total Medicines Card
        medicines_card = self.create_kpi_card("Total Medicines", str(summary['total_medicines']), "Active inventory items", "medicines")
        kpi_layout.addWidget(medicines_card)
        
        # Low Stock Alerts Card - Interactive
        alerts_card = self.create_kpi_card("Low Stock Alerts", str(summary['low_stock_count']), "Items need restocking", "low_stock")
        alerts_card.setStyleSheet(alerts_card.styleSheet().replace("#2c3e50", "#e67e22"))
        kpi_layout.addWidget(alerts_card)
        
        # Expired Medicines Card - Interactive
        expired_card = self.create_kpi_card("Expired Medicines", str(summary['expired_count']), "Items past expiry date", "expired")
        expired_card.setStyleSheet(expired_card.styleSheet().replace("#2c3e50", "#e74c3c"))
        kpi_layout.addWidget(expired_card)
        
        dashboard_content_layout.addLayout(kpi_layout)
        
        # Charts and Tables
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # Sales Chart with improved proportions
        chart_frame = self.create_chart_frame("Sales Overview", "This week's sales trend")
        chart_frame.setMinimumHeight(400)  # Ensure minimum height for better chart display
        charts_layout.addWidget(chart_frame, 3)  # Give chart more space (3:2 ratio)
        
        # Recent Sales Table with real data
        sales_table = self.create_recent_sales_table()
        charts_layout.addWidget(sales_table, 2)
        
        dashboard_content_layout.addLayout(charts_layout)
        
        # Additional dashboard content to demonstrate scrolling
        # Inventory Summary Section - FIXED: Use real-time data
        inventory_summary_frame = QFrame()
        inventory_summary_layout = QVBoxLayout(inventory_summary_frame)
        inventory_summary_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #d5dbdb;
            }
        """)
        
        inventory_title = QLabel("Inventory Summary")
        inventory_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        inventory_title.setStyleSheet("color: #2c3e50;")
        
        # Get real-time inventory data
        inventory_data_layout = QVBoxLayout()
        
        try:
            # Import the new function
            from database.modern_db import get_inventory_summary
            
            # Get real inventory data
            inventory_items = get_inventory_summary()
            
            if inventory_items:
                for item in inventory_items:
                    item_layout = QHBoxLayout()
                    
                    item_name_label = QLabel(item['name'])
                    item_name_label.setFont(QFont("Segoe UI", 10))
                    item_name_label.setStyleSheet("color: #2c3e50;")
                    
                    status_label = QLabel(item['stock_status'])
                    status_label.setFont(QFont("Segoe UI", 10))
                    if item['stock_status'] == "Low Stock":
                        status_label.setStyleSheet("color: #e67e22; font-weight: bold;")
                    elif item['stock_status'] == "Out of Stock":
                        status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
                    else:
                        status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                    
                    quantity_label = QLabel(f"{item['quantity']} units")
                    quantity_label.setFont(QFont("Segoe UI", 10))
                    quantity_label.setStyleSheet("color: #7f8c8d;")
                    
                    item_layout.addWidget(item_name_label)
                    item_layout.addWidget(status_label)
                    item_layout.addWidget(quantity_label)
                    item_layout.addStretch()
                    
                    inventory_data_layout.addLayout(item_layout)
            else:
                error_label = QLabel("No inventory data available.")
                error_label.setFont(QFont("Segoe UI", 10))
                error_label.setStyleSheet("color: #e74c3c;")
                inventory_data_layout.addWidget(error_label)
        
        except Exception as e:
            print(f"Error loading real-time inventory data: {e}")
            error_label = QLabel(f"Failed to load inventory data: {str(e)}")
            error_label.setFont(QFont("Segoe UI", 10))
            error_label.setStyleSheet("color: #e74c3c;")
            inventory_data_layout.addWidget(error_label)
        
        inventory_summary_layout.addWidget(inventory_title)
        inventory_summary_layout.addLayout(inventory_data_layout)
        
        dashboard_content_layout.addWidget(inventory_summary_frame)
        
        # Sales Performance Section with animated KPIs
        sales_performance_frame = QFrame()
        sales_performance_layout = QVBoxLayout(sales_performance_frame)
        sales_performance_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #d5dbdb;
            }
        """)
        
        sales_title = QLabel("Sales Performance")
        sales_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        sales_title.setStyleSheet("color: #2c3e50;")
        
        # Animated sales performance metrics
        performance_metrics_layout = QGridLayout()
        
        metrics = [
            ("Daily Average", "₹1,245.50", "#27ae60"),
            ("Monthly Target", "₹15,000", "#3498db"),
            ("Achievement", "83%", "#f1c40f"),
            ("Growth Rate", "+12.5%", "#2ecc71")
        ]
        
        for i, (metric_name, metric_value, color) in enumerate(metrics):
            metric_label = QLabel(metric_name)
            metric_label.setFont(QFont("Segoe UI", 10))
            metric_label.setStyleSheet("color: #7f8c8d;")
            
            value_label = QLabel(metric_value)
            value_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            value_label.setStyleSheet(f"color: {color};")
            
            # Add hover effects to KPI cards
            HoverEffects.add_hover_effect(value_label, hover_color="#f8f9fa", normal_color="white")
            
            performance_metrics_layout.addWidget(metric_label, i, 0)
            performance_metrics_layout.addWidget(value_label, i, 1)
        
        sales_performance_layout.addWidget(sales_title)
        sales_performance_layout.addLayout(performance_metrics_layout)
        
        dashboard_content_layout.addWidget(sales_performance_frame)
        
        # Set the dashboard content as the widget for the scroll area
        dashboard_scroll.setWidget(dashboard_content)
        
        layout.addWidget(dashboard_scroll)
    
    def create_kpi_card(self, title, value, subtitle, kpi_type="default"):
        """Create a KPI card with interactive features"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #d5dbdb;
            }
            QFrame:hover {
                border-color: #1AAE4A;
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12))
        title_label.setStyleSheet("color: #7f8c8d;")
        
        # Make value label clickable for interactive KPIs
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #2c3e50;")
        value_label.setCursor(Qt.CursorShape.PointingHandCursor)
        value_label.installEventFilter(self)
        
        # Store KPI type for event handling
        value_label.setProperty("kpi_type", kpi_type)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet("color: #95a5a6;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)
        layout.addStretch()
        
        return card
    
    def eventFilter(self, obj, event):
        """Handle click events on KPI value labels"""
        if event.type() == event.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            if hasattr(obj, 'property') and obj.property("kpi_type"):
                kpi_type = obj.property("kpi_type")
                if kpi_type == "low_stock":
                    self.show_low_stock_details()
                elif kpi_type == "expired":
                    self.show_expired_medicines_details()
        return super().eventFilter(obj, event)
    
    def show_low_stock_details(self):
        """Show detailed low stock medicines list"""
        try:
            print("DEBUG: Fetching low stock medicines...")
            medicines = get_medicines(low_stock=True)
            print(f"DEBUG: Found {len(medicines)} low stock medicines")
            
            # Create detailed dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Low Stock Medicines - Detailed List")
            dialog.setGeometry(200, 200, 900, 650)  # Increased size for better visibility
            dialog.setStyleSheet("background-color: white;")
            dialog.setModal(True)
            
            layout = QVBoxLayout(dialog)
            
            # Title
            title = QLabel("Low Stock Medicines Requiring Immediate Attention")
            title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            title.setStyleSheet("color: #e67e22;")
            layout.addWidget(title)
            
            # Subtitle with count
            subtitle = QLabel(f"Found {len(medicines)} medicines with low stock levels")
            subtitle.setFont(QFont("Segoe UI", 11))
            subtitle.setStyleSheet("color: #7f8c8d;")
            layout.addWidget(subtitle)
            
            # Create table for detailed view
            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["Medicine Name", "Current Stock", "Category", "Supplier", "Reorder Level"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.verticalHeader().setVisible(False)
            table.setAlternatingRowColors(True)
            table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #d5dbdb;
                    gridline-color: #ecf0f1;
                    background-color: white;
                }
                QTableWidget::item {
                    padding: 15px;
                    border-bottom: 1px solid #ecf0f1;
                    border-right: 1px solid #ecf0f1;
                    color: #2c3e50;
                    font-size: 12px;
                    font-family: 'Segoe UI';
                    font-weight: bold;
                    min-height: 50px;  /* Increased row height for better visibility */
                }
                QTableWidget::item:selected {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    border-bottom: 2px solid #1AAE4A;
                }
                QTableWidget::item:hover {
                    background-color: #f8f9fa;
                }
                QHeaderView::section {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    font-weight: bold;
                    border: 1px solid #d5dbdb;
                    padding: 12px;
                    font-size: 12px;
                    font-family: 'Segoe UI';
                    min-height: 45px;  /* Increased header height */
                }
                QTableWidget QTableCornerButton::section {
                    background-color: #f8f9fa;
                    border: 1px solid #d5dbdb;
                }
            """)
            
            # Set minimum row height for better visibility
            table.verticalHeader().setMinimumSectionSize(50)
            
            # Populate table with low stock medicines
            table.setRowCount(len(medicines))
            for row, med in enumerate(medicines):
                # Medicine Name
                name_item = QTableWidgetItem(med['name'])
                name_item.setFont(QFont("Segoe UI", 11))
                table.setItem(row, 0, name_item)
                
                # Current Stock (highlighted in red)
                stock_item = QTableWidgetItem(str(med['quantity']))
                stock_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                stock_item.setForeground(QColor("#e74c3c"))
                table.setItem(row, 1, stock_item)
                
                # Category
                category_item = QTableWidgetItem(med['category'])
                category_item.setFont(QFont("Segoe UI", 11))
                table.setItem(row, 2, category_item)
                
                # Supplier (get from database)
                supplier_name = self.get_supplier_name(med.get('supplier_id'))
                supplier_item = QTableWidgetItem(supplier_name)
                supplier_item.setFont(QFont("Segoe UI", 11))
                table.setItem(row, 3, supplier_item)
                
                # Reorder Level
                reorder_item = QTableWidgetItem(str(med.get('reorder_level', 'N/A')))
                reorder_item.setFont(QFont("Segoe UI", 11))
                table.setItem(row, 4, reorder_item)
            
            # Set row height to accommodate content
            for row in range(len(medicines)):
                table.setRowHeight(row, 60)  # Increased row height for better visibility
            
            layout.addWidget(table)
            
            # Summary section
            summary_frame = QFrame()
            summary_layout = QHBoxLayout(summary_frame)
            summary_frame.setStyleSheet("""
                QFrame {
                    background-color: #ecf0f1;
                    border-radius: 8px;
                    padding: 15px;
                    border: 1px solid #d5dbdb;
                }
            """)
            
            total_needed = sum(med.get('reorder_level', 10) - med['quantity'] for med in medicines)
            summary_text = QLabel(f"Total units needed to reach reorder levels: {total_needed}")
            summary_text.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            summary_text.setStyleSheet("color: #e67e22;")
            
            export_btn = QPushButton("Export to CSV")
            export_btn.setStyleSheet("""
                QPushButton {
                    background-color: #9b59b6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #8e44ad;
                }
            """)
            export_btn.clicked.connect(lambda: self.export_low_stock_report(medicines))
            
            summary_layout.addWidget(summary_text)
            summary_layout.addWidget(export_btn)
            
            layout.addWidget(summary_frame)
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)
            
            dialog.exec()
            
        except Exception as e:
            print(f"Error showing low stock details: {e}")
            self.show_error_message(f"Failed to load low stock details: {e}")
    
    def show_expired_medicines_details(self):
        """Show detailed expired medicines list"""
        try:
            print("DEBUG: Fetching expired medicines...")
            # Get all medicines and filter for expired ones
            all_medicines = get_medicines()
            medicines = [med for med in all_medicines if med.get('expiry_status') == 'Expired']
            print(f"DEBUG: Found {len(medicines)} expired medicines")
            
            # Create detailed dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Expired Medicines - Detailed List")
            dialog.setGeometry(200, 200, 700, 500)
            dialog.setStyleSheet("background-color: white;")
            dialog.setModal(True)
            
            layout = QVBoxLayout(dialog)
            
            # Title
            title = QLabel("Expired Medicines Requiring Immediate Action")
            title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            title.setStyleSheet("color: #e74c3c;")
            layout.addWidget(title)
            
            # Subtitle with count
            subtitle = QLabel(f"Found {len(medicines)} medicines past their expiry date")
            subtitle.setFont(QFont("Segoe UI", 11))
            subtitle.setStyleSheet("color: #7f8c8d;")
            layout.addWidget(subtitle)
            
            # Create table for detailed view
            table = QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(["Medicine Name", "Expiry Date", "Batch Number", "Quantity", "Status", "Action"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.verticalHeader().setVisible(False)
            table.setAlternatingRowColors(True)
            table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #d5dbdb;
                    gridline-color: #ecf0f1;
                }
                QTableWidget::item {
                    padding: 10px;
                    border-bottom: 1px solid #ecf0f1;
                }
                QHeaderView::section {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    font-weight: bold;
                    border: 1px solid #d5dbdb;
                    padding: 8px;
                }
            """)
            
            # Set row height for better visibility
            table.verticalHeader().setMinimumSectionSize(50)
            
            # Set column widths - increase Action column width
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Medicine Name
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # Expiry Date
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)  # Batch Number
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)  # Quantity
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)  # Status
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Action column
            header.resizeSection(5, 150)  # Set Action column width to 150px
            
            # Populate table with expired medicines
            table.setRowCount(len(medicines))
            for row, med in enumerate(medicines):
                # Medicine Name
                name_item = QTableWidgetItem(med['name'])
                name_item.setFont(QFont("Segoe UI", 10))
                table.setItem(row, 0, name_item)
                
                # Expiry Date (highlighted in red)
                expiry_item = QTableWidgetItem(med['expiry_date'])
                expiry_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                expiry_item.setForeground(QColor("#e74c3c"))
                table.setItem(row, 1, expiry_item)
                
                # Batch Number
                batch_item = QTableWidgetItem(med.get('batch_number', 'N/A'))
                batch_item.setFont(QFont("Segoe UI", 10))
                table.setItem(row, 2, batch_item)
                
                # Quantity
                qty_item = QTableWidgetItem(str(med['quantity']))
                qty_item.setFont(QFont("Segoe UI", 10))
                table.setItem(row, 3, qty_item)
                
                # Status
                status_item = QTableWidgetItem("EXPIRED")
                status_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                status_item.setForeground(QColor("#e74c3c"))
                table.setItem(row, 4, status_item)
                
                # Action button
                action_layout = QHBoxLayout()
                action_layout.setContentsMargins(0, 0, 0, 0)
                action_layout.setSpacing(5)
                
                dispose_btn = QPushButton("Dispose")
                dispose_btn.setFixedHeight(25)
                dispose_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 0px 8px 9px 8px;
                        font-size: 10px;
                        font-weight: bold;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                dispose_btn.clicked.connect(lambda checked, med_id=med['id']: self.dispose_medicine(med_id))
                
                view_btn = QPushButton("View Details")
                view_btn.setFixedHeight(25)
                view_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 0px 8px 9px 8px;
                        font-size: 10px;
                        font-weight: bold;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                view_btn.clicked.connect(lambda checked, med_id=med['id']: self.view_medicine_details(med_id))
                
                action_layout.addWidget(dispose_btn)
                action_layout.addWidget(view_btn)
                action_layout.addStretch()
                
                action_widget = QWidget()
                action_widget.setLayout(action_layout)
                table.setCellWidget(row, 5, action_widget)
            
            layout.addWidget(table)
            
            # Summary section
            summary_frame = QFrame()
            summary_layout = QHBoxLayout(summary_frame)
            summary_frame.setStyleSheet("""
                QFrame {
                    background-color: #ecf0f1;
                    border-radius: 8px;
                    padding: 15px;
                    border: 1px solid #d5dbdb;
                }
            """)
            
            total_expired = sum(med['quantity'] for med in medicines)
            summary_text = QLabel(f"Total expired units requiring disposal: {total_expired}")
            summary_text.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            summary_text.setStyleSheet("color: #e74c3c;")
            
            export_btn = QPushButton("Export to CSV")
            export_btn.setStyleSheet("""
                QPushButton {
                    background-color: #9b59b6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #8e44ad;
                }
            """)
            export_btn.clicked.connect(lambda: self.export_expired_report(medicines))
            
            summary_layout.addWidget(summary_text)
            summary_layout.addWidget(export_btn)
            
            layout.addWidget(summary_frame)
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)
            
            dialog.exec()
            
        except Exception as e:
            print(f"Error showing expired medicines details: {e}")
            self.show_error_message(f"Failed to load expired medicines details: {e}")
    
    def get_supplier_name(self, supplier_id):
        """Get supplier name from ID"""
        try:
            if not supplier_id:
                return "N/A"
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM suppliers WHERE id = ?", (supplier_id,))
                result = cursor.fetchone()
                return result[0] if result else "N/A"
        except Exception as e:
            print(f"Error getting supplier name: {e}")
            return "N/A"
    
    def reorder_medicine(self, medicine_id):
        """Handle medicine reorder action"""
        print(f"Reorder medicine {medicine_id}")
        self.show_success_message("Reorder request submitted successfully!")
    
    def view_medicine_details(self, medicine_id):
        """Handle view medicine details action"""
        print(f"View details for medicine {medicine_id}")
        self.show_success_message("Medicine details will be displayed in a detailed view!")
    
    def dispose_medicine(self, medicine_id):
        """Handle medicine disposal action"""
        print(f"Dispose medicine {medicine_id}")
        self.show_success_message("Medicine disposal logged successfully!")
    
    def export_low_stock_report(self, medicines):
        """Export low stock report to CSV"""
        try:
            import csv
            from datetime import datetime
            from PyQt6.QtWidgets import QFileDialog
            
            # Get save file path
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Low Stock Report", 
                f"low_stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Medicine Name', 'Current Stock', 'Category', 'Supplier', 'Reorder Level', 'Status'])
                    
                    for med in medicines:
                        supplier_name = self.get_supplier_name(med.get('supplier_id'))
                        writer.writerow([
                            med['name'],
                            med['quantity'],
                            med['category'],
                            supplier_name,
                            med.get('reorder_level', 'N/A'),
                            'Low Stock'
                        ])
                
                self.show_success_message(f"Low stock report exported to: {file_path}")
        except Exception as e:
            self.show_error_message(f"Failed to export low stock report: {e}")
    
    def export_expired_report(self, medicines):
        """Export expired medicines report to CSV"""
        try:
            import csv
            from datetime import datetime
            from PyQt6.QtWidgets import QFileDialog
            
            # Get save file path
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Expired Medicines Report", 
                f"expired_medicines_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Medicine Name', 'Expiry Date', 'Batch Number', 'Quantity', 'Status'])
                    
                    for med in medicines:
                        writer.writerow([
                            med['name'],
                            med['expiry_date'],
                            med.get('batch_number', 'N/A'),
                            med['quantity'],
                            'EXPIRED'
                        ])
                
                self.show_success_message(f"Expired medicines report exported to: {file_path}")
        except Exception as e:
            self.show_error_message(f"Failed to export expired medicines report: {e}")
    
    def create_chart_frame(self, title, subtitle):
        """Create a real sales chart frame with matplotlib"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #d5dbdb;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet("color: #7f8c8d;")
        
        # Create matplotlib chart
        chart_widget = self.create_sales_chart()
        
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(chart_widget)
        
        return frame
    
    def create_sales_chart(self):
        """Create a robust sales chart with proper error handling"""
        try:
            # Create figure and canvas with improved dimensions
            figure = Figure(figsize=(14, 10), dpi=100)
            canvas = FigureCanvas(figure)
            
            # Set up the plot with consistent styling
            ax = figure.add_subplot(111)
            
            # Set colors to match application theme
            bg_color = '#ecf0f1'
            primary_color = '#1AAE4A'
            text_color = '#2c3e50'
            grid_color = '#bdc3c7'
            
            figure.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)
            
            # Remove spines for clean look
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            # Set professional grid
            ax.grid(True, color=grid_color, linestyle='-', alpha=0.3, linewidth=1)
            
            # Get and validate sales data
            sales_data, dates = self.get_sales_data_for_chart()
            
            print(f"DEBUG: Chart data - sales_data: {sales_data}, dates: {dates}")
            
            if sales_data is not None and dates is not None and len(sales_data) > 0 and len(dates) > 0:
                print(f"DEBUG: Creating chart with {len(sales_data)} data points")
                
                # Create the bar chart with consistent styling
                bars = ax.bar(range(len(dates)), sales_data, color=primary_color, 
                             alpha=0.8, width=0.4)
                
                # Add value labels on bars
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                           f'₹{int(height)}', ha='center', va='bottom',
                           fontfamily='Segoe UI', fontsize=9, color=text_color)
                
                # Format x-axis with weekday names
                weekdays = [d.strftime('%A') for d in dates]
                ax.set_xticks(range(len(dates)))
                ax.set_xticklabels(weekdays, fontfamily='Segoe UI', fontsize=10, 
                                  rotation=45, ha='right')
                
                # Format y-axis with proper labels
                ax.set_ylabel('Sales (₹)', fontfamily='Segoe UI', fontsize=12, 
                             color=text_color, fontweight='bold')
                
                # Add y-axis ticks with dollar formatting
                max_sales = max(sales_data) if len(sales_data) > 0 else 200
                max_sales_int = int(max_sales)
                y_ticks = range(0, max_sales_int + 50, 50)
                ax.set_yticks(y_ticks)
                ax.set_yticklabels([f'₹{y}' for y in y_ticks], 
                                  fontfamily='Segoe UI', fontsize=10, color=text_color)
                
                # Add x-axis line at bottom
                ax.axhline(y=0, color=text_color, linewidth=2, alpha=0.8)
                
                # Set title
                ax.set_title('Daily Sales Trend', fontfamily='Segoe UI', fontsize=14, 
                            fontweight='bold', color=text_color, pad=25)
            else:
                print("DEBUG: No valid sales data, showing empty chart message")
                # Handle empty data case with informative message
                ax.text(0.5, 0.5, 'No sales data available\nAdd some sales to see the chart', 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='#7f8c8d')
                ax.set_xlim(-1, 1)
                ax.set_ylim(0, 1)
            
            figure.tight_layout()
            
            # CRITICAL FIX: Force canvas to update and refresh
            canvas.draw()
            canvas.flush_events()
            
            return canvas
            
        except Exception as e:
            print(f"ERROR in create_sales_chart: {e}")
            import traceback
            traceback.print_exc()
            
            # Return a simple error canvas
            figure = Figure(figsize=(14, 10), dpi=100)
            canvas = FigureCanvas(figure)
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Chart Error: {e}', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12, color='#e74c3c')
            figure.tight_layout()
            return canvas
    
    def get_sales_data_for_chart(self):
        """Get and validate sales data for chart with robust error handling"""
        try:
            # Check if database functions are available by trying to import them
            try:
                from database.modern_db import get_recent_sales as db_get_recent_sales
                # Test if the function works
                test_sales = db_get_recent_sales(1)  # Just get 1 record to test
                print("DEBUG: Database functions are available and working")
            except Exception as e:
                print(f"DEBUG: Database functions not available: {e}")
                return [], []
            
            # Get recent sales data for last 7 days
            recent_sales = get_recent_sales(50)  # Get more records to ensure we have data
            
            if not recent_sales:
                print("DEBUG: No sales data from database")
                return [], []
            
            # Process and validate data
            sales_by_date = {}
            
            for sale in recent_sales:
                try:
                    # Validate sale data structure
                    if not isinstance(sale, dict) or 'sale_date' not in sale or 'total_amount' not in sale:
                        print(f"DEBUG: Invalid sale data: {sale}")
                        continue
                    
                    # Parse date safely
                    date_str = str(sale['sale_date'])[:10]
                    if len(date_str) != 10 or '-' not in date_str:
                        print(f"DEBUG: Invalid date format: {date_str}")
                        continue
                    
                    # Validate amount
                    amount = float(sale['total_amount'])
                    if amount < 0:
                        print(f"DEBUG: Negative amount: {amount}")
                        continue
                    
                    # Aggregate by date
                    if date_str not in sales_by_date:
                        sales_by_date[date_str] = 0
                    sales_by_date[date_str] += amount
                    
                except (ValueError, TypeError) as e:
                    print(f"DEBUG: Error processing sale: {e}, {sale}")
                    continue
            
            if not sales_by_date:
                print("DEBUG: No valid sales data after processing")
                return [], []
            
            # Create 7-day range starting from 6 days ago to today
            today = datetime.now().date()
            week_dates = []
            for i in range(6, -1, -1):  # 6 days ago to today
                date_obj = today - timedelta(days=i)
                week_dates.append(date_obj)
            
            # Build sales data for the 7-day period
            dates = []
            sales_data = []
            
            for date_obj in week_dates:
                date_str = date_obj.strftime('%Y-%m-%d')
                if date_str in sales_by_date:
                    dates.append(date_obj)
                    sales_data.append(sales_by_date[date_str])
                else:
                    # No sales for this date, add zero
                    dates.append(date_obj)
                    sales_data.append(0)
            
            print(f"DEBUG: Final chart data - dates: {len(dates)}, sales_data: {len(sales_data)}")
            print(f"DEBUG: Dates: {[d.strftime('%Y-%m-%d') for d in dates]}")
            print(f"DEBUG: Sales: {sales_data}")
            
            if not dates or not sales_data:
                return [], []
            
            return sales_data, dates
            
        except Exception as e:
            print(f"DEBUG: Critical error in get_sales_data_for_chart: {e}")
            import traceback
            traceback.print_exc()
            return [], []
    
    def create_recent_sales_table(self):
        """Create recent sales table with real data"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #d5dbdb;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        title_label = QLabel("Recent Sales")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        
        subtitle_label = QLabel("Latest transactions from your pharmacy")
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet("color: #7f8c8d;")
        
        # Table
        table = QTableWidget(5, 3)
        table.setHorizontalHeaderLabels(["Customer", "Date", "Amount"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #2c3e50;
                font-weight: bold;
                border: none;
                padding: 8px;
            }
        """)
        
        # Get real data from database
        try:
            recent_sales = get_recent_sales(5)
        except Exception as e:
            print(f"Error getting recent sales: {e}")
            recent_sales = []
        
        # Populate table with real data
        if recent_sales:
            for row, sale in enumerate(recent_sales):
                customer_item = QTableWidgetItem(sale['customer_name'])
                customer_item.setFont(QFont("Segoe UI", 10))
                table.setItem(row, 0, customer_item)
                
                date_item = QTableWidgetItem(sale['sale_date'][:10])  # Just date part
                date_item.setFont(QFont("Segoe UI", 10))
                table.setItem(row, 1, date_item)
                
                amount_item = QTableWidgetItem(f"₹{sale['total_amount']:.2f}")
                amount_item.setFont(QFont("Segoe UI", 10))
                table.setItem(row, 2, amount_item)
        else:
            no_data_item = QTableWidgetItem("No sales data available")
            no_data_item.setFont(QFont("Segoe UI", 10))
            table.setItem(0, 0, no_data_item)
        
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(table)
        
        return frame
    
    def create_inventory_content(self, layout):
        """Create inventory management content with real data - FIXED VERSION"""
        title = QLabel("Medicine Inventory")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        subtitle = QLabel("Manage your pharmacy's medicine stock")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search medicines...")
        search_input.setFixedHeight(40)
        search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d5dbdb;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1AAE4A;
            }
        """)
        search_input.textChanged.connect(self.search_medicines)
        
        add_btn = QPushButton("➕ Add Medicine")
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #1AAE4A;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #168f3c;
            }
        """)
        add_btn.clicked.connect(self.add_medicine)
        
        controls_layout.addWidget(search_input)
        controls_layout.addWidget(add_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # CRITICAL FIX: Add QScrollArea container for inventory table (like customers table)
        inventory_scroll_area = QScrollArea()
        inventory_scroll_area.setWidgetResizable(True)
        inventory_scroll_area.setMinimumHeight(600)
        inventory_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
                min-height: 600px;
            }
            QScrollBar:vertical {
                width: 14px;
                background: #ecf0f1;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 7px;
                min-height: 50px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Inventory table - Set up columns first with improved height
        self.inventory_table = QTableWidget()
        self.inventory_table.setHorizontalHeaderLabels(["Name", "Category", "Supplier", "Stock Status", "Expiry", "Quantity", "Price", "Drawer", "Shelf", "Actions"])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.inventory_table.verticalHeader().setVisible(False)
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
                border-radius: 8px;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 15px 10px;
                border-bottom: 1px solid #e8e8e8;
                color: #333333;
                background-color: white;
                font-size: 13px;
                font-family: 'Segoe UI';
            }
            QTableWidget::item:alternate {
                background-color: #f9f9f9;
            }
            QTableWidget::item:selected {
                background-color: #e3f2e9;
                color: #1AAE4A;
                border-left: 3px solid #1AAE4A;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #ffffff;
                color: #555555;
                font-weight: 600;
                border: none;
                border-bottom: 2px solid #1AAE4A;
                padding: 12px 10px;
                font-size: 13px;
                font-family: 'Segoe UI';
                min-height: 50px;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #ffffff;
                border: none;
            }
        """)
        self.inventory_table.setSortingEnabled(True)
        # Set minimum row height for better visibility
        self.inventory_table.verticalHeader().setMinimumSectionSize(50)
        
        # CRITICAL FIX: Set fixed height for internal table scrolling (like customers table)
        self.inventory_table.setFixedHeight(700)
        self.inventory_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Add scrollbar styling to match customers table
        self.inventory_table.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                width: 14px;
                background: #ecf0f1;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 7px;
                min-height: 50px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Set the table as the widget for the scroll area
        inventory_scroll_area.setWidget(self.inventory_table)
        
        layout.addWidget(inventory_scroll_area)
        layout.addStretch()

        # CRITICAL FIX: Load initial data immediately after table creation
        self.load_inventory_data()
    
    def search_medicines(self, text):
        """Search medicines in inventory"""
        try:
            medicines = get_medicines(search=text)
            self.populate_inventory_table(medicines)
        except Exception as e:
            print(f"Error searching medicines: {e}")
    
    def load_inventory_data(self):
        """Load all medicines from database - FIXED VERSION"""
        try:
            medicines = get_medicines()
            if medicines:
                # CRITICAL FIX: Ensure table has columns set up before populating
                if self.inventory_table.columnCount() == 0:
                    headers = ["Name", "Category", "Stock Status", "Expiry", "Quantity", "Price", "Drawer", "Shelf", "Actions"]
                    self.inventory_table.setColumnCount(len(headers))
                    self.inventory_table.setHorizontalHeaderLabels(headers)
                
                # Add error handling around table population
                try:
                    self.populate_inventory_table(medicines)
                except Exception as table_error:
                    print(f"Error populating inventory table: {table_error}")
                    import traceback
                    traceback.print_exc()
                    # Show error message to user
                    self.show_error_message(f"Failed to display inventory data: {table_error}")
            else:
                print("No medicines found in database")
                self.show_error_message("No medicines found in database. Please add medicines first.")
        except Exception as e:
            print(f"Error loading inventory: {e}")
            # Show error message to user
            self.show_error_message("Failed to load inventory data")
    
    def populate_inventory_table(self, medicines):
        """Populate inventory table with medicine data - FIXED VERSION"""
        print(f"DEBUG: populate_inventory_table called with {len(medicines)} medicines")
        
        # CRITICAL FIX: Clear existing data first
        self.inventory_table.setRowCount(0)
        self.inventory_table.setRowCount(len(medicines))
        
        for row, med in enumerate(medicines):
            print(f"DEBUG: Adding medicine {row}: {med['name']}")
            
            # Name
            name_item = QTableWidgetItem(med['name'])
            name_item.setFont(QFont("Segoe UI", 10))
            self.inventory_table.setItem(row, 0, name_item)
            
            # Category
            category_item = QTableWidgetItem(med['category'])
            category_item.setFont(QFont("Segoe UI", 10))
            self.inventory_table.setItem(row, 1, category_item)
            
            # Stock Status
            stock_status = QTableWidgetItem(med['stock_status'])
            stock_status.setFont(QFont("Segoe UI", 10))
            if med['stock_status'] == 'Low Stock':
                stock_status.setForeground(QColor("#e67e22"))
            elif med['stock_status'] == 'Out of Stock':
                stock_status.setForeground(QColor("#e74c3c"))
            self.inventory_table.setItem(row, 2, stock_status)
            
            # Expiry
            expiry_item = QTableWidgetItem(med['expiry_date'])
            expiry_item.setFont(QFont("Segoe UI", 10))
            if med['expiry_status'] == 'Expired':
                expiry_item.setForeground(QColor("#e74c3c"))
            elif med['expiry_status'] == 'Near Expiry':
                expiry_item.setForeground(QColor("#e67e22"))
            self.inventory_table.setItem(row, 3, expiry_item)
            
            # Quantity
            qty_item = QTableWidgetItem(str(med['quantity']))
            qty_item.setFont(QFont("Segoe UI", 10))
            self.inventory_table.setItem(row, 4, qty_item)
            
            # Price
            price_item = QTableWidgetItem(f"₹{med['price']:.2f}")
            price_item.setFont(QFont("Segoe UI", 10))
            self.inventory_table.setItem(row, 5, price_item)
            
            # Drawer (NEW)
            drawer_item = QTableWidgetItem(med.get('drawer_number', '-'))
            drawer_item.setFont(QFont("Segoe UI", 10))
            self.inventory_table.setItem(row, 6, drawer_item)
            
            # Shelf (NEW)
            shelf_item = QTableWidgetItem(med.get('shelf_location', '-'))
            shelf_item.setFont(QFont("Segoe UI", 10))
            self.inventory_table.setItem(row, 7, shelf_item)
            
            # Actions
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedHeight(25)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 0px 8px 9px 8px;
                    font-size: 10px;
                    font-weight: bold;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            edit_btn.clicked.connect(lambda checked, med_id=med['id']: self.edit_medicine(med_id))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setFixedHeight(25)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 0px 8px 9px 8px;
                    font-size: 10px;
                    font-weight: bold;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, med_id=med['id']: self.delete_medicine(med_id))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.inventory_table.setCellWidget(row, 8, actions_widget)
        
        print(f"DEBUG: Inventory table populated with {len(medicines)} rows")
        
        # CRITICAL FIX: Ensure table is visible
        if not self.inventory_table.isVisible():
            self.inventory_table.setVisible(True)
    
    def add_medicine(self):
        """Add new medicine"""
        print("Add medicine clicked")
        # Create a simple add medicine dialog
        self.show_add_medicine_dialog()
    
    def show_add_medicine_dialog(self):
        """Show add medicine dialog"""
        try:
            print("DEBUG: Creating Add Medicine dialog...")
            
            # Create dialog window
            dialog = QDialog(self)
            dialog.setWindowTitle("Add Medicine")
            dialog.setGeometry(100, 100, 500, 450)
            dialog.setStyleSheet("background-color: white;")
            dialog.setModal(True)  # Make it modal
            
            layout = QVBoxLayout(dialog)
            
            # Title
            title = QLabel("Add New Medicine")
            title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            title.setStyleSheet("color: #2c3e50;")
            layout.addWidget(title)
            
            # Form fields
            form_layout = QGridLayout()
            
            # Name
            name_label = QLabel("Medicine Name:")
            name_label.setFont(QFont("Segoe UI", 10))
            name_label.setStyleSheet("color: #2c3e50;")
            name_input = QLineEdit()
            name_input.setPlaceholderText("Enter medicine name")
            name_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(name_label, 0, 0)
            form_layout.addWidget(name_input, 0, 1)
            
            # Category
            category_label = QLabel("Category:")
            category_label.setFont(QFont("Segoe UI", 10))
            category_label.setStyleSheet("color: #2c3e50;")
            category_combo = QComboBox()
            category_combo.addItems(["Analgesics", "Antibiotics", "Cardiovascular", "Antidiabetics", "Respiratory", "Antihistamines"])
            category_combo.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(category_label, 1, 0)
            form_layout.addWidget(category_combo, 1, 1)
            
            # Batch Number
            batch_label = QLabel("Batch Number:")
            batch_label.setFont(QFont("Segoe UI", 10))
            batch_label.setStyleSheet("color: #2c3e50;")
            batch_input = QLineEdit()
            batch_input.setPlaceholderText("Enter batch number")
            batch_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(batch_label, 2, 0)
            form_layout.addWidget(batch_input, 2, 1)
            
            # Expiry Date
            expiry_label = QLabel("Expiry Date:")
            expiry_label.setFont(QFont("Segoe UI", 10))
            expiry_label.setStyleSheet("color: #2c3e50;")
            expiry_input = QDateEdit()
            expiry_input.setCalendarPopup(True)
            expiry_input.setDate(QDate.currentDate().addYears(1))  # Default to 1 year from now
            expiry_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(expiry_label, 3, 0)
            form_layout.addWidget(expiry_input, 3, 1)
            
            # Quantity
            qty_label = QLabel("Quantity:")
            qty_label.setFont(QFont("Segoe UI", 10))
            qty_label.setStyleSheet("color: #2c3e50;")
            qty_input = QLineEdit()
            qty_input.setPlaceholderText("Enter quantity")
            qty_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(qty_label, 4, 0)
            form_layout.addWidget(qty_input, 4, 1)
            
            # Reorder Level
            reorder_label = QLabel("Reorder Level:")
            reorder_label.setFont(QFont("Segoe UI", 10))
            reorder_label.setStyleSheet("color: #2c3e50;")
            reorder_input = QLineEdit()
            reorder_input.setPlaceholderText("Enter reorder level (default: 10)")
            reorder_input.setText("10")
            reorder_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(reorder_label, 5, 0)
            form_layout.addWidget(reorder_input, 5, 1)
            
            # Price
            price_label = QLabel("Price:")
            price_label.setFont(QFont("Segoe UI", 10))
            price_label.setStyleSheet("color: #2c3e50;")
            price_input = QLineEdit()
            price_input.setPlaceholderText("Enter price")
            price_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(price_label, 6, 0)
            form_layout.addWidget(price_input, 6, 1)
            
            # Supplier
            supplier_label = QLabel("Supplier:")
            supplier_label.setFont(QFont("Segoe UI", 10))
            supplier_label.setStyleSheet("color: #2c3e50;")
            supplier_combo = QComboBox()
            supplier_combo.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            self.load_supplier_options(supplier_combo)  # Load real-time supplier data
            form_layout.addWidget(supplier_label, 7, 0)
            form_layout.addWidget(supplier_combo, 7, 1)
            
            # Drawer Number (NEW)
            drawer_label = QLabel("Drawer Number:")
            drawer_label.setFont(QFont("Segoe UI", 10))
            drawer_label.setStyleSheet("color: #2c3e50;")
            drawer_input = QLineEdit()
            drawer_input.setPlaceholderText("e.g., A1, B2, C3")
            drawer_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(drawer_label, 8, 0)
            form_layout.addWidget(drawer_input, 8, 1)
            
            # Shelf Location (NEW)
            shelf_label = QLabel("Shelf Location:")
            shelf_label.setFont(QFont("Segoe UI", 10))
            shelf_label.setStyleSheet("color: #2c3e50;")
            shelf_combo = QComboBox()
            shelf_combo.addItems(["Top", "Middle", "Bottom"])
            shelf_combo.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(shelf_label, 9, 0)
            form_layout.addWidget(shelf_combo, 9, 1)
            
            layout.addLayout(form_layout)
            
            # Buttons
            btn_layout = QHBoxLayout()
            
            save_btn = QPushButton("Save Medicine")
            save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1AAE4A;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #168f3c;
                }
            """)
            
            # Add debug to save button
            def debug_save():
                print("DEBUG: Save Medicine button clicked!")
                try:
                    self.save_new_medicine(dialog, name_input, category_combo, qty_input, price_input, 
                                         batch_input, expiry_input, reorder_input, supplier_combo,
                                         drawer_input, shelf_combo)
                except Exception as e:
                    print(f"DEBUG: Error in save_new_medicine: {e}")
                    import traceback
                    traceback.print_exc()
            
            save_btn.clicked.connect(debug_save)
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            cancel_btn.clicked.connect(dialog.close)
            
            btn_layout.addWidget(save_btn)
            btn_layout.addWidget(cancel_btn)
            
            layout.addLayout(btn_layout)
            
            print("DEBUG: Dialog created successfully, showing...")
            dialog.exec()  # Use exec() for modal dialog
            print("DEBUG: Dialog closed")
            
        except Exception as e:
            print(f"DEBUG: Error creating dialog: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to open Add Medicine dialog: {e}")
    
    def save_new_medicine(self, dialog, name_input, category_combo, qty_input, price_input, 
                         batch_input=None, expiry_input=None, reorder_input=None, supplier_combo=None,
                         drawer_input=None, shelf_combo=None):
        """Save new medicine to database"""
        try:
            print("DEBUG: save_new_medicine called")
            
            name = name_input.text().strip()
            category = category_combo.currentText()
            quantity = int(qty_input.text())
            price = float(price_input.text())
            
            # Get optional fields
            batch_number = batch_input.text().strip() if batch_input and batch_input.text().strip() else None
            expiry_date = expiry_input.date().toString("yyyy-MM-dd") if expiry_input else "2026-12-31"
            reorder_level = int(reorder_input.text()) if reorder_input and reorder_input.text().strip() else 10
            supplier_name = supplier_combo.currentText() if supplier_combo else None
            
            # Get drawer and shelf fields (NEW)
            drawer_number = drawer_input.text().strip() if drawer_input and drawer_input.text().strip() else None
            shelf_location = shelf_combo.currentText() if shelf_combo else None
            
            print(f"DEBUG: Medicine data - Name: {name}, Category: {category}, Quantity: {quantity}, Price: {price}")
            print(f"DEBUG: Optional data - Batch: {batch_number}, Expiry: {expiry_date}, Reorder: {reorder_level}, Supplier: {supplier_name}")
            print(f"DEBUG: Location data - Drawer: {drawer_number}, Shelf: {shelf_location}")
            
            if not name or quantity < 0 or price < 0:
                print("DEBUG: Validation failed")
                self.show_error_message("Please enter valid medicine details")
                return
            
            # Save to database with drawer and shelf info
            medicine_id = create_medicine(
                name=name,
                category=category,
                quantity=quantity,
                price=price,
                expiry_date=expiry_date,
                batch_number=batch_number or f"BATCH{datetime.now().strftime('%Y%m%d')}{self.inventory_table.rowCount() + 1}",
                supplier_id=self.get_supplier_id(supplier_name) if supplier_name and supplier_name != "Select Supplier" else None,
                drawer_number=drawer_number,
                shelf_location=shelf_location
            )
            
            if medicine_id:
                print(f"DEBUG: Medicine saved to database with ID: {medicine_id}")
                
                # Close dialog first
                dialog.close()
                
                print("DEBUG: Dialog closed")
                
                # Refresh the inventory data to show the new medicine
                self.load_inventory_data()
                
                self.show_success_message("Medicine added successfully!")
                
                print("DEBUG: Success message shown")
            else:
                print("DEBUG: Failed to save medicine to database")
                self.show_error_message("Failed to save medicine to database")
            
        except ValueError as ve:
            print(f"DEBUG: ValueError: {ve}")
            self.show_error_message("Please enter valid quantity and price")
        except Exception as e:
            print(f"DEBUG: Exception in save_new_medicine: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to add medicine: {e}")
    
    def get_supplier_id(self, supplier_name):
        """Get supplier ID from name"""
        try:
            # Query the suppliers table to get the actual supplier ID
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM suppliers WHERE name = ?", (supplier_name,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    return None
        except Exception as e:
            print(f"Error getting supplier ID: {e}")
            return None
    
    def show_error_message(self, message):
        """Show error message to user"""
        error_dialog = QWidget()
        error_dialog.setWindowTitle("Error")
        error_dialog.setGeometry(100, 100, 300, 150)
        error_dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(error_dialog)
        
        error_label = QLabel(message)
        error_label.setFont(QFont("Segoe UI", 10))
        error_label.setStyleSheet("color: #e74c3c;")
        error_label.setWordWrap(True)
        
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        ok_btn.clicked.connect(error_dialog.close)
        
        layout.addWidget(error_label)
        layout.addWidget(ok_btn)
        
        error_dialog.show()
    
    def show_success_message(self, message):
        """Show success message to user"""
        success_dialog = QWidget()
        success_dialog.setWindowTitle("Success")
        success_dialog.setGeometry(100, 100, 300, 150)
        success_dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(success_dialog)
        
        success_label = QLabel(message)
        success_label.setFont(QFont("Segoe UI", 10))
        success_label.setStyleSheet("color: #27ae60;")
        success_label.setWordWrap(True)
        
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        ok_btn.clicked.connect(success_dialog.close)
        
        layout.addWidget(success_label)
        layout.addWidget(ok_btn)
        
        success_dialog.show()
    
    def edit_medicine(self, med_id):
        """Edit medicine - Opens dialog with medicine data for editing"""
        print(f"Edit medicine {med_id} clicked")
        
        try:
            # Get the medicine details from database
            medicines = get_medicines()
            medicine_data = None
            
            for med in medicines:
                if med['id'] == med_id:
                    medicine_data = med
                    break
            
            if not medicine_data:
                # Try to get from database directly
                from database.modern_db import db
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT id, name, category, quantity, price, expiry_date, 
                               batch_number, supplier_id, reorder_level
                        FROM medicines WHERE id = ?
                    """, (med_id,))
                    row = cursor.fetchone()
                    if row:
                        medicine_data = {
                            'id': row[0],
                            'name': row[1],
                            'category': row[2],
                            'quantity': row[3],
                            'price': row[4],
                            'expiry_date': row[5],
                            'batch_number': row[6],
                            'supplier_id': row[7],
                            'reorder_level': row[8]
                        }
            
            if medicine_data:
                self.show_edit_medicine_dialog(medicine_data)
            else:
                self.show_error_message("Medicine not found")
                
        except Exception as e:
            print(f"Error loading medicine for edit: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to load medicine data: {e}")
    
    def show_edit_medicine_dialog(self, medicine_data):
        """Show edit medicine dialog with pre-filled data"""
        try:
            print(f"DEBUG: Creating Edit Medicine dialog for: {medicine_data['name']}")
            
            # Create dialog window
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Medicine")
            dialog.setGeometry(100, 100, 500, 500)
            dialog.setStyleSheet("background-color: white;")
            dialog.setModal(True)
            
            layout = QVBoxLayout(dialog)
            
            # Title
            title = QLabel("Edit Medicine Details")
            title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            title.setStyleSheet("color: #2c3e50;")
            layout.addWidget(title)
            
            # Medicine ID (hidden but stored)
            med_id = medicine_data['id']
            
            # Form fields
            form_layout = QGridLayout()
            
            # Name
            name_label = QLabel("Medicine Name:")
            name_label.setFont(QFont("Segoe UI", 10))
            name_label.setStyleSheet("color: #2c3e50;")
            name_input = QLineEdit()
            name_input.setText(medicine_data.get('name', ''))
            name_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(name_label, 0, 0)
            form_layout.addWidget(name_input, 0, 1)
            
            # Category
            category_label = QLabel("Category:")
            category_label.setFont(QFont("Segoe UI", 10))
            category_label.setStyleSheet("color: #2c3e50;")
            category_combo = QComboBox()
            categories = ["Analgesics", "Antibiotics", "Cardiovascular", "Antidiabetics", 
                         "Respiratory", "Antihistamines", "Gastrointestinal", "Neurological", 
                         "Dermatological", "Other"]
            category_combo.addItems(categories)
            # Set current category
            current_category = medicine_data.get('category', '')
            if current_category in categories:
                category_combo.setCurrentText(current_category)
            category_combo.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(category_label, 1, 0)
            form_layout.addWidget(category_combo, 1, 1)
            
            # Batch Number
            batch_label = QLabel("Batch Number:")
            batch_label.setFont(QFont("Segoe UI", 10))
            batch_label.setStyleSheet("color: #2c3e50;")
            batch_input = QLineEdit()
            batch_input.setText(medicine_data.get('batch_number', ''))
            batch_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(batch_label, 2, 0)
            form_layout.addWidget(batch_input, 2, 1)
            
            # Expiry Date
            expiry_label = QLabel("Expiry Date:")
            expiry_label.setFont(QFont("Segoe UI", 10))
            expiry_label.setStyleSheet("color: #2c3e50;")
            expiry_input = QDateEdit()
            expiry_input.setCalendarPopup(True)
            # Parse the expiry date
            expiry_date_str = medicine_data.get('expiry_date', '')
            if expiry_date_str:
                try:
                    from datetime import datetime
                    expiry_date = datetime.strptime(str(expiry_date_str), '%Y-%m-%d').date()
                    from PyQt6.QtCore import QDate
                    expiry_input.setDate(QDate(expiry_date.year, expiry_date.month, expiry_date.day))
                except:
                    expiry_input.setDate(QDate.currentDate().addYears(1))
            else:
                expiry_input.setDate(QDate.currentDate().addYears(1))
            expiry_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(expiry_label, 3, 0)
            form_layout.addWidget(expiry_input, 3, 1)
            
            # Quantity
            qty_label = QLabel("Quantity:")
            qty_label.setFont(QFont("Segoe UI", 10))
            qty_label.setStyleSheet("color: #2c3e50;")
            qty_input = QLineEdit()
            qty_input.setText(str(medicine_data.get('quantity', 0)))
            qty_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(qty_label, 4, 0)
            form_layout.addWidget(qty_input, 4, 1)
            
            # Reorder Level
            reorder_label = QLabel("Reorder Level:")
            reorder_label.setFont(QFont("Segoe UI", 10))
            reorder_label.setStyleSheet("color: #2c3e50;")
            reorder_input = QLineEdit()
            reorder_level = medicine_data.get('reorder_level', 10)
            reorder_input.setText(str(reorder_level) if reorder_level else "10")
            reorder_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(reorder_label, 5, 0)
            form_layout.addWidget(reorder_input, 5, 1)
            
            # Price
            price_label = QLabel("Price:")
            price_label.setFont(QFont("Segoe UI", 10))
            price_label.setStyleSheet("color: #2c3e50;")
            price_input = QLineEdit()
            price_input.setText(str(medicine_data.get('price', 0.0)))
            price_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(price_label, 6, 0)
            form_layout.addWidget(price_input, 6, 1)
            
            # Supplier
            supplier_label = QLabel("Supplier:")
            supplier_label.setFont(QFont("Segoe UI", 10))
            supplier_label.setStyleSheet("color: #2c3e50;")
            supplier_combo = QComboBox()
            supplier_combo.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            self.load_supplier_options(supplier_combo)
            
            # Set current supplier
            current_supplier_id = medicine_data.get('supplier_id')
            if current_supplier_id:
                # Find and set the current supplier
                for i in range(supplier_combo.count()):
                    data = supplier_combo.itemData(i)
                    if data == current_supplier_id:
                        supplier_combo.setCurrentIndex(i)
                        break
            form_layout.addWidget(supplier_label, 7, 0)
            form_layout.addWidget(supplier_combo, 7, 1)
            
            # Drawer Number (NEW)
            drawer_label = QLabel("Drawer Number:")
            drawer_label.setFont(QFont("Segoe UI", 10))
            drawer_label.setStyleSheet("color: #2c3e50;")
            drawer_input = QLineEdit()
            drawer_input.setText(medicine_data.get('drawer_number', ''))
            drawer_input.setPlaceholderText("e.g., A1, B2, C3")
            drawer_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(drawer_label, 8, 0)
            form_layout.addWidget(drawer_input, 8, 1)
            
            # Shelf Location (NEW)
            shelf_label = QLabel("Shelf Location:")
            shelf_label.setFont(QFont("Segoe UI", 10))
            shelf_label.setStyleSheet("color: #2c3e50;")
            shelf_combo = QComboBox()
            shelf_combo.addItems(["Top", "Middle", "Bottom"])
            shelf_combo.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            # Set current shelf location
            current_shelf = medicine_data.get('shelf_location', 'Middle')
            if current_shelf in ["Top", "Middle", "Bottom"]:
                shelf_combo.setCurrentText(current_shelf)
            form_layout.addWidget(shelf_label, 9, 0)
            form_layout.addWidget(shelf_combo, 9, 1)
            
            layout.addLayout(form_layout)
            
            # Buttons
            btn_layout = QHBoxLayout()
            
            update_btn = QPushButton("Update Medicine")
            update_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            
            # Add debug to update button
            def debug_update():
                print("DEBUG: Update Medicine button clicked!")
                try:
                    self.update_medicine_record(dialog, med_id, name_input, category_combo, 
                                               qty_input, price_input, batch_input, 
                                               expiry_input, reorder_input, supplier_combo,
                                               drawer_input, shelf_combo)
                except Exception as e:
                    print(f"DEBUG: Error in update_medicine_record: {e}")
                    import traceback
                    traceback.print_exc()
            
            update_btn.clicked.connect(debug_update)
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            cancel_btn.clicked.connect(dialog.close)
            
            btn_layout.addWidget(update_btn)
            btn_layout.addWidget(cancel_btn)
            
            layout.addLayout(btn_layout)
            
            print("DEBUG: Dialog created successfully, showing...")
            dialog.exec()
            print("DEBUG: Dialog closed")
            
        except Exception as e:
            print(f"DEBUG: Error creating edit dialog: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to open Edit Medicine dialog: {e}")
    
    def update_medicine_record(self, dialog, med_id, name_input, category_combo, qty_input, 
                                price_input, batch_input, expiry_input, reorder_input, supplier_combo,
                                drawer_input=None, shelf_combo=None):
        """Update medicine record in database"""
        try:
            print(f"DEBUG: update_medicine_record called for medicine ID: {med_id}")
            
            name = name_input.text().strip()
            category = category_combo.currentText()
            quantity = int(qty_input.text())
            price = float(price_input.text())
            
            # Get optional fields
            batch_number = batch_input.text().strip() if batch_input.text().strip() else None
            expiry_date = expiry_input.date().toString("yyyy-MM-dd")
            reorder_level = int(reorder_input.text()) if reorder_input.text().strip() else 10
            supplier_id = supplier_combo.currentData()
            
            # Get drawer and shelf location if provided
            drawer_number = drawer_input.text().strip() if drawer_input else None
            shelf_location = shelf_combo.currentText() if shelf_combo else "Middle"
            
            print(f"DEBUG: Updated medicine data - Name: {name}, Category: {category}, Quantity: {quantity}, Price: {price}")
            print(f"DEBUG: Optional data - Batch: {batch_number}, Expiry: {expiry_date}, Reorder: {reorder_level}, Supplier ID: {supplier_id}")
            print(f"DEBUG: Location data - Drawer: {drawer_number}, Shelf: {shelf_location}")
            
            if not name or quantity < 0 or price < 0:
                print("DEBUG: Validation failed")
                self.show_error_message("Please enter valid medicine details")
                return
            
            # Try to update via database function first
            try:
                success = update_medicine(
                    medicine_id=med_id,
                    name=name,
                    category=category,
                    quantity=quantity,
                    price=price,
                    expiry_date=expiry_date,
                    batch_number=batch_number,
                    reorder_level=reorder_level,
                    supplier_id=supplier_id
                )
            except Exception as db_error:
                print(f"DEBUG: Database function failed, trying direct update: {db_error}")
                # Fallback to direct database update
                from database.modern_db import db
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE medicines 
                        SET name = ?, category = ?, quantity = ?, price = ?, 
                            expiry_date = ?, batch_number = ?, reorder_level = ?, supplier_id = ?,
                            drawer_number = ?, shelf_location = ?
                        WHERE id = ?
                    """, (name, category, quantity, price, expiry_date, batch_number, 
                          reorder_level, supplier_id, drawer_number, shelf_location, med_id))
                success = True
            
            if success:
                print(f"DEBUG: Medicine updated successfully!")
                
                # Close dialog first
                dialog.close()
                
                print("DEBUG: Dialog closed")
                
                # Refresh the inventory data to show the updated medicine
                self.load_inventory_data()
                
                self.show_success_message("Medicine updated successfully!")
                
                print("DEBUG: Success message shown")
            else:
                print("DEBUG: Failed to update medicine in database")
                self.show_error_message("Failed to update medicine in database")
            
        except ValueError as ve:
            print(f"DEBUG: ValueError: {ve}")
            self.show_error_message("Please enter valid quantity and price")
        except Exception as e:
            print(f"DEBUG: Exception in update_medicine_record: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to update medicine: {e}")
    
    def delete_medicine(self, med_id):
        """Delete medicine with confirmation"""
        print(f"Delete medicine {med_id} clicked")
        
        # Show confirmation dialog
        self.show_delete_confirmation(med_id)
    
    def show_delete_confirmation(self, med_id):
        """Show delete confirmation dialog"""
        try:
            # Get medicine name for display
            medicines = get_medicines()
            medicine_name = "this medicine"
            for med in medicines:
                if med['id'] == med_id:
                    medicine_name = med['name']
                    break
            
            # Create confirmation dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Confirm Delete")
            dialog.setGeometry(100, 100, 400, 200)
            dialog.setStyleSheet("background-color: white;")
            dialog.setModal(True)
            
            layout = QVBoxLayout(dialog)
            
            # Warning icon and message
            warning_label = QLabel("⚠️")
            warning_label.setFont(QFont("Segoe UI", 40))
            warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(warning_label)
            
            # Title
            title = QLabel("Confirm Delete")
            title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            title.setStyleSheet("color: #e74c3c;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            # Message
            message = QLabel(f"Are you sure you want to delete '{medicine_name}'?\nThis action cannot be undone.")
            message.setFont(QFont("Segoe UI", 11))
            message.setStyleSheet("color: #2c3e50;")
            message.setAlignment(Qt.AlignmentFlag.AlignCenter)
            message.setWordWrap(True)
            layout.addWidget(message)
            
            # Buttons
            btn_layout = QHBoxLayout()
            
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda: self.perform_delete(dialog, med_id))
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            cancel_btn.clicked.connect(dialog.close)
            
            btn_layout.addWidget(delete_btn)
            btn_layout.addWidget(cancel_btn)
            
            layout.addLayout(btn_layout)
            
            dialog.exec()
            
        except Exception as e:
            print(f"Error showing delete confirmation: {e}")
            self.show_error_message(f"Failed to show delete confirmation: {e}")
    
    def perform_delete(self, dialog, med_id):
        """Perform the actual delete operation"""
        try:
            print(f"DEBUG: Performing delete for medicine ID: {med_id}")
            
            # Try to delete via database function first
            try:
                success = delete_medicine(med_id)
            except Exception as db_error:
                print(f"DEBUG: Database function failed, trying direct delete: {db_error}")
                # Fallback to direct database delete
                from database.modern_db import db
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
                success = True
            
            if success:
                print(f"DEBUG: Medicine deleted successfully!")
                
                # Close dialog
                dialog.close()
                
                # Refresh the inventory data
                self.load_inventory_data()
                
                self.show_success_message("Medicine deleted successfully!")
            else:
                self.show_error_message("Failed to delete medicine")
                
        except Exception as e:
            print(f"Error performing delete: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to delete medicine: {e}")
    
    def create_sales_content(self, layout):
        """Create sales management content - CLEAN DESIGN like debug_sales_table.py"""
        # Header section
        title = QLabel("New Sale")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        subtitle = QLabel("Create a new invoice for a customer.")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)
        
        # Main layout: 2 columns
        main_container = QHBoxLayout()
        main_container.setContentsMargins(0, 15, 0, 0)
        main_container.setSpacing(15)
        
        # Left: Create Invoice panel - CLEAN DESIGN
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #d5dbdb;
            }
        """)
        
        # Left panel header
        left_title = QLabel("Create Invoice")
        left_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        left_title.setStyleSheet("color: #2c3e50;")
        left_layout.addWidget(left_title)
        
        # Medicine selection row
        select_frame = QHBoxLayout()
        
        # Medicine dropdown with search functionality
        med_label = QLabel("Medicine:")
        med_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        med_label.setStyleSheet("color: #2c3e50;")
        
        # Create search frame for medicine selection
        medicine_search_frame = QFrame()
        medicine_search_layout = QVBoxLayout(medicine_search_frame)
        medicine_search_layout.setContentsMargins(0, 0, 0, 0)
        medicine_search_layout.setSpacing(2)
        
        # Search input
        self.medicine_search_input = QLineEdit()
        self.medicine_search_input.setPlaceholderText("Search medicines...")
        self.medicine_search_input.setFixedHeight(30)
        self.medicine_search_input.setFont(QFont("Segoe UI", 10))
        self.medicine_search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d5dbdb;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1AAE4A;
            }
        """)
        self.medicine_search_input.textChanged.connect(self.filter_medicines)
        
        # Medicine dropdown
        self.medicine_var = QComboBox()
        self.medicine_var.setFixedHeight(30)  # Reduced height for compact design
        self.medicine_var.setFixedWidth(250)
        self.medicine_var.setFont(QFont("Segoe UI", 10))
        # Set minimum height to ensure dropdown shows more items
        self.medicine_var.setMinimumHeight(30)
        # Set maximum height to control dropdown popup
        self.medicine_var.setMaximumHeight(30)
        
        medicine_search_layout.addWidget(self.medicine_search_input)
        medicine_search_layout.addWidget(self.medicine_var)

        
        # Quantity
        qty_label = QLabel("Qty:")
        qty_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        qty_label.setStyleSheet("color: #2c3e50;")
        
        self.qty_var = QLineEdit("1")
        self.qty_var.setFixedHeight(30)
        self.qty_var.setFixedWidth(80)
        self.qty_var.setFont(QFont("Segoe UI", 9))
        
        # Add to bill button
        add_btn = QPushButton("Add to Bill")
        add_btn.setFixedHeight(30)
        add_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        add_btn.clicked.connect(self.add_to_bill)
        
        # Clear bill button
        clear_btn = QPushButton("Clear Bill")
        clear_btn.setFixedHeight(30)
        clear_btn.setFont(QFont("Segoe UI", 9))
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #BDC3C7;
            }
        """)
        clear_btn.clicked.connect(self.clear_bill)
        
        select_frame.addWidget(med_label)
        select_frame.addWidget(self.medicine_var)
        select_frame.addWidget(qty_label)
        select_frame.addWidget(self.qty_var)
        select_frame.addWidget(add_btn)
        select_frame.addWidget(clear_btn)
        select_frame.addStretch()
        
        left_layout.addLayout(select_frame)
        
        # Bill items table - CLEAN DESIGN like debug_sales_table.py
        self.bill_table_frame = QFrame()
        self.bill_table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #d5dbdb;
            }
        """)
        self.bill_table_frame.setFixedHeight(600)  # Increased height for more content area
        table_layout = QVBoxLayout(self.bill_table_frame)
        
        # Table header - CLEAN DESIGN like debug_sales_table.py
        self.table_header = QFrame()
        self.table_header.setStyleSheet("""
            QFrame {
                background-color: #34495E;  /* Dark blue like debug_sales_table.py */
                min-height: 40px;
            }
        """)
        self.table_header.setFixedHeight(40)
        header_layout = QHBoxLayout(self.table_header)
        header_layout.setContentsMargins(15, 12, 15, 12)  # Proper padding like debug_sales_table.py
        header_layout.setSpacing(5)  # Add 5px spacing between header columns to match data rows
        
        # Header labels - CLEAN DESIGN like debug_sales_table.py
        headers = [
            ("Medicine", 1),   # expand=True
            ("Qty", 0),        # fixed width
            ("Price", 0),      # fixed width  
            ("Total", 0)       # fixed width
        ]
        
        for i, (text, stretch) in enumerate(headers):
            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            lbl.setStyleSheet("""
                color: white;
                background-color: transparent;
                padding: 0px;      /* Remove all padding */
                margin: 0px;       /* Remove all margins */
                border: none;      /* Remove any borders */
                font-size: 12px;
            """)
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft if text == "Medicine" else Qt.AlignmentFlag.AlignRight)
            if stretch:
                header_layout.addWidget(lbl, stretch)
            else:
                lbl.setFixedWidth(80)  # Fixed width for Qty, Price, Total
                header_layout.addWidget(lbl)
        
        table_layout.addWidget(self.table_header)
        
        # Table body - CLEAN DESIGN like debug_sales_table.py
        self.table_body = QFrame()
        self.table_body.setStyleSheet("background-color: white;")
        # FIX: Use Preferred height policy so it only takes needed space
        # Don't set Fixed height - let it grow with content
        self.table_body.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.table_body_layout = QVBoxLayout(self.table_body)
        self.table_body_layout.setContentsMargins(0, 0, 0, 0)
        self.table_body_layout.setSpacing(0)  # Remove spacing between rows
        # Align to TOP so first item starts at top, not centered vertically
        self.table_body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        table_layout.addWidget(self.table_body)
        
        # Initial empty state - CLEAN DESIGN (hidden by default)
        self.empty_label = QLabel("No items in the bill.")
        self.empty_label.setFont(QFont("Segoe UI", 11))
        self.empty_label.setStyleSheet("color: #95A5A6;")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setVisible(False)  # Hide by default to prevent height gap
        self.table_body_layout.addWidget(self.empty_label)
        
        left_layout.addWidget(self.bill_table_frame)
        
        main_container.addWidget(left_panel, 2)
        
        # Right: Bill Summary panel - CLEAN DESIGN
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 10, 10)
        right_layout.setSpacing(10)  # Proper spacing
        right_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #d5dbdb;
            }
        """)
        # Use preferred height policy instead of fixed height to prevent stretching
        right_panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        # Right panel header
        right_title = QLabel("Bill Summary")
        right_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        right_title.setStyleSheet("color: #2c3e50;")
        right_layout.addWidget(right_title)
        
        # Customer selection
        cust_label = QLabel("Customer:")
        cust_label.setFixedHeight(45)
        cust_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        cust_label.setStyleSheet("color: #2c3e50;")
        

        self.customer_var = QComboBox()
        self.customer_var.setFixedHeight(30)
        self.customer_var.setFont(QFont("Segoe UI", 11))
        self.load_customer_options()
        
        right_layout.addWidget(cust_label)
        right_layout.addWidget(self.customer_var)
        
        # Quick Lookup button for ] purchase history
        quick_lookup_btn = QPushButton("🔍 Quick Lookup")
        quick_lookup_btn.setFixedHeight(30)
        quick_lookup_btn.setFont(QFont("Segoe UI", 10))
        quick_lookup_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        quick_lookup_btn.clicked.connect(self.show_customer_lookup)
        right_layout.addWidget(quick_lookup_btn)
        
        # Payment Method selection
        payment_label = QLabel("Payment Method:")
        payment_label.setFixedHeight(45)
        payment_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        payment_label.setStyleSheet("color: #2c3e50;")
        
        self.payment_method_var = QComboBox()
        self.payment_method_var.setFixedHeight(30)
        self.payment_method_var.setFont(QFont("Segoe UI", 11))
        self.payment_method_var.addItems(["Cash", "Card", "Mobile Payment", "Credit"])
        self.payment_method_var.setCurrentText("Cash")  # Default to Cash
        
        right_layout.addWidget(payment_label)
        right_layout.addWidget(self.payment_method_var)
        
       
        
        # Totals section - CLEAN DESIGN
        totals_container = QFrame()
        totals_layout = QVBoxLayout(totals_container)
        totals_container.setStyleSheet("background-color: white;")
        totals_layout.setContentsMargins(0, 0, 0, 0)
        totals_layout.setSpacing(2)  # Small spacing between items
        
        # Subtotal
        subtotal_frame = QFrame()
        subtotal_layout= QHBoxLayout(subtotal_frame)  # Fixed height to prevent stretching
        subtotal_layout.setContentsMargins(0, 0, 0, 0)
        subtotal_layout.setSpacing(10)  # Add spacing for better appearance
        
        subtotal_label = QLabel("Subtotal:")
        subtotal_label.setFont(QFont("Segoe UI", 10))
        subtotal_label.setStyleSheet("color: #2c3e50;")
        
        self.subtotal_label = QLabel("₹0.00")
        self.subtotal_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.subtotal_label.setStyleSheet("color: #27AE60;")
        
        subtotal_layout.addWidget(subtotal_label)
        subtotal_layout.addStretch(1)  # Add stretch to push total to right
        subtotal_layout.addWidget(self.subtotal_label)
        
        totals_layout.addWidget(subtotal_frame)
        
        # Tax
        tax_frame = QFrame()
        tax_layout = QHBoxLayout(tax_frame)
        tax_layout.setContentsMargins(0, 0, 0, 0)
        tax_layout.setSpacing(10)  # Add spacing for better appearance
        
        tax_label = QLabel("Tax (%):")
        tax_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        tax_label.setStyleSheet("color: #2c3e50;")
        
        self.tax_var = QLineEdit("0")
        self.tax_var.setFixedHeight(26)
        self.tax_var.setFixedWidth(100)
        self.tax_var.setFont(QFont("Segoe UI", 10))
        self.tax_var.setPlaceholderText("0%")
        self.tax_var.textChanged.connect(self.update_totals)
        
        # Add tax display label
        self.tax_label = QLabel("₹0.00")
        self.tax_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.tax_label.setStyleSheet("color: #27AE60;")
        
        tax_layout.addWidget(tax_label)
        tax_layout.addStretch(1)  # Add stretch to push input to right
        tax_layout.addWidget(self.tax_var)
        tax_layout.addWidget(self.tax_label)
        
        totals_layout.addWidget(tax_frame)
        
        # Discount
        disc_frame = QFrame()
        disc_layout = QHBoxLayout(disc_frame)
        disc_layout.setContentsMargins(0, 0, 0, 0)
        disc_layout.setSpacing(10)  # Add spacing for better appearance
        
        disc_label = QLabel("Discount (%):")
        disc_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        disc_label.setStyleSheet("color: #2c3e50;")
        
        self.discount_var = QLineEdit("0")
        self.discount_var.setFixedHeight(26)
        self.discount_var.setFixedWidth(100)
        self.discount_var.setFont(QFont("Segoe UI", 10))
        self.discount_var.setPlaceholderText("0%")
        self.discount_var.textChanged.connect(self.update_totals)
        
        disc_layout.addWidget(disc_label)
        disc_layout.addStretch(1)  # Add stretch to push input to right
        disc_layout.addWidget(self.discount_var)
        
        totals_layout.addWidget(disc_frame)
        
          # Invoice Preference checkbox
        invoice_label = QLabel("Invoice Preference:")
        invoice_label.setFixedHeight(45)
        invoice_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        invoice_label.setStyleSheet("color: #2c3e50;")
        
        self.invoice_preference_var = QCheckBox("Generate Invoice")
        self.invoice_preference_var.setFixedHeight(25)
        self.invoice_preference_var.setFont(QFont("Segoe UI", 11))
        self.invoice_preference_var.setChecked(False)  # Default to OFF (no invoice)
        self.invoice_preference_var.setStyleSheet("""
            QCheckBox {
                color: #2c3e50;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        
        right_layout.addWidget(invoice_label)
        right_layout.addWidget(self.invoice_preference_var)
        
        
        # TOTAL LINE (highlighted) - CLEAN DESIGN
        total_line = QFrame()
        total_line_layout = QHBoxLayout(total_line)
        total_line_layout.setContentsMargins(0, 0, 0, 0)
        total_line.setStyleSheet("""
            QFrame {
                background-color: #ECF0F1;
                border: 1px solid #d5dbdb;
                padding: 8px;
            }
        """)
        
        total_text_label = QLabel("Total:")
        total_text_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        total_text_label.setStyleSheet("color: #2c3e50;")
        
        self.total_label = QLabel("₹0.00")
        self.total_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #27AE60;")
        
        total_line_layout.addWidget(total_text_label)
        total_line_layout.addStretch()
        total_line_layout.addWidget(self.total_label)
        
        right_layout.addWidget(totals_container)
        right_layout.addWidget(total_line)
        
        # COMPLETE BUTTON - CLEAN DESIGN
        complete_btn = QPushButton("Complete Sale & Print Invoice")
        complete_btn.setFixedHeight(40)
        complete_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        complete_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        complete_btn.clicked.connect(self.complete_sale)
        
        right_layout.addWidget(complete_btn)
        
        main_container.addWidget(right_panel, 1, alignment=Qt.AlignmentFlag.AlignTop)
        
        layout.addLayout(main_container)
        layout.addStretch()
        
        # Initialize bill items list
        self.bill_items = []
        
        # Load medicines
        self.load_medicines()
    
    def load_medicines(self):
        """Load medicines for sales form"""
        try:
            medicines = get_medicines()
            self.medicine_var.clear()
            self.medicine_var.addItem("Select Medicine")
            
            if medicines:
                for med in medicines:
                    self.medicine_var.addItem(f"{med['name']} - ₹{med['price']:.2f}", med)
                print(f"Loaded {len(medicines)} medicines")
            else:
                print("No medicines found in database")
        except Exception as e:
            print(f"Error loading medicines: {e}")
    
    def add_to_bill(self):
        """Add selected medicine to the bill"""
        try:
            # Get selected medicine
            med_data = self.medicine_var.currentData()
            if not med_data:
                self.show_error_message("Please select a medicine")
                return
            
            # Get quantity
            try:
                qty_text = self.qty_var.text().strip()
                if not qty_text:
                    raise ValueError("Please enter a quantity")
                qty = int(qty_text)
                if qty <= 0:
                    raise ValueError("Quantity must be positive")
            except ValueError as ve:
                self.show_error_message(f"Invalid quantity: {ve}")
                return
            
            # Check stock availability
            if qty > med_data['quantity']:
                self.show_error_message(f"Insufficient stock. Only {med_data['quantity']} units available")
                return
            
            # Calculate totals
            unit_price = med_data['price']
            line_total = qty * unit_price
            
            # Add to bill items list
            self.bill_items.append({
                'medicine': f"{med_data['name']} - ₹{unit_price:.2f}",
                'quantity': qty,
                'price': unit_price,
                'total': line_total
            })
            
            # Update bill table
            self.update_bill_table()
            self.update_totals()
            
            # Clear inputs
            self.qty_var.setText("1")
            self.medicine_var.setCurrentIndex(0)
            
        except Exception as e:
            print(f"Error adding medicine to bill: {e}")
            self.show_error_message(f"Failed to add medicine to bill: {e}")
    
    def update_bill_table(self):
        """Update bill items table - FIXED VERSION"""
        # Clear existing bill items
        for i in reversed(range(self.table_body_layout.count())):
            widget = self.table_body_layout.itemAt(i).widget()
            if widget and widget != self.empty_label:
                widget.deleteLater()
        
        # Show empty state if no items
        if not self.bill_items:
            self.empty_label.setVisible(True)
            return
        
        # Hide empty state
        self.empty_label.setVisible(False)
        
        # Create bill items rows - CLEAN DESIGN like debug_sales_table.py
        for item in self.bill_items:
            # Create row frame - SINGLE ROW LAYOUT like debug_sales_table.py
            row_frame = QFrame()
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(0, 0, 0, 0)  # Remove padding to eliminate box around entire row
            row_layout.setSpacing(5)  # Reduced spacing for compact 25px rows
            row_frame.setFixedHeight(25)  # Set row height to 25px for compact appearance
            row_frame.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Ensure fixed size
            # REMOVE border styling to eliminate boxes around data row values
            row_frame.setStyleSheet("background-color: transparent;")  # No borders
            
            # Medicine name - CLEAN DESIGN like debug_sales_table.py
            med_label = QLabel(item['medicine'])
            med_label.setFont(QFont("Segoe UI", 11))
            med_label.setStyleSheet("""
                color: #2c3e50;
                padding: 0px;      /* Remove all padding */
                margin: 0px;       /* Remove all margins */
                border: none;      /* Remove any borders */
                background-color: transparent;  /* Ensure no background box */
            """)
            med_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            row_layout.addWidget(med_label, 1)
            
            # Quantity - CLEAN DESIGN like debug_sales_table.py
            qty_label = QLabel(str(item['quantity']))
            qty_label.setFont(QFont("Segoe UI", 11))
            qty_label.setStyleSheet("""
                color: #2c3e50;
                padding: 0px;      /* Remove all padding */
                margin: 0px;       /* Remove all margins */
                border: none;      /* Remove any borders */
                background-color: transparent;  /* Ensure no background box */
            """)
            qty_label.setFixedWidth(80)
            row_layout.addWidget(qty_label)
            
            # Price - CLEAN DESIGN like debug_sales_table.py
            price_label = QLabel(f"₹{item['price']:.2f}")
            price_label.setFont(QFont("Segoe UI", 11))
            price_label.setStyleSheet("""
                color: #2c3e50;
                padding: 0px;      /* Remove all padding */
                margin: 0px;       /* Remove all margins */
                border: none;      /* Remove any borders */
                background-color: transparent;  /* Ensure no background box */
            """)
            price_label.setFixedWidth(100)
            row_layout.addWidget(price_label)
            
            # Total - CLEAN DESIGN like debug_sales_table.py
            total_label = QLabel(f"₹{item['total']:.2f}")
            total_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            total_label.setStyleSheet("""
                color: #27AE60;
                padding: 0px;      /* Remove all padding */
                margin: 0px;       /* Remove all margins */
                border: none;      /* Remove any borders */
                background-color: transparent;  /* Ensure no background box */
            """)
            total_label.setFixedWidth(100)
            row_layout.addWidget(total_label)
            
            self.table_body_layout.addWidget(row_frame)
    
    def update_totals(self):
        """Update bill totals"""
        try:
            # Calculate subtotal from bill items
            subtotal = 0.0
            for item in self.bill_items:
                subtotal += item['total']
            
            # Get tax percentage and convert to dollar amount
            try:
                tax_percent = float(self.tax_var.text())
                # Convert percentage to dollar amount
                tax = (tax_percent / 100) * subtotal
            except ValueError:
                tax = 0.0
            
            # Get discount percentage and convert to dollar amount
            try:
                discount_percent = float(self.discount_var.text())
                # Convert percentage to dollar amount
                discount_amount = (discount_percent / 100) * subtotal
            except ValueError:
                discount_amount = 0.0
            
            # Calculate total with percentage discount
            total = subtotal + tax - discount_amount
            
            # Update display
            self.subtotal_label.setText(f"₹{subtotal:.2f}")
            self.tax_label.setText(f"₹{tax:.2f}")
            self.total_label.setText(f"₹{total:.2f}")
            
        except Exception as e:
            print(f"Error updating totals: {e}")
    
    def clear_bill(self):
        """Clear the current bill"""
        self.bill_items = []
        self.update_bill_table()
        self.update_totals()
        self.qty_var.setText("1")
        self.medicine_var.setCurrentIndex(0)
        self.discount_var.setText("0.00")
        self.customer_var.setCurrentIndex(0)
    
    def complete_sale(self):
        """Complete the sale and save to database"""
        try:
            if not self.bill_items:
                self.show_error_message("Please add items to the bill first")
                return
            
            # Get customer ID (now stored as dict with 'id' key)
            customer_data = self.customer_var.currentData()
            customer_id = customer_data['id'] if customer_data and isinstance(customer_data, dict) and 'id' in customer_data else None
            
            # Get payment method (default to Cash)
            payment_method = self.payment_method_var.currentText()
            
            # Get discount percentage and convert to dollar amount
            try:
                discount_percent = float(self.discount_var.text())
                # Calculate discount amount from percentage
                subtotal = sum(item['total'] for item in self.bill_items)
                discount_amount = (discount_percent / 100) * subtotal
            except ValueError:
                discount_amount = 0.0
                discount_percent = 0.0
            
            # Prepare sale items
            items = []
            for item in self.bill_items:
                # Find medicine ID from name
                med_data = None
                for i in range(self.medicine_var.count()):
                    data = self.medicine_var.itemData(i)
                    if data and data['name'] in item['medicine']:
                        med_data = data
                        break
                
                if med_data:
                    items.append({
                        'medicine_id': med_data['id'],
                        'quantity': item['quantity'],
                        'unit_price': item['price']
                    })
            
            # Create sale in database
            sale_id = create_sale(
                customer_id=customer_id,
                items=items,
                discount=discount_amount,  # Pass the calculated dollar amount
                payment_method=payment_method,
                user_id=self.user['id']
            )
            
            if sale_id:
                print(f"Sale completed successfully! Invoice ID: {sale_id}")
                
                # Check if user wants to generate invoice
                generate_invoice = self.invoice_preference_var.isChecked()
                
                if generate_invoice:
                    # Generate invoice PDF
                    from database.pharmacy_settings import get_pharmacy_settings
                    from utils.invoice_generator import generate_invoice_pdf, get_invoice_data, open_pdf
                    
                    pharmacy_settings = get_pharmacy_settings()
                    invoice_data = get_invoice_data(self.bill_items, customer_id, discount_amount)
                    
                    # Handle customer data safely
                    if customer_data:
                        customer_info = {
                            'name': customer_data.get('name', 'Walk-in Customer'),
                            'phone': customer_data.get('phone', 'N/A')
                        }
                    else:
                        customer_info = {
                            'name': 'Walk-in Customer',
                            'phone': 'N/A'
                        }
                    
                    if invoice_data:
                        pdf_path = generate_invoice_pdf(self.bill_items, customer_info, pharmacy_settings, invoice_data)
                        
                        if pdf_path:
                            print(f"Invoice generated: {pdf_path}")
                            # Open PDF automatically
                            open_pdf(pdf_path)
                            self.show_success_message("Sale completed successfully! Invoice generated.")
                        else:
                            self.show_error_message("Sale completed but invoice generation failed")
                            self.show_success_message("Sale completed successfully!")
                    else:
                        self.show_error_message("Sale completed but invoice data generation failed")
                        self.show_success_message("Sale completed successfully!")
                else:
                    # No invoice requested
                    self.show_success_message("Sale completed successfully! (No invoice generated)")
                
                # Clear the bill after successful sale
                self.clear_bill()
            else:
                self.show_error_message("Failed to complete sale")
                
        except Exception as e:
            print(f"Error completing sale: {e}")
            self.show_error_message(f"Failed to complete sale: {e}")
    
    def load_sales_data(self):
        """Load medicines and customers for sales form - FIXED VERSION"""
        try:
            # Load medicines with error handling
            medicines = get_medicines()
            self.med_combo.clear()
            self.med_combo.addItem("Select Medicine", None)
            
            if medicines:
                for med in medicines:
                    self.med_combo.addItem(f"{med['name']} - ₹{med['price']:.2f}", med)
                print(f"Loaded {len(medicines)} medicines")
            else:
                print("No medicines found in database")
            
            # Load customers with real database integration
            self.cust_combo.clear()
            self.cust_combo.addItem("Walk-in Customer", None)
            
            customers = self.get_customers()
            if customers:
                for cust in customers:
                    self.cust_combo.addItem(f"{cust['name']} - {cust['phone']}", cust)
                print(f"Loaded {len(customers)} customers")
            else:
                print("No customers found in database")
            
        except Exception as e:
            print(f"Error loading sales data: {e}")
            import traceback
            traceback.print_exc()
            # Show error message to user
            self.show_error_message(f"Failed to load sales data: {e}")
    
    def update_medicine_price(self):
        """Update price display when medicine selection changes"""
        # This will be enhanced when we have real medicine data
        pass
    
    def add_medicine_to_bill(self):
        """Add selected medicine to the bill - FIXED VERSION like debug_sales_table.py"""
        print("DEBUG: add_medicine_to_bill called")
        try:
            # Get selected medicine
            med_data = self.med_combo.currentData()
            print(f"DEBUG: Selected medicine data: {med_data}")
            if not med_data:
                print("DEBUG: No medicine selected")
                self.show_error_message("Please select a medicine")
                return
            
            # Get quantity
            try:
                qty_text = self.qty_input.text().strip()
                if not qty_text:
                    raise ValueError("Please enter a quantity")
                qty = int(qty_text)
                print(f"DEBUG: Quantity entered: {qty}")
                if qty <= 0:
                    raise ValueError("Quantity must be positive")
            except ValueError as ve:
                print(f"DEBUG: Quantity error: {ve}")
                self.show_error_message(f"Invalid quantity: {ve}")
                return
            
            # Check stock availability
            if qty > med_data['quantity']:
                print(f"DEBUG: Insufficient stock. Available: {med_data['quantity']}")
                self.show_error_message(f"Insufficient stock. Only {med_data['quantity']} units available")
                return
            
            # Calculate totals
            unit_price = med_data['price']
            line_total = qty * unit_price
            print(f"DEBUG: Unit price: {unit_price}, Line total: {line_total}")
            
            # Extract medicine name from combo box format (like debug_sales_table.py)
            # The combo box displays "Medicine Name - ₹Price" but we need just the name
            medicine_name = med_data['name']  # This should be just the name from the database
            medicine_display = f"{medicine_name} - ₹{unit_price:.2f}"
            
            # Add to bill items list (like debug_sales_table.py)
            self.bill_items.append({
                'medicine': medicine_display,
                'quantity': qty,
                'price': unit_price,
                'total': line_total
            })
            
            print(f"DEBUG: Bill items: {self.bill_items}")
            
            # Update bill table (like debug_sales_table.py)
            self.update_bill_table()
            self.update_bill_totals()
            
            # Clear inputs
            self.qty_input.clear()
            self.med_combo.setCurrentIndex(0)
            
            print("DEBUG: Medicine successfully added to bill")
            
        except Exception as e:
            print(f"Error adding medicine to bill: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to add medicine to bill: {e}")
    
    def update_bill_table(self):
        """Update bill items table - FIXED VERSION"""
        # Clear existing bill items
        for i in reversed(range(self.table_body_layout.count())):
            widget = self.table_body_layout.itemAt(i).widget()
            if widget and widget != self.empty_label:
                widget.deleteLater()
        
        # Show empty state if no items
        if not self.bill_items:
            self.empty_label.setVisible(True)
            return
        
        # Hide empty state
        self.empty_label.setVisible(False)
        
        # Create bill items rows - CLEAN DESIGN like debug_sales_table.py
        for item in self.bill_items:
            # Create row frame - SINGLE ROW LAYOUT like debug_sales_table.py
            row_frame = QFrame()
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(15, 8, 15, 8)
            row_layout.setSpacing(15)
            # REMOVE border styling to eliminate boxes around data row values
            row_frame.setStyleSheet("background-color: transparent;")  # No borders
            
            # Medicine name - CLEAN DESIGN like debug_sales_table.py
            med_label = QLabel(item['medicine'])
            med_label.setFont(QFont("Segoe UI", 11))
            med_label.setStyleSheet("""
                color: #2c3e50;
                padding: 0px;      /* Remove all padding */
                margin: 0px;       /* Remove all margins */
                border: none;      /* Remove any borders */
                background-color: transparent;  /* Ensure no background box */
            """)
            med_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            row_layout.addWidget(med_label, 1)
            
            # Quantity - CLEAN DESIGN like debug_sales_table.py
            qty_label = QLabel(str(item['quantity']))
            qty_label.setFont(QFont("Segoe UI", 11))
            qty_label.setStyleSheet("""
                color: #2c3e50;
                padding: 0px;      /* Remove all padding */
                margin: 0px;       /* Remove all margins */
                border: none;      /* Remove any borders */
                background-color: transparent;  /* Ensure no background box */
            """)
            qty_label.setFixedWidth(80)
            row_layout.addWidget(qty_label)
            
            # Price - CLEAN DESIGN like debug_sales_table.py
            price_label = QLabel(f"₹{item['price']:.2f}")
            price_label.setFont(QFont("Segoe UI", 11))
            price_label.setStyleSheet("""
                color: #2c3e50;
                padding: 0px;      /* Remove all padding */
                margin: 0px;       /* Remove all margins */
                border: none;      /* Remove any borders */
                background-color: transparent;  /* Ensure no background box */
            """)
            price_label.setFixedWidth(100)
            row_layout.addWidget(price_label)
            
            # Total - CLEAN DESIGN like debug_sales_table.py
            total_label = QLabel(f"₹{item['total']:.2f}")
            total_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            total_label.setStyleSheet("""
                color: #27AE60;
                padding: 0px;      /* Remove all padding */
                margin: 0px;       /* Remove all margins */
                border: none;      /* Remove any borders */
                background-color: transparent;  /* Ensure no background box */
            """)
            total_label.setFixedWidth(100)
            row_layout.addWidget(total_label)
            
            self.table_body_layout.addWidget(row_frame)
    
    def update_bill_totals(self):
        """Update bill totals based on items and discount - FIXED VERSION"""
        try:
            # Calculate subtotal from bill items
            subtotal = 0.0
            for item in self.bill_items:
                subtotal += item['total']
            
            # Calculate tax (5%)
            tax = subtotal * 0.05
            
            # Get discount
            try:
                discount = float(self.discount_input.text())
            except ValueError:
                discount = 0.0
            
            # Calculate total
            total = subtotal + tax - discount
            
            # Update display
            self.subtotal_value.setText(f"₹{subtotal:.2f}")
            self.tax_value.setText(f"₹{tax:.2f}")
            self.total_value.setText(f"₹{total:.2f}")
            
            # Enable complete button if there are items
            self.complete_btn.setEnabled(len(self.bill_items) > 0)
            
        except Exception as e:
            print(f"Error updating bill totals: {e}")
    
    def clear_bill(self):
        """Clear the current bill"""
        # Clear bill items list
        self.bill_items = []
        self.update_bill_table()
        self.update_totals()
        self.qty_var.setText("1")
        self.medicine_var.setCurrentIndex(0)
        self.discount_var.setText("0.00")
        self.customer_var.setCurrentIndex(0)
    
    def process_sale(self):
        """Process the complete sale and save to database"""
        try:
            if self.bill_table.rowCount() == 0:
                return
            
            # Get customer ID - handle both dict (from real DB) and integer (from fallback)
            customer_data = self.customer_var.currentData()
            if customer_data is None:
                customer_id = None  # Walk-in customer
            elif isinstance(customer_data, dict):
                customer_id = customer_data.get('id')  # Real customer from database
            else:
                customer_id = customer_data  # Integer fallback ID (1, 2, 3)
            
            # Get payment method
            payment_method = self.payment_combo.currentText()
            
            # Get discount
            try:
                discount = float(self.discount_input.text())
            except ValueError:
                discount = 0.0
            
            # Prepare sale items
            items = []
            for row in range(self.bill_table.rowCount()):
                # Get table items safely
                med_name_item = self.bill_table.item(row, 0)
                qty_item = self.bill_table.item(row, 1)
                price_item = self.bill_table.item(row, 2)
                
                if not med_name_item or not qty_item or not price_item:
                    continue
                
                med_name = med_name_item.text()
                qty = int(qty_item.text())
                price = float(price_item.text().replace('₹', ''))
                
                # Find medicine ID from name
                med_data = None
                for i in range(self.med_combo.count()):
                    data = self.med_combo.itemData(i)
                    if data and data['name'] == med_name:
                        med_data = data
                        break
                
                if med_data:
                    items.append({
                        'medicine_id': med_data['id'],
                        'quantity': qty,
                        'unit_price': price
                    })
            
            # Create sale in database
            sale_id = create_sale(
                customer_id=customer_id,
                items=items,
                discount=discount,
                payment_method=payment_method,
                user_id=self.user['id']
            )
            
            if sale_id:
                print(f"Sale completed successfully! Invoice ID: {sale_id}")
                # Clear the bill after successful sale
                self.clear_bill()
                # Refresh inventory data
                self.load_inventory_data()
            else:
                print("Failed to complete sale")
                
        except Exception as e:
            print(f"Error processing sale: {e}")
    
    def create_customers_content(self, layout):
        """Create customers management content - FIXED VERSION"""
        title = QLabel("Customer Management")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        subtitle = QLabel("View and manage customer details")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search customers...")
        search_input.setFixedHeight(40)
        search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d5dbdb;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1AAE4A;
            }
        """)
        search_input.textChanged.connect(self.search_customers)
        
        add_btn = QPushButton("➕ Add Customer")
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #1AAE4A;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #168f3c;
            }
        """)
        add_btn.clicked.connect(self.add_customer)
        
        controls_layout.addWidget(search_input)
        controls_layout.addWidget(add_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # CRITICAL FIX: Add QScrollArea container for customers table (like inventory)
        customers_scroll_area = QScrollArea()
        customers_scroll_area.setWidgetResizable(True)
        customers_scroll_area.setMinimumHeight(600)
        customers_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
                min-height: 600px;
            }
            QScrollBar:vertical {
                width: 14px;
                background: #ecf0f1;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 7px;
                min-height: 50px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Customers table - Set up columns first with improved height
        self.customers_table = QTableWidget()
        # include address column
        self.customers_table.setHorizontalHeaderLabels(["Name", "Email", "Phone", "Address", "Total Spent", "Actions"])
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.customers_table.verticalHeader().setVisible(False)
        self.customers_table.setAlternatingRowColors(True)
        self.customers_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
                border-radius: 8px;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #e8e8e8;
                color: #333333;
                background-color: white;
                font-size: 12px;
                font-family: 'Segoe UI';
                font-weight: bold;
                min-height: 40px;  /* Increased row height */
            }
            QTableWidget::item:selected {
                background-color: #e3f2e9;
                color: #1AAE4A;
                border-left: 3px solid #1AAE4A;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #ffffff;
                color: #555555;
                font-weight: 600;
                border: none;
                border-bottom: 2px solid #1AAE4A;
                padding: 12px;
                font-size: 12px;
                font-family: 'Segoe UI';
                min-height: 45px;  /* Increased header height */
            }
            QTableWidget QTableCornerButton::section {
                background-color: #ffffff;
                border: none;
            }
        """)
        self.customers_table.setSortingEnabled(True)
        # Set minimum row height for better visibility
        self.customers_table.verticalHeader().setMinimumSectionSize(50)
        
        # Increase fixed height for more visible rows
        self.customers_table.setFixedHeight(700)  # Increased for more visible rows
        self.customers_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Add scrollbar styling to match inventory table
        self.customers_table.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                width: 14px;
                background: #ecf0f1;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 7px;
                min-height: 50px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Set the table as the widget for the scroll area
        customers_scroll_area.setWidget(self.customers_table)
        
        layout.addWidget(customers_scroll_area)
        layout.addStretch()

        # Load initial data immediately after table creation
        self.load_customers_data()
    
    def search_customers(self, text):
        """Search customers"""
        try:
            customers = get_customers(search=text)
            self.populate_customers_table(customers)
        except Exception as e:
            print(f"Error searching customers: {e}")
    
    def load_customers_data(self):
        """Load all customers from database - FIXED VERSION"""
        try:
            customers = self.get_customers()
            if customers:
                # CRITICAL FIX: Ensure table has columns set up before populating
                if self.customers_table.columnCount() == 0:
                    headers = ["Name", "Email", "Phone", "Address", "Total Spent", "Actions"]
                    self.customers_table.setColumnCount(len(headers))
                    self.customers_table.setHorizontalHeaderLabels(headers)
                
                self.populate_customers_table(customers)
            else:
                print("No customers found in database")
                self.show_error_message("No customers found in database.")
        except Exception as e:
            print(f"Error loading customers: {e}")
            # Show error message to user
            self.show_error_message("Failed to load customers data")
    
    def populate_customers_table(self, customers):
        """Populate customers table with customer data - FIXED VERSION"""
        # CRITICAL Fix: Clear existing data first
        self.customers_table.setRowCount(0)
        self.customers_table.setRowCount(len(customers))
        
        for row, cust in enumerate(customers):
            # Name
            name_item = QTableWidgetItem(cust['name'])
            name_item.setFont(QFont("Segoe UI", 10))
            self.customers_table.setItem(row, 0, name_item)
            
            # Email
            email_item = QTableWidgetItem(cust['email'])
            email_item.setFont(QFont("Segoe UI", 10))
            self.customers_table.setItem(row, 1, email_item)
            
            # Phone
            phone_item = QTableWidgetItem(cust['phone'])
            phone_item.setFont(QFont("Segoe UI", 10))
            self.customers_table.setItem(row, 2, phone_item)
            
            # Address
            address_item = QTableWidgetItem(cust.get('address', ''))
            address_item.setFont(QFont("Segoe UI", 10))
            self.customers_table.setItem(row, 3, address_item)
            
            # Total Spent
            total_spent_item = QTableWidgetItem(f"₹{cust['total_spent']:.2f}")
            total_spent_item.setFont(QFont("Segoe UI", 10))
            self.customers_table.setItem(row, 4, total_spent_item)
            
            # Actions
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedHeight(25)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 0px 8px 9px 8px;
                    font-size: 10px;
                    font-weight: bold;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            edit_btn.clicked.connect(lambda checked, cust_id=cust['id']: self.edit_customer(cust_id))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setFixedHeight(25)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 0px 8px 9px 8px;
                    font-size: 10px;
                    font-weight: bold;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, cust_id=cust['id']: self.delete_customer(cust_id))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            # actions now in column 5 after adding Address
            self.customers_table.setCellWidget(row, 5, actions_widget)
        
        # CRITICAL FIX: Ensure table is visible
        if not self.customers_table.isVisible():
            self.customers_table.setVisible(True)
    
    def add_customer(self):
        """Add new customer"""
        print("Add customer clicked")
        # Create a simple add customer dialog
        self.show_add_customer_dialog()
    
    def show_add_customer_dialog(self):
        """Show add customer dialog"""
        try:
            print("DEBUG: Creating Add Customer dialog...")
            
            # Create dialog window
            dialog = QDialog(self)
            dialog.setWindowTitle("Add Customer")
            dialog.setGeometry(100, 100, 450, 350)
            dialog.setStyleSheet("background-color: white;")
            dialog.setModal(True)  # Make it modal
            
            layout = QVBoxLayout(dialog)
            
            # Title
            title = QLabel("Add New Customer")
            title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            title.setStyleSheet("color: #2c3e50;")
            layout.addWidget(title)
            
            # Form fields
            form_layout = QGridLayout()
            
            # Name
            name_label = QLabel("Customer Name:")
            name_label.setFont(QFont("Segoe UI", 10))
            name_label.setStyleSheet("color: #2c3e50;")
            name_input = QLineEdit()
            name_input.setPlaceholderText("Enter customer name")
            name_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(name_label, 0, 0)
            form_layout.addWidget(name_input, 0, 1)
            
            # Email
            email_label = QLabel("Email:")
            email_label.setFont(QFont("Segoe UI", 10))
            email_label.setStyleSheet("color: #2c3e50;")
            email_input = QLineEdit()
            email_input.setPlaceholderText("Enter customer email")
            email_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(email_label, 1, 0)
            form_layout.addWidget(email_input, 1, 1)
            
            # Phone
            phone_label = QLabel("Phone:")
            phone_label.setFont(QFont("Segoe UI", 10))
            phone_label.setStyleSheet("color: #2c3e50;")
            phone_input = QLineEdit()
            phone_input.setPlaceholderText("Enter customer phone")
            phone_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(phone_label, 2, 0)
            form_layout.addWidget(phone_input, 2, 1)
            
            # Address
            address_label = QLabel("Address:")
            address_label.setFont(QFont("Segoe UI", 10))
            address_label.setStyleSheet("color: #2c3e50;")
            address_input = QLineEdit()
            address_input.setPlaceholderText("Enter customer address")
            address_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(address_label, 3, 0)
            form_layout.addWidget(address_input, 3, 1)
            
            layout.addLayout(form_layout)
            
            # Buttons
            btn_layout = QHBoxLayout()
            
            save_btn = QPushButton("Save Customer")
            save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1AAE4A;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #168f3c;
                }
            """)
            
            # Add debug to save button
            def debug_save():
                print("DEBUG: Save Customer button clicked!")
                try:
                    self.save_new_customer(dialog, name_input, email_input, phone_input, address_input)
                except Exception as e:
                    print(f"DEBUG: Error in save_new_customer: {e}")
                    import traceback
                    traceback.print_exc()
            
            save_btn.clicked.connect(debug_save)
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            cancel_btn.clicked.connect(dialog.close)
            
            btn_layout.addWidget(save_btn)
            btn_layout.addWidget(cancel_btn)
            
            layout.addLayout(btn_layout)
            
            print("DEBUG: Dialog created successfully, showing...")
            dialog.exec()  # Use exec() for modal dialog
            print("DEBUG: Dialog closed")
            
        except Exception as e:
            print(f"DEBUG: Error creating dialog: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to open Add Customer dialog: {e}")
    
    def save_new_customer(self, dialog, name_input, email_input, phone_input, address_input):
        """Save new customer to database"""
        try:
            print("DEBUG: save_new_customer called")
            
            name = name_input.text().strip()
            email = email_input.text().strip()
            phone = phone_input.text().strip()
            address = address_input.text().strip()
            
            print(f"DEBUG: Customer data - Name: {name}, Email: {email}, Phone: {phone}, Address: {address}")
            
            if not name or not email or not phone:
                print("DEBUG: Validation failed")
                self.show_error_message("Please enter all required customer details")
                return
            
            # Save to database
            customer_id = self.create_customer(
                name=name,
                email=email,
                phone=phone,
                address=address
            )
            
            if customer_id:
                print(f"DEBUG: Customer saved to database with ID: {customer_id}")
                
                # Close dialog first
                dialog.close()
                
                print("DEBUG: Dialog closed")
                
                # Refresh the customers data to show the new customer
                self.load_customers_data()
                
                self.show_success_message("Customer added successfully!")
                
                print("DEBUG: Success message shown")
            else:
                print("DEBUG: Failed to save customer to database")
                self.show_error_message("Failed to save customer to database")
            
        except Exception as e:
            print(f"DEBUG: Exception in save_new_customer: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to add customer: {e}")
    
    def edit_customer(self, cust_id):
        """Edit customer - Open edit dialog with customer data"""
        print(f"Edit customer {cust_id} clicked")
        try:
            # Fetch customer data from database
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, email, phone, address
                    FROM customers
                    WHERE id = ?
                """, (cust_id,))
                result = cursor.fetchone()
                
                if result:
                    customer_data = {
                        'id': result[0],
                        'name': result[1],
                        'email': result[2],
                        'phone': result[3],
                        'address': result[4]
                    }
                    self.show_edit_customer_dialog(customer_data)
                else:
                    self.show_error_message(f"Customer with ID {cust_id} not found")
        except Exception as e:
            print(f"Error fetching customer data: {e}")
            self.show_error_message(f"Failed to load customer data: {e}")
    
    def show_edit_customer_dialog(self, customer_data):
        """Show edit customer dialog with pre-filled data"""
        try:
            print(f"DEBUG: Creating Edit Customer dialog for: {customer_data['name']}")
            
            # Create dialog window
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Customer")
            dialog.setGeometry(100, 100, 450, 350)
            dialog.setStyleSheet("background-color: white;")
            dialog.setModal(True)
            
            layout = QVBoxLayout(dialog)
            
            # Title
            title = QLabel("Edit Customer Details")
            title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            title.setStyleSheet("color: #2c3e50;")
            layout.addWidget(title)
            
            # Customer ID (stored for later use)
            cust_id = customer_data['id']
            
            # Form fields
            form_layout = QGridLayout()
            
            # Name
            name_label = QLabel("Customer Name:")
            name_label.setFont(QFont("Segoe UI", 10))
            name_label.setStyleSheet("color: #2c3e50;")
            name_input = QLineEdit()
            name_input.setText(customer_data.get('name', ''))
            name_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(name_label, 0, 0)
            form_layout.addWidget(name_input, 0, 1)
            
            # Email
            email_label = QLabel("Email:")
            email_label.setFont(QFont("Segoe UI", 10))
            email_label.setStyleSheet("color: #2c3e50;")
            email_input = QLineEdit()
            email_input.setText(customer_data.get('email', ''))
            email_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(email_label, 1, 0)
            form_layout.addWidget(email_input, 1, 1)
            
            # Phone
            phone_label = QLabel("Phone:")
            phone_label.setFont(QFont("Segoe UI", 10))
            phone_label.setStyleSheet("color: #2c3e50;")
            phone_input = QLineEdit()
            phone_input.setText(customer_data.get('phone', ''))
            phone_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(phone_label, 2, 0)
            form_layout.addWidget(phone_input, 2, 1)
            
            # Address
            address_label = QLabel("Address:")
            address_label.setFont(QFont("Segoe UI", 10))
            address_label.setStyleSheet("color: #2c3e50;")
            address_input = QLineEdit()
            address_input.setText(customer_data.get('address', ''))
            address_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(address_label, 3, 0)
            form_layout.addWidget(address_input, 3, 1)
            
            layout.addLayout(form_layout)
            
            # Buttons
            btn_layout = QHBoxLayout()
            
            update_btn = QPushButton("Update Customer")
            update_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            
            # Add debug to update button
            def debug_update():
                print("DEBUG: Update Customer button clicked!")
                try:
                    self.update_customer_record(dialog, cust_id, name_input, email_input, phone_input, address_input)
                except Exception as e:
                    print(f"DEBUG: Error in update_customer_record: {e}")
                    import traceback
                    traceback.print_exc()
            
            update_btn.clicked.connect(debug_update)
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            cancel_btn.clicked.connect(dialog.close)
            
            btn_layout.addWidget(update_btn)
            btn_layout.addWidget(cancel_btn)
            
            layout.addLayout(btn_layout)
            
            print("DEBUG: Customer edit dialog created successfully, showing...")
            dialog.exec()
            print("DEBUG: Dialog closed")
            
        except Exception as e:
            print(f"DEBUG: Error creating edit dialog: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to open Edit Customer dialog: {e}")
    
    def update_customer_record(self, dialog, cust_id, name_input, email_input, phone_input, address_input):
        """Update customer record in database"""
        try:
            print(f"DEBUG: update_customer_record called for customer ID: {cust_id}")
            
            name = name_input.text().strip()
            email = email_input.text().strip()
            phone = phone_input.text().strip()
            address = address_input.text().strip()
            
            print(f"DEBUG: Updated customer data - Name: {name}, Email: {email}, Phone: {phone}, Address: {address}")
            
            if not name or not email or not phone:
                print("DEBUG: Validation failed")
                self.show_error_message("Please enter all required customer details")
                return
            
            # Update in database
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE customers 
                    SET name = ?, email = ?, phone = ?, address = ?
                    WHERE id = ?
                """, (name, email, phone, address, cust_id))
                conn.commit()
            
            print(f"DEBUG: Customer updated successfully!")
            
            # Close dialog first
            dialog.close()
            
            print("DEBUG: Dialog closed")
            
            # Refresh the customers data to show the updated customer
            self.load_customers_data()
            
            self.show_success_message("Customer updated successfully!")
            
            print("DEBUG: Success message shown")
            
        except Exception as e:
            print(f"DEBUG: Exception in update_customer_record: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to update customer: {e}")
    
    def delete_customer(self, cust_id):
        """Delete customer (placeholder for now)"""
        print(f"Delete customer {cust_id} clicked")
        # TODO: Implement delete confirmation and database update
    
    def get_customers(self, search=""):
        """Get customers with optional filtering"""
        try:
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, name, email, phone, address, total_spent
                    FROM customers
                    WHERE 1=1
                """
                params = []
                
                if search:
                    query += " AND (name LIKE ? OR email LIKE ? OR phone LIKE ?)"
                    search_like = f"%{search}%"
                    params.extend([search_like, search_like, search_like])
                
                query += " ORDER BY name"
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                customers = []
                for row in results:
                    customers.append({
                        'id': row[0],
                        'name': row[1],
                        'email': row[2],
                        'phone': row[3],
                        'address': row[4] if row[4] else "",
                        'total_spent': row[5] if row[5] else 0
                    })
                
                return customers
        except Exception as e:
            print(f"Error getting customers: {e}")
            return []
    
    def create_customer(self, name, email, phone, address=""):
        """Create a new customer record"""
        try:
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO customers (name, email, phone, address)
                    VALUES (?, ?, ?, ?)
                """, (name, email, phone, address))
                conn.commit()  # Explicitly commit the transaction
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating customer: {e}")
            return None
    
    def create_suppliers_content(self, layout):
        """Create suppliers management content - FIXED VERSION"""
        title = QLabel("Supplier Management")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        subtitle = QLabel("Keep track of your medicine suppliers")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search suppliers...")
        search_input.setFixedHeight(40)
        search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d5dbdb;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1AAE4A;
            }
        """)
        search_input.textChanged.connect(self.search_suppliers)
        
        add_btn = QPushButton("➕ Add Supplier")
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #1AAE4A;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #168f3c;
            }
        """)
        add_btn.clicked.connect(self.add_supplier)
        
        controls_layout.addWidget(search_input)
        controls_layout.addWidget(add_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # CRITICAL FIX: Add QScrollArea container for suppliers table (like inventory)
        suppliers_scroll_area = QScrollArea()
        suppliers_scroll_area.setWidgetResizable(True)
        suppliers_scroll_area.setMinimumHeight(600)
        suppliers_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
                min-height: 600px;
            }
            QScrollBar:vertical {
                width: 14px;
                background: #ecf0f1;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 7px;
                min-height: 50px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Suppliers table - Set up columns first with improved height
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setHorizontalHeaderLabels(["Supplier Name", "Contact Person", "Email", "Phone", "Actions"])
        self.suppliers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.suppliers_table.verticalHeader().setVisible(False)
        self.suppliers_table.setAlternatingRowColors(True)
        self.suppliers_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
                border-radius: 8px;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #e8e8e8;
                color: #333333;
                background-color: white;
                font-size: 12px;
                font-family: 'Segoe UI';
                font-weight: bold;
                min-height: 40px;  /* Increased row height */
            }
            QTableWidget::item:selected {
                background-color: #e3f2e9;
                color: #1AAE4A;
                border-left: 3px solid #1AAE4A;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #ffffff;
                color: #555555;
                font-weight: 600;
                border: none;
                border-bottom: 2px solid #1AAE4A;
                padding: 12px;
                font-size: 12px;
                font-family: 'Segoe UI';
                min-height: 45px;  /* Increased header height */
            }
            QTableWidget QTableCornerButton::section {
                background-color: #ffffff;
                border: none;
            }
        """)
        self.suppliers_table.setSortingEnabled(True)
        # Set minimum row height for better visibility
        self.suppliers_table.verticalHeader().setMinimumSectionSize(50)
        
        # CRITICAL FIX: Set fixed height for internal table scrolling
        self.suppliers_table.setFixedHeight(700)  # Increased for more visible rows
        self.suppliers_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Add scrollbar styling to match inventory table
        self.suppliers_table.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                width: 14px;
                background: #ecf0f1;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 7px;
                min-height: 50px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Set the table as the widget for the scroll area
        suppliers_scroll_area.setWidget(self.suppliers_table)
        
        layout.addWidget(suppliers_scroll_area)
        layout.addStretch()

        # Load initial data immediately after table creation
        self.load_suppliers_data()
    
    def search_suppliers(self, text):
        """Search suppliers by name"""
        try:
            suppliers = get_suppliers(search=text)
            self.populate_suppliers_table(suppliers)
        except Exception as e:
            print(f"Error searching suppliers: {e}")
    
    def load_suppliers_data(self):
        """Load all suppliers from database - FIXED VERSION"""
        try:
            suppliers = self.get_suppliers()
            if suppliers:
                # CRITICAL FIX: Ensure table has columns set up before populating
                if self.suppliers_table.columnCount() == 0:
                    headers = ["Supplier Name", "Contact Person", "Email", "Phone", "Actions"]
                    self.suppliers_table.setColumnCount(len(headers))
                    self.suppliers_table.setHorizontalHeaderLabels(headers)
                
                self.populate_suppliers_table(suppliers)
            else:
                self.show_error_message("No suppliers found in database.")
        except Exception as e:
            print(f"Error loading suppliers: {e}")
            # Show error message to user
            self.show_error_message("Failed to load suppliers data")
    
    def populate_suppliers_table(self, suppliers):
        """Populate suppliers table with supplier data - FIXED VERSION"""
        # CRITICAL FIX: Clear existing data first
        self.suppliers_table.setRowCount(0)
        self.suppliers_table.setRowCount(len(suppliers))
        
        for row, sup in enumerate(suppliers):
            # Supplier Name
            name_item = QTableWidgetItem(sup['name'])
            name_item.setFont(QFont("Segoe UI", 10))
            self.suppliers_table.setItem(row, 0, name_item)
            
            # Contact Person
            contact_item = QTableWidgetItem(sup['contact_person'])
            contact_item.setFont(QFont("Segoe UI", 10))
            self.suppliers_table.setItem(row, 1, contact_item)
            
            # Email
            email_item = QTableWidgetItem(sup['email'])
            email_item.setFont(QFont("Segoe UI", 10))
            self.suppliers_table.setItem(row, 2, email_item)
            
            # Phone
            phone_item = QTableWidgetItem(sup['phone'])
            phone_item.setFont(QFont("Segoe UI", 10))
            self.suppliers_table.setItem(row, 3, phone_item)
            
            # Actions
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedHeight(25)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 0px 8px 9px 8px;
                    font-size: 10px;
                    font-weight: bold;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            edit_btn.clicked.connect(lambda checked, sup_id=sup['id']: self.edit_supplier(sup_id))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setFixedHeight(25)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 0px 8px 9px 8px;
                    font-size: 10px;
                    font-weight: bold;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, sup_id=sup['id']: self.delete_supplier(sup_id))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.suppliers_table.setCellWidget(row, 4, actions_widget)
        
        # CRITICAL FIX: Ensure table is visible
        if not self.suppliers_table.isVisible():
            self.suppliers_table.setVisible(True)
    
    def add_supplier(self):
        """Add new supplier"""
        print("Add supplier clicked")
        # Create a simple add supplier dialog
        self.show_add_supplier_dialog()
    
    def show_add_supplier_dialog(self):
        """Show add supplier dialog"""
        try:
            print("DEBUG: Creating Add Supplier dialog...")
            
            # Create dialog window
            dialog = QDialog(self)
            dialog.setWindowTitle("Add Supplier")
            dialog.setGeometry(100, 100, 450, 300)
            dialog.setStyleSheet("background-color: white;")
            dialog.setModal(True)  # Make it modal
            
            layout = QVBoxLayout(dialog)
            
            # Title
            title = QLabel("Add New Supplier")
            title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            title.setStyleSheet("color: #2c3e50;")
            layout.addWidget(title)
            
            # Form fields
            form_layout = QGridLayout()
            
            # Supplier Name
            name_label = QLabel("Supplier Name:")
            name_label.setFont(QFont("Segoe UI", 10))
            name_label.setStyleSheet("color: #2c3e50;")
            name_input = QLineEdit()
            name_input.setPlaceholderText("Enter supplier name")
            name_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(name_label, 0, 0)
            form_layout.addWidget(name_input, 0, 1)
            
            # Contact Person
            contact_label = QLabel("Contact Person:")
            contact_label.setFont(QFont("Segoe UI", 10))
            contact_label.setStyleSheet("color: #2c3e50;")
            contact_input = QLineEdit()
            contact_input.setPlaceholderText("Enter contact person name")
            contact_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(contact_label, 1, 0)
            form_layout.addWidget(contact_input, 1, 1)
            
            # Email
            email_label = QLabel("Email:")
            email_label.setFont(QFont("Segoe UI", 10))
            email_label.setStyleSheet("color: #2c3e50;")
            email_input = QLineEdit()
            email_input.setPlaceholderText("Enter supplier email")
            email_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(email_label, 2, 0)
            form_layout.addWidget(email_input, 2, 1)
            
            # Phone
            phone_label = QLabel("Phone:")
            phone_label.setFont(QFont("Segoe UI", 10))
            phone_label.setStyleSheet("color: #2c3e50;")
            phone_input = QLineEdit()
            phone_input.setPlaceholderText("Enter supplier phone")
            phone_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(phone_label, 3, 0)
            form_layout.addWidget(phone_input, 3, 1)
            
            layout.addLayout(form_layout)
            
            # Buttons
            btn_layout = QHBoxLayout()
            
            save_btn = QPushButton("Save Supplier")
            save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1AAE4A;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #168f3c;
                }
            """)
            
            # Add debug to save button
            def debug_save():
                print("DEBUG: Save Supplier button clicked!")
                try:
                    self.save_new_supplier(dialog, name_input, contact_input, email_input, phone_input)
                except Exception as e:
                    print(f"DEBUG: Error in save_new_supplier: {e}")
                    import traceback
                    traceback.print_exc()
            
            save_btn.clicked.connect(debug_save)
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            cancel_btn.clicked.connect(dialog.close)
            
            btn_layout.addWidget(save_btn)
            btn_layout.addWidget(cancel_btn)
            
            layout.addLayout(btn_layout)
            
            print("DEBUG: Dialog created successfully, showing...")
            dialog.exec()  # Use exec() for modal dialog
            print("DEBUG: Dialog closed")
            
        except Exception as e:
            print(f"DEBUG: Error creating dialog: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to open Add Supplier dialog: {e}")
    
    def save_new_supplier(self, dialog, name_input, contact_input, email_input, phone_input):
        """Save new supplier to database"""
        try:
            print("DEBUG: save_new_supplier called")
            
            name = name_input.text().strip()
            contact_person = contact_input.text().strip()
            email = email_input.text().strip()
            phone = phone_input.text().strip()
            
            print(f"DEBUG: Supplier data - Name: {name}, Contact: {contact_person}, Email: {email}, Phone: {phone}")
            
            if not name or not contact_person or not email or not phone:
                print("DEBUG: Validation failed")
                self.show_error_message("Please enter all supplier details")
                return
            
            # Save to database
            supplier_id = self.create_supplier(
                name=name,
                contact_person=contact_person,
                email=email,
                phone=phone
            )
            
            if supplier_id:
                print(f"DEBUG: Supplier saved to database with ID: {supplier_id}")
                
                # Close dialog first
                dialog.close()
                
                print("DEBUG: Dialog closed")
                
                # Refresh the suppliers data to show the new supplier
                self.load_suppliers_data()
                
                self.show_success_message("Supplier added successfully!")
                
                print("DEBUG: Success message shown")
            else:
                print("DEBUG: Failed to save supplier to database")
                self.show_error_message("Failed to save supplier to database")
            
        except Exception as e:
            print(f"DEBUG: Exception in save_new_supplier: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to add supplier: {e}")
    
    def edit_supplier(self, sup_id):
        """Edit supplier - Open edit dialog with supplier data"""
        print(f"Edit supplier {sup_id} clicked")
        try:
            # Fetch supplier data from database
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, contact_person, email, phone
                    FROM suppliers
                    WHERE id = ?
                """, (sup_id,))
                result = cursor.fetchone()
                
                if result:
                    supplier_data = {
                        'id': result[0],
                        'name': result[1],
                        'contact_person': result[2],
                        'email': result[3],
                        'phone': result[4]
                    }
                    self.show_edit_supplier_dialog(supplier_data)
                else:
                    self.show_error_message(f"Supplier with ID {sup_id} not found")
        except Exception as e:
            print(f"Error fetching supplier data: {e}")
            self.show_error_message(f"Failed to load supplier data: {e}")
    
    def show_edit_supplier_dialog(self, supplier_data):
        """Show edit supplier dialog with pre-filled data"""
        try:
            print(f"DEBUG: Creating Edit Supplier dialog for: {supplier_data['name']}")
            
            # Create dialog window
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Supplier")
            dialog.setGeometry(100, 100, 450, 300)
            dialog.setStyleSheet("background-color: white;")
            dialog.setModal(True)
            
            layout = QVBoxLayout(dialog)
            
            # Title
            title = QLabel("Edit Supplier Details")
            title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            title.setStyleSheet("color: #2c3e50;")
            layout.addWidget(title)
            
            # Supplier ID (stored for later use)
            sup_id = supplier_data['id']
            
            # Form fields
            form_layout = QGridLayout()
            
            # Supplier Name
            name_label = QLabel("Supplier Name:")
            name_label.setFont(QFont("Segoe UI", 10))
            name_label.setStyleSheet("color: #2c3e50;")
            name_input = QLineEdit()
            name_input.setText(supplier_data.get('name', ''))
            name_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(name_label, 0, 0)
            form_layout.addWidget(name_input, 0, 1)
            
            # Contact Person
            contact_label = QLabel("Contact Person:")
            contact_label.setFont(QFont("Segoe UI", 10))
            contact_label.setStyleSheet("color: #2c3e50;")
            contact_input = QLineEdit()
            contact_input.setText(supplier_data.get('contact_person', ''))
            contact_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(contact_label, 1, 0)
            form_layout.addWidget(contact_input, 1, 1)
            
            # Email
            email_label = QLabel("Email:")
            email_label.setFont(QFont("Segoe UI", 10))
            email_label.setStyleSheet("color: #2c3e50;")
            email_input = QLineEdit()
            email_input.setText(supplier_data.get('email', ''))
            email_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(email_label, 2, 0)
            form_layout.addWidget(email_input, 2, 1)
            
            # Phone
            phone_label = QLabel("Phone:")
            phone_label.setFont(QFont("Segoe UI", 10))
            phone_label.setStyleSheet("color: #2c3e50;")
            phone_input = QLineEdit()
            phone_input.setText(supplier_data.get('phone', ''))
            phone_input.setStyleSheet("padding: 8px; border: 1px solid #d5dbdb; border-radius: 4px;")
            form_layout.addWidget(phone_label, 3, 0)
            form_layout.addWidget(phone_input, 3, 1)
            
            layout.addLayout(form_layout)
            
            # Buttons
            btn_layout = QHBoxLayout()
            
            update_btn = QPushButton("Update Supplier")
            update_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            
            # Add debug to update button
            def debug_update():
                print("DEBUG: Update Supplier button clicked!")
                try:
                    self.update_supplier_record(dialog, sup_id, name_input, contact_input, email_input, phone_input)
                except Exception as e:
                    print(f"DEBUG: Error in update_supplier_record: {e}")
                    import traceback
                    traceback.print_exc()
            
            update_btn.clicked.connect(debug_update)
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            cancel_btn.clicked.connect(dialog.close)
            
            btn_layout.addWidget(update_btn)
            btn_layout.addWidget(cancel_btn)
            
            layout.addLayout(btn_layout)
            
            print("DEBUG: Supplier edit dialog created successfully, showing...")
            dialog.exec()
            print("DEBUG: Dialog closed")
            
        except Exception as e:
            print(f"DEBUG: Error creating edit dialog: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to open Edit Supplier dialog: {e}")
    
    def update_supplier_record(self, dialog, sup_id, name_input, contact_input, email_input, phone_input):
        """Update supplier record in database"""
        try:
            print(f"DEBUG: update_supplier_record called for supplier ID: {sup_id}")
            
            name = name_input.text().strip()
            contact_person = contact_input.text().strip()
            email = email_input.text().strip()
            phone = phone_input.text().strip()
            
            print(f"DEBUG: Updated supplier data - Name: {name}, Contact: {contact_person}, Email: {email}, Phone: {phone}")
            
            if not name or not contact_person or not email or not phone:
                print("DEBUG: Validation failed")
                self.show_error_message("Please enter all required supplier details")
                return
            
            # Update in database
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE suppliers 
                    SET name = ?, contact_person = ?, email = ?, phone = ?
                    WHERE id = ?
                """, (name, contact_person, email, phone, sup_id))
                conn.commit()
            
            print(f"DEBUG: Supplier updated successfully!")
            
            # Close dialog first
            dialog.close()
            
            print("DEBUG: Dialog closed")
            
            # Refresh the suppliers data to show the updated supplier
            self.load_suppliers_data()
            
            self.show_success_message("Supplier updated successfully!")
            
            print("DEBUG: Success message shown")
            
        except Exception as e:
            print(f"DEBUG: Exception in update_supplier_record: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to update supplier: {e}")
    
    def delete_supplier(self, sup_id):
        """Delete supplier (placeholder for now)"""
        print(f"Delete supplier {sup_id} clicked")
        # TODO: Implement delete confirmation and database update
    
    def get_suppliers(self, search=""):
        """Get suppliers with optional filtering"""
        try:
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, name, contact_person, email, phone
                    FROM suppliers
                    WHERE 1=1
                """
                params = []
                
                if search:
                    query += " AND (name LIKE ? OR contact_person LIKE ? OR email LIKE ? OR phone LIKE ?)"
                    search_like = f"%{search}%"
                    params.extend([search_like, search_like, search_like, search_like])
                
                query += " ORDER BY name"
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                suppliers = []
                for row in results:
                    suppliers.append({
                        'id': row[0],
                        'name': row[1],
                        'contact_person': row[2],
                        'email': row[3],
                        'phone': row[4]
                    })
                
                return suppliers
        except Exception as e:
            print(f"Error getting suppliers: {e}")
            return []
    
    def create_supplier(self, name, contact_person, email, phone):
        """Create a new supplier record"""
        try:
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO suppliers (name, contact_person, email, phone)
                    VALUES (?, ?, ?, ?)
                """, (name, contact_person, email, phone))
                conn.commit()  # Explicitly commit the transaction
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating supplier: {e}")
            return None
    
    def load_customer_options(self):
        """Load real-time customer options into combo box"""
        try:
            # Clear existing items
            self.customer_var.clear()
            
            # Add default option
            self.customer_var.addItem("Walk-in Customer", None)
            
            # Get customers from database
            customers = self.get_customers()
            
            # Add customers to combo box - store full customer dict for complete_sale
            for customer in customers:
                self.customer_var.addItem(f"{customer['name']} - {customer['phone']}", customer)
            
            print(f"Loaded {len(customers)} customers into dropdown")
            
        except Exception as e:
            print(f"Error loading customer options: {e}")
            # Only keep walk-in customer option
            self.customer_var.addItem("Walk-in Customer", None)
    
    def show_customer_lookup(self):
        """Show customer lookup dialog with purchase history"""
        try:
            print("DEBUG: Opening customer lookup dialog...")
            
            # Create dialog window
            dialog = QDialog(self)
            dialog.setWindowTitle("Customer Lookup")
            dialog.setGeometry(150, 150, 800, 500)
            dialog.setStyleSheet("background-color: white;")
            dialog.setModal(True)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            
            # Title
            title = QLabel("🔍 Customer Purchase History Lookup")
            title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            title.setStyleSheet("color: #2c3e50;")
            layout.addWidget(title)
            
            # Search frame
            search_frame = QFrame()
            search_layout = QHBoxLayout(search_frame)
            search_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 8px; padding: 10px;")
            
            search_label = QLabel("Search Customer:")
            search_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            search_label.setStyleSheet("color: #2c3e50;")
            
            search_input = QLineEdit()
            search_input.setPlaceholderText("Enter customer name or phone...")
            search_input.setFixedHeight(35)
            search_input.setFont(QFont("Segoe UI", 10))
            search_input.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #d5dbdb;
                    border-radius: 6px;
                    padding: 8px 12px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border-color: #1AAE4A;
                }
            """)
            
            search_btn = QPushButton("Search")
            search_btn.setFixedHeight(35)
            search_btn.setFixedWidth(100)
            search_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            search_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1AAE4A;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #168f3c;
                }
            """)
            
            search_layout.addWidget(search_label)
            search_layout.addWidget(search_input, 1)
            search_layout.addWidget(search_btn)
            
            layout.addWidget(search_frame)
            
            # Results table
            results_label = QLabel("Search Results:")
            results_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            results_label.setStyleSheet("color: #2c3e50;")
            layout.addWidget(results_label)
            
            results_table = QTableWidget()
            results_table.setColumnCount(5)
            results_table.setHorizontalHeaderLabels(["Customer Name", "Phone", "Total Purchases", "Total Spent", "Recent Medicines"])
            results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            results_table.verticalHeader().setVisible(False)
            results_table.setAlternatingRowColors(True)
            results_table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #d5dbdb;
                    gridline-color: #ecf0f1;
                    background-color: white;
                }
                QTableWidget::item {
                    padding: 10px;
                    border-bottom: 1px solid #ecf0f1;
                }
                QHeaderView::section {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    font-weight: bold;
                    border: 1px solid #d5dbdb;
                    padding: 10px;
                }
            """)
            results_table.setMinimumHeight(250)
            
            layout.addWidget(results_table)
            
            # Empty state message
            empty_label = QLabel("Enter a customer name or phone number to search for their purchase history.")
            empty_label.setFont(QFont("Segoe UI", 10))
            empty_label.setStyleSheet("color: #7f8c8d;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(empty_label)
            
            # Search function
            def perform_search():
                search_text = search_input.text().strip()
                if not search_text:
                    return
                
                try:
                    # Use the new function to get customer purchase history summary
                    from database.modern_db import get_customer_purchase_history_summary
                    customers = get_customer_purchase_history_summary(search_text)
                    
                    if customers:
                        # Clear and populate results
                        results_table.setRowCount(len(customers))
                        empty_label.setVisible(False)
                        results_table.setVisible(True)
                        
                        for row, customer in enumerate(customers):
                            # Customer Name
                            name_item = QTableWidgetItem(customer['name'])
                            name_item.setFont(QFont("Segoe UI", 10))
                            results_table.setItem(row, 0, name_item)
                            
                            # Phone
                            phone_item = QTableWidgetItem(customer['phone'])
                            phone_item.setFont(QFont("Segoe UI", 10))
                            results_table.setItem(row, 1, phone_item)
                            
                            # Total Purchases
                            count_item = QTableWidgetItem(str(customer['purchase_count']))
                            count_item.setFont(QFont("Segoe UI", 10))
                            results_table.setItem(row, 2, count_item)
                            
                            # Total Spent
                            total_spent = customer.get('total_spent', 0)
                            spent_item = QTableWidgetItem(f"₹{total_spent:.2f}")
                            spent_item.setFont(QFont("Segoe UI", 10))
                            results_table.setItem(row, 3, spent_item)
                            
                            # Recent Medicines (NEW COLUMN)
                            medicines_item = QTableWidgetItem(customer['medicines'])
                            medicines_item.setFont(QFont("Segoe UI", 10))
                            medicines_item.setToolTip(customer['medicines'])  # Show full list on hover
                            results_table.setItem(row, 4, medicines_item)
                        
                        print(f"DEBUG: Found {len(customers)} customers matching '{search_text}'")
                    else:
                        results_table.setVisible(False)
                        empty_label.setText(f"No customers found matching '{search_text}'")
                        empty_label.setVisible(True)
                        
                except Exception as e:
                    print(f"DEBUG: Error searching customers: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Connect search button
            search_btn.clicked.connect(perform_search)
            search_input.returnPressed.connect(perform_search)
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            close_btn.clicked.connect(dialog.close)
            
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(close_btn)
            layout.addLayout(btn_layout)
            
            print("DEBUG: Customer lookup dialog created, showing...")
            dialog.exec()
            print("DEBUG: Customer lookup dialog closed")
            
        except Exception as e:
            print(f"DEBUG: Error showing customer lookup: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Failed to open customer lookup: {e}")
    
    def get_customer_purchase_count(self, customer_id):
        """Get the total number of purchases for a customer"""
        try:
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as purchase_count
                    FROM sales
                    WHERE customer_id = ?
                """, (customer_id,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"Error getting customer purchase count: {e}")
            return 0
    
    def load_supplier_options(self, combo_box):
        """Load real-time supplier options into combo box"""
        try:
            # Clear existing items
            combo_box.clear()
            
            # Add default option
            combo_box.addItem("Select Supplier", None)
            
            # Get suppliers from database
            suppliers = self.get_suppliers()
            
            # Add suppliers to combo box
            for supplier in suppliers:
                combo_box.addItem(supplier['name'], supplier['id'])
            
            print(f"Loaded {len(suppliers)} suppliers into dropdown")
            
        except Exception as e:
            print(f"Error loading supplier options: {e}")
            combo_box.addItem("Select Supplier", None)
    
    def create_reports_content(self, layout):
        """Create reports generation content"""
        title = QLabel("Reports")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        subtitle = QLabel("Generate and view various reports")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)
        
        # Report generation card
        report_card = QFrame()
        report_layout = QVBoxLayout(report_card)
        report_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 30px;
                border: 1px solid #d5dbdb;
            }
        """)
        
        card_title = QLabel("Generate Report")
        card_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        card_title.setStyleSheet("color: #2c3e50;")
        report_layout.addWidget(card_title)
        
        # Report type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("Report Type:")
        type_label.setFont(QFont("Segoe UI", 12))
        type_label.setStyleSheet("color: #2c3e50;")
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Daily Sales Report",
            "Monthly Sales Report", 
            "Low Stock Report",
            "Expiry Report",
            "Purchase History",
            "Customer Analytics"
        ])
        self.report_type_combo.setFixedHeight(40)
        self.report_type_combo.setFont(QFont("Segoe UI", 11))
        
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.report_type_combo)
        type_layout.addStretch()
        
        report_layout.addLayout(type_layout)
        
        # Date range selection
        date_layout = QHBoxLayout()
        date_label = QLabel("Date Range:")
        date_label.setFont(QFont("Segoe UI", 12))
        date_label.setStyleSheet("color: #2c3e50;")
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setFixedHeight(40)
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setFixedHeight(40)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(self.end_date)
        date_layout.addStretch()
        
        report_layout.addLayout(date_layout)
        
        # Generate button with click handler
        generate_btn = QPushButton("📊 Generate Report")
        generate_btn.setFixedHeight(50)
        generate_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #1AAE4A;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #168f3c;
            }
        """)
        
        # Connect generate button to handler
        generate_btn.clicked.connect(self.generate_report)
        
        report_layout.addWidget(generate_btn)
        
        layout.addWidget(report_card)
        
        # Report display area with scrollbar
        self.report_display = QFrame()
        self.report_display.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #d5dbdb;
            }
        """)
        
        # Create scroll area for report display
        report_scroll_area = QScrollArea()
        report_scroll_area.setWidgetResizable(True)
        report_scroll_area.setMinimumHeight(400)
        report_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
                min-height: 400px;
            }
            QScrollBar:vertical {
                width: 14px;
                background: #ecf0f1;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 7px;
                min-height: 50px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Report content widget
        report_content = QWidget()
        report_display_layout = QVBoxLayout(report_content)
        report_display_layout.setContentsMargins(20, 20, 20, 20)
        
        self.report_title = QLabel("Report Results")
        self.report_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.report_title.setStyleSheet("color: #2c3e50;")
        self.report_title.setVisible(False)
        
        self.report_table = QTableWidget()
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.verticalHeader().setVisible(False)
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d5dbdb;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #2c3e50;
                font-weight: bold;
                border: 1px solid #d5dbdb;
                padding: 8px;
            }
        """)
        self.report_table.setVisible(False)
        
        self.report_message = QLabel("Generate a report to view results here.")
        self.report_message.setFont(QFont("Segoe UI", 12))
        self.report_message.setStyleSheet("color: #7f8c8d;")
        
        report_display_layout.addWidget(self.report_title)
        report_display_layout.addWidget(self.report_table)
        report_display_layout.addWidget(self.report_message)
        
        # Set the report content as the widget for the scroll area
        report_scroll_area.setWidget(report_content)
        
        layout.addWidget(report_scroll_area)
        
        # Export options
        export_layout = QHBoxLayout()
        
        export_label = QLabel("Export Options:")
        export_label.setFont(QFont("Segoe UI", 12))
        export_label.setStyleSheet("color: #2c3e50;")
        
        csv_btn = QPushButton("📄 Export to CSV")
        csv_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        csv_btn.clicked.connect(self.export_to_csv)
        
        excel_btn = QPushButton("📊 Export to Excel")
        excel_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        excel_btn.clicked.connect(self.export_to_excel)
        
        pdf_btn = QPushButton("📄 Export to PDF")
        pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        pdf_btn.clicked.connect(self.export_to_pdf)
        
        export_layout.addWidget(export_label)
        export_layout.addWidget(csv_btn)
        export_layout.addWidget(excel_btn)
        export_layout.addWidget(pdf_btn)
        export_layout.addStretch()
        
        layout.addLayout(export_layout)
        layout.addStretch()
    
    def generate_report(self):
        """Generate the selected report"""
        try:
            report_type = self.report_type_combo.currentText()
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            
            print(f"DEBUG: Generating {report_type} report from {start_date} to {end_date}")
            
            # Show loading message
            self.report_title.setVisible(True)
            self.report_title.setText(f"Generating {report_type}...")
            self.report_table.setVisible(False)
            self.report_message.setVisible(False)
            
            # Generate sample report data based on type
            if report_type == "Daily Sales Report":
                self.generate_daily_sales_report(start_date, end_date)
            elif report_type == "Monthly Sales Report":
                self.generate_monthly_sales_report(start_date, end_date)
            elif report_type == "Low Stock Report":
                self.generate_low_stock_report()
            elif report_type == "Expiry Report":
                self.generate_expiry_report()
            elif report_type == "Purchase History":
                self.generate_purchase_history_report(start_date, end_date)
            elif report_type == "Customer Analytics":
                self.generate_customer_analytics_report(start_date, end_date)
            
        except Exception as e:
            print(f"Error generating report: {e}")
            self.show_error_message(f"Failed to generate report: {e}")
    
    def generate_daily_sales_report(self, start_date, end_date):
        """Generate daily sales report"""
        try:
            # Get sales data from database
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DATE(sale_date) as date, 
                           COUNT(*) as transactions,
                           SUM(total_amount) as total_revenue,
                           AVG(total_amount) as avg_transaction
                    FROM sales 
                    WHERE DATE(sale_date) BETWEEN ? AND ?
                    GROUP BY DATE(sale_date)
                    ORDER BY date DESC
                """, (start_date, end_date))
                
                results = cursor.fetchall()
                
                if results:
                    # Set up table
                    self.report_table.setColumnCount(4)
                    self.report_table.setHorizontalHeaderLabels(["Date", "Transactions", "Total Revenue", "Avg Transaction"])
                    self.report_table.setRowCount(len(results))
                    
                    for row, (date, transactions, total_revenue, avg_transaction) in enumerate(results):
                        self.report_table.setItem(row, 0, QTableWidgetItem(date))
                        self.report_table.setItem(row, 1, QTableWidgetItem(str(transactions)))
                        self.report_table.setItem(row, 2, QTableWidgetItem(f"₹{total_revenue:.2f}"))
                        self.report_table.setItem(row, 3, QTableWidgetItem(f"₹{avg_transaction:.2f}"))
                    
                    self.report_title.setText(f"Daily Sales Report ({start_date} to {end_date})")
                    self.report_table.setVisible(True)
                    self.report_message.setVisible(False)
                else:
                    self.report_title.setText("No sales data found for the selected date range")
                    self.report_table.setVisible(False)
                    self.report_message.setVisible(True)
                    
        except Exception as e:
            print(f"Error generating daily sales report: {e}")
            self.show_error_message(f"Failed to generate daily sales report: {e}")
    
    def generate_monthly_sales_report(self, start_date, end_date):
        """Generate monthly sales report"""
        try:
            # Get sales data from database
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT strftime('%Y-%m', sale_date) as month,
                           COUNT(*) as transactions,
                           SUM(total_amount) as total_revenue,
                           AVG(total_amount) as avg_transaction
                    FROM sales 
                    WHERE DATE(sale_date) BETWEEN ? AND ?
                    GROUP BY strftime('%Y-%m', sale_date)
                    ORDER BY month DESC
                """, (start_date, end_date))
                
                results = cursor.fetchall()
                
                if results:
                    # Set up table
                    self.report_table.setColumnCount(4)
                    self.report_table.setHorizontalHeaderLabels(["Month", "Transactions", "Total Revenue", "Avg Transaction"])
                    self.report_table.setRowCount(len(results))
                    
                    for row, (month, transactions, total_revenue, avg_transaction) in enumerate(results):
                        self.report_table.setItem(row, 0, QTableWidgetItem(month))
                        self.report_table.setItem(row, 1, QTableWidgetItem(str(transactions)))
                        self.report_table.setItem(row, 2, QTableWidgetItem(f"₹{total_revenue:.2f}"))
                        self.report_table.setItem(row, 3, QTableWidgetItem(f"₹{avg_transaction:.2f}"))
                    
                    self.report_title.setText(f"Monthly Sales Report ({start_date} to {end_date})")
                    self.report_table.setVisible(True)
                    self.report_message.setVisible(False)
                else:
                    self.report_title.setText("No sales data found for the selected date range")
                    self.report_table.setVisible(False)
                    self.report_message.setVisible(True)
                    
        except Exception as e:
            print(f"Error generating monthly sales report: {e}")
            self.show_error_message(f"Failed to generate monthly sales report: {e}")
    
    def generate_low_stock_report(self):
        """Generate low stock report"""
        try:
            # Get medicines with low stock
            medicines = get_medicines(low_stock=True)
            
            if medicines:
                # Set up table
                self.report_table.setColumnCount(5)
                self.report_table.setHorizontalHeaderLabels(["Medicine Name", "Current Stock", "Category", "Supplier", "Reorder Level"])
                self.report_table.setRowCount(len(medicines))
                
                for row, med in enumerate(medicines):
                    self.report_table.setItem(row, 0, QTableWidgetItem(med['name']))
                    self.report_table.setItem(row, 1, QTableWidgetItem(str(med['quantity'])))
                    self.report_table.setItem(row, 2, QTableWidgetItem(med['category']))
                    
                    # Get supplier name
                    supplier_name = self.get_supplier_name(med.get('supplier_id'))
                    self.report_table.setItem(row, 3, QTableWidgetItem(supplier_name))
                    
                    self.report_table.setItem(row, 4, QTableWidgetItem(str(med.get('reorder_level', 'N/A'))))
                
                self.report_title.setText(f"Low Stock Report ({len(medicines)} items)")
                self.report_table.setVisible(True)
                self.report_message.setVisible(False)
            else:
                self.report_title.setText("No low stock items found")
                self.report_table.setVisible(False)
                self.report_message.setVisible(True)
                
        except Exception as e:
            print(f"Error generating low stock report: {e}")
            self.show_error_message(f"Failed to generate low stock report: {e}")
    
    def generate_expiry_report(self):
        """Generate expiry report"""
        try:
            # Get medicines with expiry issues
            all_medicines = get_medicines()
            expired_medicines = [med for med in all_medicines if med.get('expiry_status') == 'Expired']
            near_expiry_medicines = [med for med in all_medicines if med.get('expiry_status') == 'Near Expiry']
            
            medicines = expired_medicines + near_expiry_medicines
            
            if medicines:
                # Set up table
                self.report_table.setColumnCount(5)
                self.report_table.setHorizontalHeaderLabels(["Medicine Name", "Expiry Date", "Status", "Quantity", "Category"])
                self.report_table.setRowCount(len(medicines))
                
                for row, med in enumerate(medicines):
                    self.report_table.setItem(row, 0, QTableWidgetItem(med['name']))
                    self.report_table.setItem(row, 1, QTableWidgetItem(med['expiry_date']))
                    
                    status = med.get('expiry_status', 'Valid')
                    status_item = QTableWidgetItem(status)
                    if status == 'Expired':
                        status_item.setForeground(QColor("#e74c3c"))
                    elif status == 'Near Expiry':
                        status_item.setForeground(QColor("#e67e22"))
                    self.report_table.setItem(row, 2, status_item)
                    
                    self.report_table.setItem(row, 3, QTableWidgetItem(str(med['quantity'])))
                    self.report_table.setItem(row, 4, QTableWidgetItem(med['category']))
                
                self.report_title.setText(f"Expiry Report ({len(medicines)} items)")
                self.report_table.setVisible(True)
                self.report_message.setVisible(False)
            else:
                self.report_title.setText("No expiry issues found")
                self.report_table.setVisible(False)
                self.report_message.setVisible(True)
                
        except Exception as e:
            print(f"Error generating expiry report: {e}")
            self.show_error_message(f"Failed to generate expiry report: {e}")
    
    def generate_purchase_history_report(self, start_date, end_date):
        """Generate purchase history report"""
        try:
            # Get purchase data from database
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.date, m.name, p.quantity, p.price, s.name as supplier
                    FROM purchases p
                    JOIN medicines m ON p.medicine_id = m.id
                    JOIN suppliers s ON p.supplier_id = s.id
                    WHERE DATE(p.date) BETWEEN ? AND ?
                    ORDER BY p.date DESC
                """, (start_date, end_date))
                
                results = cursor.fetchall()
                
                if results:
                    # Set up table
                    self.report_table.setColumnCount(5)
                    self.report_table.setHorizontalHeaderLabels(["Date", "Medicine", "Quantity", "Price", "Supplier"])
                    self.report_table.setRowCount(len(results))
                    
                    for row, (date, medicine, quantity, price, supplier) in enumerate(results):
                        self.report_table.setItem(row, 0, QTableWidgetItem(date))
                        self.report_table.setItem(row, 1, QTableWidgetItem(medicine))
                        self.report_table.setItem(row, 2, QTableWidgetItem(str(quantity)))
                        self.report_table.setItem(row, 3, QTableWidgetItem(f"₹{price:.2f}"))
                        self.report_table.setItem(row, 4, QTableWidgetItem(supplier))
                    
                    self.report_title.setText(f"Purchase History Report ({start_date} to {end_date})")
                    self.report_table.setVisible(True)
                    self.report_message.setVisible(False)
                else:
                    self.report_title.setText("No purchase data found for the selected date range")
                    self.report_table.setVisible(False)
                    self.report_message.setVisible(True)
                    
        except Exception as e:
            print(f"Error generating purchase history report: {e}")
            self.show_error_message(f"Failed to generate purchase history report: {e}")
    
    def generate_customer_analytics_report(self, start_date, end_date):
        """Generate customer analytics report"""
        try:
            # Get customer data from database
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.name, c.phone, COUNT(s.id) as transactions, 
                           SUM(s.total_amount) as total_spent,
                           AVG(s.total_amount) as avg_transaction
                    FROM customers c
                    LEFT JOIN sales s ON c.id = s.customer_id
                    WHERE s.sale_date BETWEEN ? AND ? OR s.id IS NULL
                    GROUP BY c.id
                    ORDER BY total_spent DESC
                """, (start_date, end_date))
                
                results = cursor.fetchall()
                
                if results:
                    # Set up table
                    self.report_table.setColumnCount(5)
                    self.report_table.setHorizontalHeaderLabels(["Customer", "Phone", "Transactions", "Total Spent", "Avg Transaction"])
                    self.report_table.setRowCount(len(results))
                    
                    for row, (name, phone, transactions, total_spent, avg_transaction) in enumerate(results):
                        self.report_table.setItem(row, 0, QTableWidgetItem(name))
                        self.report_table.setItem(row, 1, QTableWidgetItem(phone))
                        self.report_table.setItem(row, 2, QTableWidgetItem(str(transactions) if transactions else "0"))
                        self.report_table.setItem(row, 3, QTableWidgetItem(f"₹{total_spent:.2f}" if total_spent else "₹0.00"))
                        self.report_table.setItem(row, 4, QTableWidgetItem(f"₹{avg_transaction:.2f}" if avg_transaction else "₹0.00"))
                    
                    self.report_title.setText(f"Customer Analytics Report ({start_date} to {end_date})")
                    self.report_table.setVisible(True)
                    self.report_message.setVisible(False)
                else:
                    self.report_title.setText("No customer data found for the selected date range")
                    self.report_table.setVisible(False)
                    self.report_message.setVisible(True)
                    
        except Exception as e:
            print(f"Error generating customer analytics report: {e}")
            self.show_error_message(f"Failed to generate customer analytics report: {e}")
    
    def export_to_csv(self):
        """Export current report to CSV"""
        try:
            if not self.report_table.isVisible():
                self.show_error_message("No report to export")
                return
            
            import csv
            from datetime import datetime
            from PyQt6.QtWidgets import QFileDialog
            
            # Get save file path
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Report as CSV", 
                f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write headers
                    headers = []
                    for col in range(self.report_table.columnCount()):
                        headers.append(self.report_table.horizontalHeaderItem(col).text())
                    writer.writerow(headers)
                    
                    # Write data
                    for row in range(self.report_table.rowCount()):
                        row_data = []
                        for col in range(self.report_table.columnCount()):
                            item = self.report_table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                
                self.show_success_message(f"Report exported to: {file_path}")
        except Exception as e:
            self.show_error_message(f"Failed to export to CSV: {e}")
    
    def export_to_excel(self):
        """Export current report to Excel"""
        try:
            if not self.report_table.isVisible():
                self.show_error_message("No report to export")
                return
            
            # Try to import pandas and openpyxl
            try:
                import pandas as pd
            except ImportError:
                self.show_error_message("Pandas library required for Excel export. Install with: pip install pandas openpyxl")
                return
            
            from datetime import datetime
            from PyQt6.QtWidgets import QFileDialog
            
            # Get save file path
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Report as Excel", 
                f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Excel Files (*.xlsx)"
            )
            
            if file_path:
                # Create DataFrame from table data
                data = []
                headers = []
                
                # Get headers
                for col in range(self.report_table.columnCount()):
                    headers.append(self.report_table.horizontalHeaderItem(col).text())
                
                # Get data
                for row in range(self.report_table.rowCount()):
                    row_data = []
                    for col in range(self.report_table.columnCount()):
                        item = self.report_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)
                
                # Create DataFrame and export
                df = pd.DataFrame(data, columns=headers)
                df.to_excel(file_path, index=False)
                
                self.show_success_message(f"Report exported to: {file_path}")
        except Exception as e:
            self.show_error_message(f"Failed to export to Excel: {e}")
    
    def export_to_pdf(self):
        """Export current report to PDF"""
        try:
            if not self.report_table.isVisible():
                self.show_error_message("No report to export")
                return
            
            # Try to import reportlab
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
                from reportlab.lib import colors
                from reportlab.lib.styles import getSampleStyleSheet
            except ImportError:
                self.show_error_message("ReportLab library required for PDF export. Install with: pip install reportlab")
                return
            
            from datetime import datetime
            from PyQt6.QtWidgets import QFileDialog
            
            # Get save file path
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Report as PDF", 
                f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                # Create PDF document
                doc = SimpleDocTemplate(file_path, pagesize=letter)
                styles = getSampleStyleSheet()
                elements = []
                
                # Add title
                title = Paragraph(f"Report: {self.report_title.text()}", styles['Title'])
                elements.append(title)
                elements.append(Paragraph("<br/>", styles['Normal']))
                
                # Get table data
                data = []
                
                # Get headers
                headers = []
                for col in range(self.report_table.columnCount()):
                    headers.append(self.report_table.horizontalHeaderItem(col).text())
                data.append(headers)
                
                # Get data
                for row in range(self.report_table.rowCount()):
                    row_data = []
                    for col in range(self.report_table.columnCount()):
                        item = self.report_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)
                
                # Create table
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
                
                # Build PDF
                doc.build(elements)
                
                self.show_success_message(f"Report exported to: {file_path}")
        except Exception as e:
            self.show_error_message(f"Failed to export to PDF: {e}")
    
    def export_sales_to_csv(self):
        """Export sales history to CSV"""
        try:
            if not self.sales_history_table.rowCount():
                self.show_error_message("No sales data to export")
                return
            
            import csv
            from datetime import datetime
            from PyQt6.QtWidgets import QFileDialog
            
            # Get save file path
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Sales History as CSV", 
                f"sales_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write headers
                    headers = []
                    for col in range(self.sales_history_table.columnCount()):
                        headers.append(self.sales_history_table.horizontalHeaderItem(col).text())
                    writer.writerow(headers)
                    
                    # Write data
                    for row in range(self.sales_history_table.rowCount()):
                        row_data = []
                        for col in range(self.sales_history_table.columnCount()):
                            item = self.sales_history_table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                
                self.show_success_message(f"Sales history exported to: {file_path}")
        except Exception as e:
            self.show_error_message(f"Failed to export sales history: {e}")
    
    def load_sales_history(self):
        """Load sales history with date filters"""
        try:
            # Get date range filters
            start_date = self.start_date_filter.date().toString("yyyy-MM-dd")
            end_date = self.end_date_filter.date().toString("yyyy-MM-dd")
            
            # Get sales data from database
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT s.id, s.sale_date, c.name, s.total_amount, s.payment_method
                    FROM sales s
                    LEFT JOIN customers c ON s.customer_id = c.id
                    WHERE DATE(s.sale_date) BETWEEN ? AND ?
                    ORDER BY s.sale_date DESC
                """, (start_date, end_date))
                
                results = cursor.fetchall()
                
                if results:
                    # Set up table with 7 columns including Customer Phone and Actions
                    self.sales_history_table.setColumnCount(7)
                    self.sales_history_table.setHorizontalHeaderLabels(["Sale ID", "Date", "Customer", "Customer Phone", "Total Amount", "Payment Method", "Actions"])
                    self.sales_history_table.setRowCount(len(results))
                    
                    for row, (sale_id, sale_date, customer_name, total_amount, payment_method) in enumerate(results):
                        # Sale ID
                        id_item = QTableWidgetItem(str(sale_id))
                        id_item.setFont(QFont("Segoe UI", 10))
                        self.sales_history_table.setItem(row, 0, id_item)
                        
                        # Date
                        date_item = QTableWidgetItem(sale_date)
                        date_item.setFont(QFont("Segoe UI", 10))
                        self.sales_history_table.setItem(row, 1, date_item)
                        
                        # Customer
                        customer_item = QTableWidgetItem(customer_name if customer_name else "Walk-in Customer")
                        customer_item.setFont(QFont("Segoe UI", 10))
                        self.sales_history_table.setItem(row, 2, customer_item)
                        
                        # Customer Phone (NEW COLUMN)
                        # Get customer phone from database
                        customer_phone = "N/A"
                        if customer_name and customer_name != "Walk-in Customer":
                            try:
                                from database.modern_db import db
                                with db.get_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute("SELECT phone FROM customers WHERE name = ?", (customer_name,))
                                    result = cursor.fetchone()
                                    if result:
                                        customer_phone = result[0] if result[0] else "N/A"
                            except Exception as e:
                                print(f"Error fetching customer phone: {e}")
                        
                        phone_item = QTableWidgetItem(customer_phone)
                        phone_item.setFont(QFont("Segoe UI", 10))
                        self.sales_history_table.setItem(row, 3, phone_item)
                        
                        # Total Amount
                        amount_item = QTableWidgetItem(f"₹{total_amount:.2f}")
                        amount_item.setFont(QFont("Segoe UI", 10))
                        self.sales_history_table.setItem(row, 4, amount_item)
                        
                        # Payment Method
                        payment_item = QTableWidgetItem(payment_method)
                        payment_item.setFont(QFont("Segoe UI", 10))
                        self.sales_history_table.setItem(row, 5, payment_item)
                        
                        # Actions (NEW COLUMN)
                        actions_layout = QHBoxLayout()
                        actions_layout.setContentsMargins(0, 0, 0, 0)
                        actions_layout.setSpacing(5)
                        
                        view_btn = QPushButton("View")
                        view_btn.setFixedHeight(25)
                        view_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #3498db;
                                color: white;
                                border: none;
                                border-radius: 4px;
                                padding: 0px 8px 9px 8px;
                                font-size: 10px;
                                font-weight: bold;
                                text-align: center;
                            }
                            QPushButton:hover {
                                background-color: #2980b9;
                            }
                        """)
                        view_btn.clicked.connect(lambda checked, sale_id=sale_id: self.view_sale_details(sale_id))
                        
                        actions_layout.addWidget(view_btn)
                        actions_layout.addStretch()
                        
                        actions_widget = QWidget()
                        actions_widget.setLayout(actions_layout)
                        self.sales_history_table.setCellWidget(row, 6, actions_widget)
                    
                    # Update insights
                    self.update_sales_insights(results)
                    
                else:
                    # No results found
                    self.sales_history_table.setRowCount(0)
                    self.sales_insights_text.setText("No sales found for the selected date range.")
                    
        except Exception as e:
            print(f"Error loading sales history: {e}")
            self.show_error_message(f"Failed to load sales history: {e}")
    
    def update_sales_insights(self, results):
        """Update the sales insights text based on sales data"""
        try:
            if not results:
                self.sales_insights_text.setText("No sales data available for insights.")
                return
            
            # Calculate insights from sales data
            total_revenue = sum(row[3] for row in results)
            total_transactions = len(results)
            avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0
            
            # Find highest and lowest sales
            highest_sale = max(results, key=lambda x: x[3])
            lowest_sale = min(results, key=lambda x: x[3])
            
            # Calculate date range
            start_date = results[-1][1] if results else "N/A"
            end_date = results[0][1] if results else "N/A"
            
            # Generate insights text
            insights_text = f"""
            • Total Revenue: ₹{total_revenue:.2f}
            • Total Transactions: {total_transactions}
            • Average Transaction: ₹{avg_transaction:.2f}
            • Date Range: {start_date} to {end_date}
            • Highest Sale: ₹{highest_sale[3]:.2f} ({highest_sale[2] if highest_sale[2] else 'Walk-in Customer'})
            • Lowest Sale: ₹{lowest_sale[3]:.2f} ({lowest_sale[2] if lowest_sale[2] else 'Walk-in Customer'})
            """
            
            # Update the insights label
            self.sales_insights_text.setText(insights_text)
            
        except Exception as e:
            print(f"Error updating sales insights: {e}")
            self.sales_insights_text.setText("Error generating insights")
    
    def search_sales(self, search_text):
        """Search sales history by customer, medicine, or date"""
        try:
            if not search_text.strip():
                # If search is empty, reload with date filters only
                self.load_sales_history()
                return
            
            # Get date range filters
            start_date = self.start_date_filter.date().toString("yyyy-MM-dd")
            end_date = self.end_date_filter.date().toString("yyyy-MM-dd")
            
            # Search sales from database
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Search query that looks for customer name, medicine name, or date
                search_like = f"%{search_text}%"
                cursor.execute("""
                    SELECT s.id, s.sale_date, c.name, s.total_amount, s.payment_method
                    FROM sales s
                    LEFT JOIN customers c ON s.customer_id = c.id
                    WHERE (c.name LIKE ? OR s.sale_date LIKE ? OR s.id LIKE ?)
                    AND DATE(s.sale_date) BETWEEN ? AND ?
                    ORDER BY s.sale_date DESC
                """, (search_like, search_like, search_like, start_date, end_date))
                
                results = cursor.fetchall()
                
                if results:
                    # Set up table with 7 columns including Customer Phone and Actions
                    self.sales_history_table.setColumnCount(7)
                    self.sales_history_table.setHorizontalHeaderLabels(["Sale ID", "Date", "Customer", "Customer Phone", "Total Amount", "Payment Method", "Actions"])
                    self.sales_history_table.setRowCount(len(results))
                    
                    for row, (sale_id, sale_date, customer_name, total_amount, payment_method) in enumerate(results):
                        # Sale ID
                        id_item = QTableWidgetItem(str(sale_id))
                        id_item.setFont(QFont("Segoe UI", 10))
                        self.sales_history_table.setItem(row, 0, id_item)
                        
                        # Date
                        date_item = QTableWidgetItem(sale_date)
                        date_item.setFont(QFont("Segoe UI", 10))
                        self.sales_history_table.setItem(row, 1, date_item)
                        
                        # Customer
                        customer_item = QTableWidgetItem(customer_name if customer_name else "Walk-in Customer")
                        customer_item.setFont(QFont("Segoe UI", 10))
                        self.sales_history_table.setItem(row, 2, customer_item)
                        
                        # Customer Phone (NEW COLUMN)
                        phone_item = QTableWidgetItem("N/A")
                        phone_item.setFont(QFont("Segoe UI", 10))
                        self.sales_history_table.setItem(row, 3, phone_item)
                        
                        # Total Amount
                        amount_item = QTableWidgetItem(f"₹{total_amount:.2f}")
                        amount_item.setFont(QFont("Segoe UI", 10))
                        self.sales_history_table.setItem(row, 4, amount_item)
                        
                        # Payment Method
                        payment_item = QTableWidgetItem(payment_method)
                        payment_item.setFont(QFont("Segoe UI", 10))
                        self.sales_history_table.setItem(row, 5, payment_item)
                        
                        # Actions (NEW COLUMN)
                        actions_layout = QHBoxLayout()
                        actions_layout.setContentsMargins(0, 0, 0, 0)
                        actions_layout.setSpacing(5)
                        
                        view_btn = QPushButton("View")
                        view_btn.setFixedHeight(25)
                        view_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #3498db;
                                color: white;
                                border: none;
                                border-radius: 4px;
                                padding: 0px 8px 9px 8px;
                                font-size: 10px;
                                font-weight: bold;
                                text-align: center;
                            }
                            QPushButton:hover {
                                background-color: #2980b9;
                            }
                        """)
                        view_btn.clicked.connect(lambda checked, sale_id=sale_id: self.view_sale_details(sale_id))
                        
                        actions_layout.addWidget(view_btn)
                        actions_layout.addStretch()
                        
                        actions_widget = QWidget()
                        actions_widget.setLayout(actions_layout)
                        self.sales_history_table.setCellWidget(row, 6, actions_widget)
                    
                    # Update insights
                    self.update_sales_insights(results)
                    
                else:
                    # No results found
                    self.sales_history_table.setRowCount(0)
                    self.sales_insights_text.setText("No sales found matching your search criteria.")
                    
        except Exception as e:
            print(f"Error searching sales: {e}")
            self.show_error_message(f"Failed to search sales: {e}")

    def view_sale_details(self, sale_id):
        """View detailed information about a specific sale"""
        print(f"DEBUG: Viewing sale details for sale ID: {sale_id}")
        try:
            # Get sale details from database
            from database.modern_db import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT s.sale_date, c.name, s.total_amount, s.payment_method, s.discount_amount
                    FROM sales s
                    LEFT JOIN customers c ON s.customer_id = c.id
                    WHERE s.id = ?
                """, (sale_id,))
                sale_data = cursor.fetchone()

                if not sale_data:
                    self.show_error_message("Sale not found")
                    return

                # Get sale items
                cursor.execute("""
                    SELECT m.name, si.quantity, si.unit_price, si.line_total
                    FROM sale_items si
                    JOIN medicines m ON si.medicine_id = m.id
                    WHERE si.sale_id = ?
                """, (sale_id,))
                sale_items = cursor.fetchall()

            # Create detailed view dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Sale Details - ID: {sale_id}")
            dialog.setGeometry(200, 200, 700, 500)
            dialog.setStyleSheet("background-color: white;")
            dialog.setModal(True)

            dialog_layout = QVBoxLayout(dialog)

            # Sale information
            info_frame = QFrame()
            info_layout = QHBoxLayout(info_frame)
            info_frame.setStyleSheet("background-color: #f8f9fa; padding: 15px; border-radius: 8px;")

            info_title = QLabel("Sale Information")
            info_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            info_title.setStyleSheet("color: #2c3e50;")
            info_layout.addWidget(info_title)

            info_layout.addStretch()

            sale_date = QLabel(f"Date: {sale_data[0]}")
            sale_date.setFont(QFont("Segoe UI", 10))
            sale_date.setStyleSheet("color: #555555;")
            info_layout.addWidget(sale_date)

            total_amount = QLabel(f"Total: ₹{sale_data[2]:.2f}")
            total_amount.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            total_amount.setStyleSheet("color: #27AE60;")
            info_layout.addWidget(total_amount)

            dialog_layout.addWidget(info_frame)

            # Customer information
            customer_frame = QFrame()
            customer_layout = QHBoxLayout(customer_frame)
            customer_frame.setStyleSheet("background-color: white; padding: 15px;")

            customer_title = QLabel("Customer:")
            customer_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            customer_title.setStyleSheet("color: #2c3e50;")
            customer_layout.addWidget(customer_title)

            customer_name = QLabel(sale_data[1] if sale_data[1] else "Walk-in Customer")
            customer_name.setFont(QFont("Segoe UI", 11))
            customer_name.setStyleSheet("color: #2c3e50;")
            customer_layout.addWidget(customer_name)

            customer_layout.addStretch()

            payment_method = QLabel(f"Payment: {sale_data[3]}")
            payment_method.setFont(QFont("Segoe UI", 11))
            payment_method.setStyleSheet("color: #555555;")
            customer_layout.addWidget(payment_method)

            discount = QLabel(f"Discount: ₹{sale_data[4]:.2f}")
            discount.setFont(QFont("Segoe UI", 11))
            discount.setStyleSheet("color: #e67e22;")
            customer_layout.addWidget(discount)

            dialog_layout.addWidget(customer_frame)

            # Sale items table
            items_title = QLabel("Sale Items")
            items_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            items_title.setStyleSheet("color: #2c3e50;")
            dialog_layout.addWidget(items_title)

            items_table = QTableWidget()
            items_table.setColumnCount(4)
            items_table.setHorizontalHeaderLabels(["Medicine", "Quantity", "Unit Price", "Total"])
            items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            items_table.verticalHeader().setVisible(False)
            items_table.setAlternatingRowColors(True)
            items_table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #d5dbdb;
                    gridline-color: #ecf0f1;
                }
                QTableWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #ecf0f1;
                }
                QHeaderView::section {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    font-weight: bold;
                    border: 1px solid #d5dbdb;
                    padding: 8px;
                }
            """)

            if sale_items:
                items_table.setRowCount(len(sale_items))
                for row, (medicine_name, quantity, unit_price, line_total) in enumerate(sale_items):
                    items_table.setItem(row, 0, QTableWidgetItem(medicine_name))
                    items_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
                    items_table.setItem(row, 2, QTableWidgetItem(f"₹{unit_price:.2f}"))
                    items_table.setItem(row, 3, QTableWidgetItem(f"₹{line_total:.2f}"))
            else:
                items_table.setRowCount(1)
                items_table.setItem(0, 0, QTableWidgetItem("No items found"))

            dialog_layout.addWidget(items_table)

            # Status
            status_frame = QFrame()
            # Sale ID label (no status field in current schema)
            sale_id_label = QLabel(f"Sale ID: {sale_id}")
            sale_id_label.setFont(QFont("Segoe UI", 11))
            sale_id_label.setStyleSheet("color: #555555;")
            dialog_layout.addWidget(sale_id_label)

            # Close button
            close_btn = QPushButton("Close")
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            close_btn.clicked.connect(dialog.close)
            dialog_layout.addWidget(close_btn)

            dialog.exec()

        except Exception as e:
            print(f"Error viewing sale details: {e}")
            self.show_error_message(f"Failed to load sale details: {e}")

    def create_sales_history_content(self, layout):
        """Create sales history content with real-time data"""
        title = QLabel("Sales History")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        subtitle = QLabel("View and manage all sales transactions")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search sales by customer, medicine, or date...")
        search_input.setFixedHeight(40)
        search_input.setFont(QFont("Segoe UI", 11))
        search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d5dbdb;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1AAE4A;
            }
        """)
        search_input.textChanged.connect(self.search_sales)
        
        date_range_layout = QHBoxLayout()
        
        start_label = QLabel("From:")
        start_label.setFont(QFont("Segoe UI", 11))
        start_label.setStyleSheet("color: #2c3e50;")
        
        self.start_date_filter = QDateEdit()
        self.start_date_filter.setCalendarPopup(True)
        self.start_date_filter.setDate(QDate.currentDate().addDays(-30))
        self.start_date_filter.setFixedHeight(40)
        self.start_date_filter.setFont(QFont("Segoe UI", 11))
        
        end_label = QLabel("To:")
        end_label.setFont(QFont("Segoe UI", 11))
        end_label.setStyleSheet("color: #2c3e50;")
        
        self.end_date_filter = QDateEdit()
        self.end_date_filter.setCalendarPopup(True)
        self.end_date_filter.setDate(QDate.currentDate())
        self.end_date_filter.setFixedHeight(40)
        self.end_date_filter.setFont(QFont("Segoe UI", 11))
        
        date_range_layout.addWidget(start_label)
        date_range_layout.addWidget(self.start_date_filter)
        date_range_layout.addWidget(end_label)
        date_range_layout.addWidget(self.end_date_filter)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setFont(QFont("Segoe UI", 11))
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1AAE4A;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #168f3c;
            }
        """)
        refresh_btn.clicked.connect(self.load_sales_history)
        
        export_btn = QPushButton("📤 Export to CSV")
        export_btn.setFixedHeight(40)
        export_btn.setFont(QFont("Segoe UI", 11))
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        export_btn.clicked.connect(self.export_sales_to_csv)
        
        controls_layout.addWidget(search_input)
        controls_layout.addLayout(date_range_layout)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(export_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Sales history table - FIXED VERSION with real-time data
        self.sales_history_table = QTableWidget()
        self.sales_history_table.setHorizontalHeaderLabels(["Sale ID", "Date", "Customer", "Customer Phone", "Total Amount", "Payment Method", "Actions"])
        self.sales_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sales_history_table.verticalHeader().setVisible(False)
        self.sales_history_table.setAlternatingRowColors(True)
        self.sales_history_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
                border-radius: 8px;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #e8e8e8;
                color: #333333;
                background-color: white;
                font-size: 12px;
                font-family: 'Segoe UI';
                font-weight: bold;
                min-height: 40px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2e9;
                color: #1AAE4A;
                border-left: 3px solid #1AAE4A;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #ffffff;
                color: #555555;
                font-weight: 600;
                border: none;
                border-bottom: 2px solid #1AAE4A;
                padding: 12px;
                font-size: 12px;
                font-family: 'Segoe UI';
                min-height: 45px;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #ffffff;
                border: none;
            }
        """)
        self.sales_history_table.setSortingEnabled(True)
        # Set minimum row height for better visibility
        self.sales_history_table.verticalHeader().setMinimumSectionSize(50)
        
        # Add scrollbar styling
        self.sales_history_table.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                width: 14px;
                background: #ecf0f1;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 7px;
                min-height: 50px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Wrap table in scroll area to increase visible height
        sales_scroll_area = QScrollArea()
        sales_scroll_area.setWidgetResizable(True)
        sales_scroll_area.setMinimumHeight(600)  # show several rows without scrolling
        sales_scroll_area.setWidget(self.sales_history_table)
        layout.addWidget(sales_scroll_area)
        
        # Insights section
        insights_frame = QFrame()
        insights_layout = QVBoxLayout(insights_frame)
        insights_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #d5dbdb;
            }
        """)
        
        insights_title = QLabel("Sales Insights")
        insights_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        insights_title.setStyleSheet("color: #2c3e50;")
        
        self.sales_insights_text = QLabel("Loading sales data...")
        self.sales_insights_text.setFont(QFont("Segoe UI", 10))
        self.sales_insights_text.setStyleSheet("color: #555555;")
        self.sales_insights_text.setWordWrap(True)
        
        insights_layout.addWidget(insights_title)
        insights_layout.addWidget(self.sales_insights_text)
        
        layout.addWidget(insights_frame)
        layout.addStretch()
        
        # Load initial sales data
        self.load_sales_history()
        
        # Add debug to sales history
        print("DEBUG: Sales History content created successfully")
    
    def create_predictive_content(self, layout):
        """Create predictive analytics content with real-time data"""
        title = QLabel("Predictive Stock Analysis")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        subtitle = QLabel("Estimate future stock requirements based on past sales")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh Analysis")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1AAE4A;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #168f3c;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_predictive_analysis)
        
        controls_layout.addWidget(refresh_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Predictive table - FIXED VERSION with real-time data
        self.predictive_table = QTableWidget()
        self.predictive_table.setHorizontalHeaderLabels(["Medicine Name", "Current Stock", "Avg Daily Sales", "Days Until Out", "Status"])
        self.predictive_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.predictive_table.verticalHeader().setVisible(False)
        self.predictive_table.setAlternatingRowColors(True)
        self.predictive_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
                border-radius: 8px;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #e8e8e8;
                color: #333333;
                background-color: white;
                font-size: 12px;
                font-family: 'Segoe UI';
                font-weight: bold;
                min-height: 40px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2e9;
                color: #1AAE4A;
                border-left: 3px solid #1AAE4A;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #ffffff;
                color: #555555;
                font-weight: 600;
                border: none;
                border-bottom: 2px solid #1AAE4A;
                padding: 12px;
                font-size: 12px;
                font-family: 'Segoe UI';
                min-height: 45px;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #ffffff;
                border: none;
            }
        """)
        self.predictive_table.setSortingEnabled(True)
        # Set minimum row height for better visibility
        self.predictive_table.verticalHeader().setMinimumSectionSize(50)
        
        # wrap predictive table in scroll area for height
        predictive_scroll_area = QScrollArea()
        predictive_scroll_area.setWidgetResizable(True)
        predictive_scroll_area.setMinimumHeight(600)
        predictive_scroll_area.setWidget(self.predictive_table)
        layout.addWidget(predictive_scroll_area)
        
        # Insights section with real-time data
        insights_frame = QFrame()
        insights_layout = QVBoxLayout(insights_frame)
        insights_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #d5dbdb;
            }
        """)
        
        insights_title = QLabel("Stock Insights")
        insights_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        insights_title.setStyleSheet("color: #2c3e50;")
        
        self.insights_text = QLabel("Loading predictive analysis...")
        self.insights_text.setFont(QFont("Segoe UI", 10))
        self.insights_text.setStyleSheet("color: #555555;")
        self.insights_text.setWordWrap(True)
        
        insights_layout.addWidget(insights_title)
        insights_layout.addWidget(self.insights_text)
        
        layout.addWidget(insights_frame)
        layout.addStretch()
        
        # Load initial predictive analysis
        self.load_predictive_analysis()
    
    def create_settings_content(self, layout):
        """Create pharmacy settings and user management content"""
        # Authorization: only admins may access settings
        if not (self.user and self.user.get('role') == 'admin'):
            denied = QLabel("Access denied — admin only")
            denied.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            denied.setStyleSheet("color: #e74c3c;")
            layout.addWidget(denied)
            layout.addStretch()
            return
        # Pharmacy Settings Section
        title = QLabel("Pharmacy Settings")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        subtitle = QLabel("Configure your pharmacy information for invoices and reports")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)
        
        # Settings form
        settings_frame = QFrame()
        settings_layout = QVBoxLayout(settings_frame)
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #d5dbdb;
            }
        """)
        
        # Form fields
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        # Pharmacy Name
        name_label = QLabel("Pharmacy Name:")
        name_label.setFont(QFont("Segoe UI", 11))
        name_label.setStyleSheet("color: #2c3e50;")
        self.pharmacy_name_input = QLineEdit()
        self.pharmacy_name_input.setFixedHeight(40)
        self.pharmacy_name_input.setFont(QFont("Segoe UI", 11))
        self.pharmacy_name_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d5dbdb;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1AAE4A;
            }
        """)
        form_layout.addWidget(name_label, 0, 0)
        form_layout.addWidget(self.pharmacy_name_input, 0, 1)
        
        # Address
        address_label = QLabel("Address:")
        address_label.setFont(QFont("Segoe UI", 11))
        address_label.setStyleSheet("color: #2c3e50;")
        self.address_input = QLineEdit()
        self.address_input.setFixedHeight(40)
        self.address_input.setFont(QFont("Segoe UI", 11))
        self.address_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d5dbdb;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1AAE4A;
            }
        """)
        form_layout.addWidget(address_label, 1, 0)
        form_layout.addWidget(self.address_input, 1, 1)
        
        # City
        city_label = QLabel("City:")
        city_label.setFont(QFont("Segoe UI", 11))
        city_label.setStyleSheet("color: #2c3e50;")
        self.city_input = QLineEdit()
        self.city_input.setFixedHeight(40)
        self.city_input.setFont(QFont("Segoe UI", 11))
        self.city_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d5dbdb;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1AAE4A;
            }
        """)
        form_layout.addWidget(city_label, 2, 0)
        form_layout.addWidget(self.city_input, 2, 1)
        
        # Pincode
        pincode_label = QLabel("Pincode:")
        pincode_label.setFont(QFont("Segoe UI", 11))
        pincode_label.setStyleSheet("color: #2c3e50;")
        self.pincode_input = QLineEdit()
        self.pincode_input.setFixedHeight(40)
        self.pincode_input.setFont(QFont("Segoe UI", 11))
        self.pincode_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d5dbdb;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1AAE4A;
            }
        """)
        form_layout.addWidget(pincode_label, 3, 0)
        form_layout.addWidget(self.pincode_input, 3, 1)
        
        # GSTIN
        gstin_label = QLabel("GSTIN:")
        gstin_label.setFont(QFont("Segoe UI", 11))
        gstin_label.setStyleSheet("color: #2c3e50;")
        self.gstin_input = QLineEdit()
        self.gstin_input.setFixedHeight(40)
        self.gstin_input.setFont(QFont("Segoe UI", 11))
        self.gstin_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d5dbdb;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1AAE4A;
            }
        """)
        form_layout.addWidget(gstin_label, 4, 0)
        form_layout.addWidget(self.gstin_input, 4, 1)
        
        # License Number
        license_label = QLabel("License Number:")
        license_label.setFont(QFont("Segoe UI", 11))
        license_label.setStyleSheet("color: #2c3e50;")
        self.license_input = QLineEdit()
        self.license_input.setFixedHeight(40)
        self.license_input.setFont(QFont("Segoe UI", 11))
        self.license_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d5dbdb;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1AAE4A;
            }
        """)
        form_layout.addWidget(license_label, 5, 0)
        form_layout.addWidget(self.license_input, 5, 1)
        
        # Phone
        phone_label = QLabel("Phone:")
        phone_label.setFont(QFont("Segoe UI", 11))
        phone_label.setStyleSheet("color: #2c3e50;")
        self.phone_input = QLineEdit()
        self.phone_input.setFixedHeight(40)
        self.phone_input.setFont(QFont("Segoe UI", 11))
        self.phone_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d5dbdb;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1AAE4A;
            }
        """)
        form_layout.addWidget(phone_label, 6, 0)
        form_layout.addWidget(self.phone_input, 6, 1)
        
        # Email
        email_label = QLabel("Email:")
        email_label.setFont(QFont("Segoe UI", 11))
        email_label.setStyleSheet("color: #2c3e50;")
        self.email_input = QLineEdit()
        self.email_input.setFixedHeight(40)
        self.email_input.setFont(QFont("Segoe UI", 11))
        self.email_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d5dbdb;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1AAE4A;
            }
        """)
        form_layout.addWidget(email_label, 7, 0)
        form_layout.addWidget(self.email_input, 7, 1)
        
        settings_layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setFixedHeight(40)
        save_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1AAE4A;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #168f3c;
            }
        """)
        save_btn.clicked.connect(self.save_pharmacy_settings)
        
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.setFixedHeight(40)
        reset_btn.setFont(QFont("Segoe UI", 11))
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        reset_btn.clicked.connect(self.reset_pharmacy_settings)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        
        settings_layout.addLayout(btn_layout)
        
        layout.addWidget(settings_frame)
        
        # User Management Section (admin only)
        if self.user and self.user.get('role') == 'admin':
            layout.addSpacing(30)
            
            user_mgmt_title = QLabel("User Management")
            user_mgmt_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
            user_mgmt_title.setStyleSheet("color: #2c3e50;")
            layout.addWidget(user_mgmt_title)
            
            user_mgmt_subtitle = QLabel("Create staff accounts and manage user access")
            user_mgmt_subtitle.setFont(QFont("Segoe UI", 11))
            user_mgmt_subtitle.setStyleSheet("color: #7f8c8d;")
            layout.addWidget(user_mgmt_subtitle)
            
            # User form frame
            user_form_frame = QFrame()
            user_form_layout = QVBoxLayout(user_form_frame)
            user_form_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 12px;
                    padding: 20px;
                    border: 1px solid #d5dbdb;
                }
            """)
            
            # Form grid for creating new user
            user_grid = QGridLayout()
            user_grid.setSpacing(15)
            
            # Email
            user_email_label = QLabel("Email:")
            user_email_label.setFont(QFont("Segoe UI", 11))
            user_email_label.setStyleSheet("color: #2c3e50;")
            self.new_user_email = QLineEdit()
            self.new_user_email.setPlaceholderText("staff@medisys.com")
            self.new_user_email.setFixedHeight(40)
            self.new_user_email.setFont(QFont("Segoe UI", 11))
            self.new_user_email.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #d5dbdb;
                    border-radius: 8px;
                    padding: 10px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border-color: #1AAE4A;
                }
            """)
            user_grid.addWidget(user_email_label, 0, 0)
            user_grid.addWidget(self.new_user_email, 0, 1)
            
            # Password
            user_pwd_label = QLabel("Password:")
            user_pwd_label.setFont(QFont("Segoe UI", 11))
            user_pwd_label.setStyleSheet("color: #2c3e50;")
            self.new_user_password = QLineEdit()
            self.new_user_password.setPlaceholderText("Temporary password")
            self.new_user_password.setFixedHeight(40)
            self.new_user_password.setFont(QFont("Segoe UI", 11))
            self.new_user_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.new_user_password.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #d5dbdb;
                    border-radius: 8px;
                    padding: 10px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border-color: #1AAE4A;
                }
            """)
            user_grid.addWidget(user_pwd_label, 0, 2)
            user_grid.addWidget(self.new_user_password, 0, 3)
            
            # Role
            user_role_label = QLabel("Role:")
            user_role_label.setFont(QFont("Segoe UI", 11))
            user_role_label.setStyleSheet("color: #2c3e50;")
            self.new_user_role = QComboBox()
            self.new_user_role.addItems(["staff", "admin"])
            self.new_user_role.setFixedHeight(40)
            self.new_user_role.setFont(QFont("Segoe UI", 11))
            self.new_user_role.setStyleSheet("""
                QComboBox {
                    border: 2px solid #d5dbdb;
                    border-radius: 8px;
                    padding: 10px;
                    background-color: white;
                }
                QComboBox:focus {
                    border-color: #1AAE4A;
                }
            """)
            user_grid.addWidget(user_role_label, 1, 0)
            user_grid.addWidget(self.new_user_role, 1, 1)
            
            # Create user button
            create_user_btn = QPushButton("➕ Create User")
            create_user_btn.setFixedHeight(40)
            create_user_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            create_user_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1AAE4A;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #168f3c;
                }
            """)
            create_user_btn.clicked.connect(self.create_new_user)
            user_grid.addWidget(create_user_btn, 1, 2, 1, 2)
            
            user_form_layout.addLayout(user_grid)
            layout.addWidget(user_form_frame)
            
            # Users List Section
            layout.addSpacing(20)
            
            users_list_title = QLabel("Active Users")
            users_list_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            users_list_title.setStyleSheet("color: #2c3e50;")
            layout.addWidget(users_list_title)
            
            # Users table
            self.users_table = QTableWidget()
            self.users_table.setColumnCount(5)
            self.users_table.setHorizontalHeaderLabels(["Email", "Role", "Created", "Last Login", "Actions"])
            self.users_table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #d5dbdb;
                    border-radius: 8px;
                    background-color: white;
                }
                QHeaderView::section {
                    background-color: #ecf0f1;
                    padding: 8px;
                    border: 1px solid #d5dbdb;
                    font-weight: bold;
                    color: #2c3e50;
                }
                QTableWidget::item {
                    padding: 8px;
                }
            """)
            self.users_table.setColumnWidth(0, 280)
            self.users_table.setColumnWidth(1, 100)
            self.users_table.setColumnWidth(2, 150)
            self.users_table.setColumnWidth(3, 150)
            self.users_table.setColumnWidth(4, 150)
            self.users_table.setFixedHeight(300)
            # Increase row height so action buttons are not clipped
            self.users_table.verticalHeader().setDefaultSectionSize(44)
            self.load_users_table()
            
            layout.addWidget(self.users_table)
        
        layout.addStretch()
        
        # Load current settings
        self.load_pharmacy_settings()
    
    def load_pharmacy_settings(self):
        """Load current pharmacy settings into the form"""
        try:
            from database.pharmacy_settings import get_pharmacy_settings
            settings = get_pharmacy_settings()
            
            self.pharmacy_name_input.setText(settings.get('pharmacy_name', ''))
            self.address_input.setText(settings.get('address', ''))
            self.city_input.setText(settings.get('city', ''))
            self.pincode_input.setText(settings.get('pincode', ''))
            self.gstin_input.setText(settings.get('gstin', ''))
            self.license_input.setText(settings.get('license_number', ''))
            self.phone_input.setText(settings.get('phone', ''))
            self.email_input.setText(settings.get('email', ''))
            
        except Exception as e:
            print(f"Error loading pharmacy settings: {e}")
            self.show_error_message(f"Failed to load pharmacy settings: {e}")
    
    def save_pharmacy_settings(self):
        """Save pharmacy settings to database"""
        try:
            settings = {
                'pharmacy_name': self.pharmacy_name_input.text().strip(),
                'address': self.address_input.text().strip(),
                'city': self.city_input.text().strip(),
                'pincode': self.pincode_input.text().strip(),
                'gstin': self.gstin_input.text().strip(),
                'license_number': self.license_input.text().strip(),
                'phone': self.phone_input.text().strip(),
                'email': self.email_input.text().strip()
            }
            
            # Validate required fields
            if not settings['pharmacy_name']:
                self.show_error_message("Please enter a pharmacy name")
                return
            
            from database.pharmacy_settings import update_pharmacy_settings
            success = update_pharmacy_settings(settings)
            
            if success:
                self.show_success_message("Pharmacy settings saved successfully!")
            else:
                self.show_error_message("Failed to save pharmacy settings")
                
        except Exception as e:
            print(f"Error saving pharmacy settings: {e}")
            self.show_error_message(f"Failed to save pharmacy settings: {e}")
    
    def reset_pharmacy_settings(self):
        """Reset settings to default values"""
        try:
            self.pharmacy_name_input.setText('YOUR PHARMACY NAME')
            self.address_input.setText('Your Address Here')
            self.city_input.setText('City')
            self.pincode_input.setText('PINCODE')
            self.gstin_input.setText('')
            self.license_input.setText('')
            self.phone_input.setText('')
            self.email_input.setText('')
            
            self.show_success_message("Settings reset to defaults")
            
        except Exception as e:
            print(f"Error resetting settings: {e}")
            self.show_error_message(f"Failed to reset settings: {e}")
    
    def load_users_table(self):
        """Load all users into the users table"""
        try:
            from database.modern_db import get_all_users
            users = get_all_users()
            
            self.users_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                # Email
                email_item = QTableWidgetItem(user['email'])
                email_item.setFont(QFont("Segoe UI", 10))
                self.users_table.setItem(row, 0, email_item)
                
                # Role
                role_item = QTableWidgetItem(user['role'].upper())
                role_item.setFont(QFont("Segoe UI", 10))
                if user['role'] == 'admin':
                    role_item.setForeground(QColor("#e74c3c"))
                else:
                    role_item.setForeground(QColor("#3498db"))
                self.users_table.setItem(row, 1, role_item)
                
                # Created
                created_item = QTableWidgetItem(str(user['created_at']).split()[0] if user['created_at'] else 'N/A')
                created_item.setFont(QFont("Segoe UI", 10))
                self.users_table.setItem(row, 2, created_item)
                
                # Last Login
                last_login = user['last_login'] if user['last_login'] else 'Never'
                last_login_item = QTableWidgetItem(str(last_login).split()[0] if last_login != 'Never' else last_login)
                last_login_item.setFont(QFont("Segoe UI", 10))
                self.users_table.setItem(row, 3, last_login_item)
                
                # Actions: Reset + Delete
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_layout.setSpacing(6)

                reset_btn = QPushButton("🔐 Reset")
                reset_btn.setFixedHeight(30)
                reset_btn.setFont(QFont("Segoe UI", 9))
                reset_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f39c12;
                        color: white;
                        border: none;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #e08e0b;
                    }
                """)

                delete_btn = QPushButton("🗑️ Delete")
                delete_btn.setFixedHeight(30)
                delete_btn.setFont(QFont("Segoe UI", 9))
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)

                user_id = user['id']
                reset_btn.clicked.connect(lambda checked=False, uid=user_id: self.reset_user_password(uid))
                delete_btn.clicked.connect(lambda checked=False, uid=user_id: self.delete_user(uid))

                # Slightly increase button widths by 3px so they aren't cramped
                try:
                    reset_btn.setFixedWidth(reset_btn.sizeHint().width() + 3)
                    delete_btn.setFixedWidth(delete_btn.sizeHint().width() + 3)
                except Exception:
                    pass

                actions_layout.addWidget(reset_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()

                self.users_table.setCellWidget(row, 4, actions_widget)
                
        except Exception as e:
            print(f"Error loading users table: {e}")
            self.show_error_message(f"Failed to load users: {e}")
    
    def create_new_user(self):
        """Create a new staff user"""
        try:
            # Authorization: only admins can create users
            if not (self.user and self.user.get('role') == 'admin'):
                # log unauthorized attempt
                log_audit('users', None, 'UNAUTHORIZED_CREATE_ATTEMPT', {'email': email}, None, self.user.get('id') if self.user else None)
                self.show_error_message("Unauthorized: admin only")
                return
            email = self.new_user_email.text().strip()
            password = self.new_user_password.text().strip()
            role = self.new_user_role.currentText()
            
            if not email or not password:
                self.show_error_message("Please enter both email and password")
                return
            
            if len(password) < 6:
                self.show_error_message("Password must be at least 6 characters")
                return
            
            from database.modern_db import create_user
            performed_by = self.user.get('id') if self.user else None
            user_id = create_user(email, password, role, performed_by)
            
            if user_id:
                self.show_success_message(f"User '{email}' created successfully!")
                self.new_user_email.clear()
                self.new_user_password.clear()
                self.new_user_role.setCurrentIndex(0)
                self.load_users_table()
            else:
                self.show_error_message(f"Failed to create user. Email may already exist.")
                
        except Exception as e:
            print(f"Error creating user: {e}")
            self.show_error_message(f"Failed to create user: {e}")
    
    def delete_user(self, user_id: int):
        """Delete a user account"""
        try:
            # Authorization: only admins can delete users
            if not (self.user and self.user.get('role') == 'admin'):
                log_audit('users', user_id, 'UNAUTHORIZED_DELETE_ATTEMPT', None, None, self.user.get('id') if self.user else None)
                self.show_error_message("Unauthorized: admin only")
                return
            # Confirm deletion
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete this user?\nThis action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
            
            from database.modern_db import delete_user
            performed_by = self.user.get('id') if self.user else None
            if delete_user(user_id, performed_by):
                self.show_success_message("User deleted successfully!")
                self.load_users_table()
            else:
                self.show_error_message("Failed to delete user")
                
        except Exception as e:
            print(f"Error deleting user: {e}")
            self.show_error_message(f"Failed to delete user: {e}")

    def reset_user_password(self, user_id: int):
        """Prompt admin for a new password and update it (admin action)"""
        try:
            # Authorization: only admins can reset passwords
            if not (self.user and self.user.get('role') == 'admin'):
                log_audit('users', user_id, 'UNAUTHORIZED_RESET_ATTEMPT', None, None, self.user.get('id') if self.user else None)
                self.show_error_message("Unauthorized: admin only")
                return

            from PyQt6.QtWidgets import (QMessageBox, QInputDialog, QLineEdit)

            # Ask administrator to enter the desired new password
            pwd, ok = QInputDialog.getText(
                self,
                "Set New Password",
                "Enter new password for user:",
                QLineEdit.EchoMode.Password
            )
            if not ok or not pwd:
                # Cancelled or empty
                return

            # Optionally confirm
            confirm, ok2 = QInputDialog.getText(
                self,
                "Confirm Password",
                "Re-enter password to confirm:",
                QLineEdit.EchoMode.Password
            )
            if not ok2 or confirm != pwd:
                QMessageBox.warning(self, "Mismatch", "Passwords do not match. Reset aborted.")
                return

            from database.modern_db import update_user_password
            performed_by = self.user.get('id') if self.user else None
            success = update_user_password(user_id, pwd, performed_by)

            if success:
                # Copy to clipboard for admin convenience
                clipboard = QApplication.instance().clipboard()
                clipboard.setText(pwd)

                QMessageBox.information(
                    self,
                    "Password Reset",
                    "Password updated successfully and copied to clipboard."
                )
                self.show_success_message("Password updated and copied to clipboard")
            else:
                self.show_error_message("Failed to reset password")

        except Exception as e:
            print(f"Error resetting user password: {e}")
            self.show_error_message(f"Failed to reset password: {e}")

    
    def load_predictive_analysis(self):
        """Load initial predictive analysis"""
        try:
            # Get predictive stock analysis from database
            analysis = get_predictive_stock_analysis()
            
            if analysis:
                # Set up table
                self.predictive_table.setColumnCount(5)
                self.predictive_table.setHorizontalHeaderLabels(["Medicine Name", "Current Stock", "Avg Daily Sales", "Days Until Out", "Status"])
                self.predictive_table.setRowCount(len(analysis))
                
                # Populate table with analysis data
                for row, item in enumerate(analysis):
                    # Medicine Name
                    name_item = QTableWidgetItem(item['medicine_name'])
                    name_item.setFont(QFont("Segoe UI", 10))
                    self.predictive_table.setItem(row, 0, name_item)
                    
                    # Current Stock
                    stock_item = QTableWidgetItem(str(item['current_stock']))
                    stock_item.setFont(QFont("Segoe UI", 10))
                    self.predictive_table.setItem(row, 1, stock_item)
                    
                    # Avg Daily Sales
                    avg_item = QTableWidgetItem(str(item['avg_daily_sales']))
                    avg_item.setFont(QFont("Segoe UI", 10))
                    self.predictive_table.setItem(row, 2, avg_item)
                    
                    # Days Until Out
                    days_item = QTableWidgetItem(item['days_until_out'])
                    days_item.setFont(QFont("Segoe UI", 10))
                    self.predictive_table.setItem(row, 3, days_item)
                    
                    # Status
                    status_item = QTableWidgetItem(item['status'])
                    status_item.setFont(QFont("Segoe UI", 10))
                    if item['status'] == '🔴 Critical':
                        status_item.setForeground(QColor("#e74c3c"))
                    elif item['status'] == '🟡 Review':
                        status_item.setForeground(QColor("#e67e22"))
                    else:
                        status_item.setForeground(QColor("#27ae60"))
                    self.predictive_table.setItem(row, 4, status_item)
                
                # Generate insights
                self.update_predictive_insights(analysis)
                
            else:
                self.show_error_message("No predictive analysis data available.")
                
        except Exception as e:
            print(f"Error loading predictive analysis: {e}")
            # Show error message to user
            self.show_error_message("Failed to load predictive analysis")
    
    def refresh_predictive_analysis(self):
        """Refresh the predictive analysis"""
        print("Refreshing predictive analysis...")
        self.load_predictive_analysis()
    
    def update_predictive_insights(self, analysis):
        """Update the insights text based on analysis data"""
        try:
            # Count items by status
            critical_count = sum(1 for item in analysis if item['status'] == '🔴 Critical')
            review_count = sum(1 for item in analysis if item['status'] == '🟡 Review')
            ok_count = sum(1 for item in analysis if item['status'] == '🟢 OK')
            
            # Calculate average stock turnover
            total_days = sum(int(item['days_until_out'].split()[0]) for item in analysis)
            avg_turnover = total_days / len(analysis) if analysis else 0
            
            # Find highest sales velocity
            highest_velocity = max(analysis, key=lambda x: x['avg_daily_sales']) if analysis else None
            
            # Generate insights text
            insights_text = f"""
            • {critical_count} items need immediate restocking
            • {review_count} items need attention
            • {ok_count} items are in good condition
            • Average stock turnover is {avg_turnover:.1f} days
            """
            
            if highest_velocity:
                insights_text += f"• {highest_velocity['medicine_name']} has the highest sales velocity ({highest_velocity['avg_daily_sales']:.1f} units/day)"
            
            # Update the insights label
            self.insights_text.setText(insights_text)
            
        except Exception as e:
            print(f"Error updating predictive insights: {e}")
            self.insights_text.setText("Error generating insights")
    
    def logout(self):
        """Logout and return to login screen"""
        try:
            # Clear login fields for security
            self.hide()

            # Get existing login window if available, or create new one
            app = QApplication.instance()

            # Find if login window exists
            login_window = None
            for widget in app.topLevelWidgets():
                if widget.__class__.__name__ == 'ModernLoginWindow':
                    login_window = widget
                    break

            if not login_window:
                from modern_login import ModernLoginWindow
                login_window = ModernLoginWindow(main_app=self)
            else:
                # Update the reference to main app
                login_window.main_app = self
                # Clear login fields
                login_window.email_input.clear()
                login_window.password_input.clear()

            login_window.show()

        except Exception as e:
            print(f"Error during logout: {e}")
            import traceback
            traceback.print_exc()
    
    def closeEvent(self, event):
        """Handle application close event to ensure proper cleanup"""
        try:
            # Allow the application to quit when main window is closed
            app = QApplication.instance()
            if app:
                app.setQuitOnLastWindowClosed(True)
            
            # Call parent close event
            super().closeEvent(event)
        except Exception as e:
            print(f"Error in closeEvent: {e}")
            # Force close if there's an error
            event.accept()
    
    def on_app_shown(self):
        """Called when the app is shown after login/logout cycle"""
        # If user role changed (e.g., admin -> staff), rebuild sidebar
        current_role = self.user.get('role') if self.user else None
        if current_role != self.previous_role:
            # remove old sidebar and recreate it
            parent = self.sidebar.parent()
            if parent:
                # layout is HBoxLayout
                layout = parent.layout()
                # hide and detach the existing sidebar first so it doesn't float
                try:
                    self.sidebar.hide()
                except Exception:
                    pass
                layout.removeWidget(self.sidebar)
                # clear its parent so Qt won't promote it to a top‑level window
                self.sidebar.setParent(None)
                self.sidebar.deleteLater()
                # build a fresh sidebar for the new role
                self.sidebar = self.create_sidebar()
                layout.insertWidget(0, self.sidebar, 1)
            self.previous_role = current_role

        # Clear the content area
        for i in reversed(range(self.content_area.layout().count())):
            widget = self.content_area.layout().itemAt(i).widget()
            widget.setParent(None)
            widget.deleteLater()
        # Recreate page_title QLabel after clearing
        self.page_title = QLabel()
        self.page_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.page_title.setStyleSheet("color: #168f3c; margin-bottom: 12px;")
        self.page_title.setText("")
        self.content_area.layout().insertWidget(0, self.page_title)
        # Recreate page_subtitle QLabel after clearing content area
        self.page_subtitle = QLabel()
        self.page_subtitle.setFont(QFont("Segoe UI", 14))
        self.page_subtitle.setStyleSheet("color: #555555; margin-bottom: 8px;")
        self.page_subtitle.setText("")
        self.content_area.layout().insertWidget(1, self.page_subtitle)
        # Recreate subtotal_label QLabel after clearing content area
        self.subtotal_label = QLabel()
        self.subtotal_label.setFont(QFont("Segoe UI", 14))
        self.subtotal_label.setStyleSheet("color: #555555; margin-bottom: 8px;")
        self.subtotal_label.setText("")
        # Recreate content_container QScrollArea after clearing
        from PyQt6.QtWidgets import QScrollArea
        self.content_container = QScrollArea()
        self.content_container.setWidgetResizable(True)
        self.content_area.layout().addWidget(self.content_container)
        # Refresh dashboard content
        self.show_dashboard()
    
    def show_dashboard(self):
        """Show dashboard as default"""
        self.switch_view("Dashboard")
    
    def filter_medicines(self):
        """Filter medicines based on search input"""
        search_text = self.medicine_search_input.text().lower()
        
        # Clear current items
        self.medicine_var.clear()
        self.medicine_var.addItem("Select Medicine")
        
        # Get all medicines
        try:
            medicines = get_medicines()
            
            if medicines:
                for med in medicines:
                    medicine_name = med['name'].lower()
                    medicine_category = med['category'].lower()
                    medicine_price = str(med['price'])
                    
                    # Check if search text matches name, category, or price
                    if (search_text in medicine_name or 
                        search_text in medicine_category or 
                        search_text in medicine_price):
                        self.medicine_var.addItem(f"{med['name']} - ₹{med['price']:.2f}", med)
            else:
                print("No medicines found in database")
                        
        except Exception as e:
            print(f"Error filtering medicines: {e}")

def main():
    """Main entry point - start with login screen"""
    from modern_login import ModernLoginWindow
    app = QApplication(sys.argv)
    # Prevent app from exiting when all windows are hidden
    app.setQuitOnLastWindowClosed(False)
    login_window = ModernLoginWindow()
    login_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()