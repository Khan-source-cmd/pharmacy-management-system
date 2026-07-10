#!/usr/bin/env python3
"""
Modern Table Component for PyQt6
Advanced data table with sorting, filtering, and custom styling
"""
from PyQt6.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView, 
                           QAbstractItemView, QWidget, QVBoxLayout, QHBoxLayout,
                           QLineEdit, QPushButton, QLabel, QComboBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel
from PyQt6.QtGui import QFont, QColor, QPalette
from config.theme import MODERN_COLORS, MODERN_STYLES


class ModernTable(QTableWidget):
    """Enhanced table widget with modern styling and features"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()
    
    def setup_table(self):
        """Setup table styling and behavior"""
        # Styling
        self.setStyleSheet(f"""
            QTableWidget {{
                border: none;
                gridline-color: {MODERN_COLORS['bg_secondary']};
                background-color: {MODERN_COLORS['bg_card']};
                selection-background-color: {MODERN_COLORS['primary']};
                selection-color: white;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {MODERN_COLORS['bg_secondary']};
                color: {MODERN_COLORS['text_primary']};
                font-family: 'Segoe UI';
                font-size: 10px;
            }}
            QHeaderView::section {{
                background-color: {MODERN_COLORS['bg_secondary']};
                color: {MODERN_COLORS['text_primary']};
                font-weight: bold;
                border: none;
                padding: 8px;
                font-family: 'Segoe UI';
                font-size: 10px;
            }}
            QTableWidget::item:selected {{
                background-color: {MODERN_COLORS['primary']};
                color: white;
            }}
        """)
        
        # Behavior
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Alternating row colors
        self.setStyleSheet(self.styleSheet() + f"""
            QTableWidget::item:alternate {{
                background-color: {MODERN_COLORS['bg_secondary']};
            }}
        """)


class DataTableWidget(QWidget):
    """Complete data table with search, filters, and actions"""
    
    def __init__(self, parent=None, title="Data Table", columns=None, data=None):
        super().__init__(parent)
        self.title = title
        self.columns = columns or []
        self.data = data or []
        self.filtered_data = self.data.copy()
        
        self.setup_ui()
        self.populate_data()
    
    def setup_ui(self):
        """Setup the complete table UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with title and controls
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {MODERN_COLORS['text_primary']};")
        header_layout.addWidget(title_label)
        
        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.filter_data)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {MODERN_COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                background-color: {MODERN_COLORS['bg_card']};
                font-family: 'Segoe UI';
                font-size: 10px;
            }}
            QLineEdit:focus {{
                border-color: {MODERN_COLORS['primary']};
            }}
        """)
        header_layout.addWidget(self.search_input)
        
        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("All")
        self.filter_combo.currentTextChanged.connect(self.filter_data)
        self.filter_combo.setStyleSheet(f"""
            QComboBox {{
                border: 2px solid {MODERN_COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                background-color: {MODERN_COLORS['bg_card']};
                font-family: 'Segoe UI';
                font-size: 10px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {MODERN_COLORS['bg_card']};
                border: 1px solid {MODERN_COLORS['border']};
                selection-background-color: {MODERN_COLORS['primary']};
            }}
        """)
        header_layout.addWidget(self.filter_combo)
        
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
        # Table
        self.table = ModernTable()
        if self.columns:
            self.table.setColumnCount(len(self.columns))
            self.table.setHorizontalHeaderLabels(self.columns)
        
        layout.addWidget(self.table)
        
        # Footer with stats
        footer_frame = QFrame()
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stats_label = QLabel("Showing 0 of 0 items")
        self.stats_label.setStyleSheet(f"color: {MODERN_COLORS['text_secondary']}; font-size: 10px;")
        footer_layout.addWidget(self.stats_label)
        
        footer_layout.addStretch()
        
        layout.addWidget(footer_frame)
    
    def set_data(self, data):
        """Set new data for the table"""
        self.data = data
        self.filtered_data = self.data.copy()
        self.populate_data()
    
    def set_columns(self, columns):
        """Set table columns"""
        self.columns = columns
        if self.columns:
            self.table.setColumnCount(len(self.columns))
            self.table.setHorizontalHeaderLabels(self.columns)
    
    def populate_data(self):
        """Populate table with data"""
        self.table.setRowCount(len(self.filtered_data))
        
        for row, item in enumerate(self.filtered_data):
            for col, key in enumerate(self.columns):
                value = str(item.get(key, ''))
                table_item = QTableWidgetItem(value)
                table_item.setFont(QFont("Segoe UI", 10))
                self.table.setItem(row, col, table_item)
        
        self.update_stats()
    
    def filter_data(self):
        """Filter data based on search and filter"""
        search_text = self.search_input.text().lower()
        filter_text = self.filter_combo.currentText()
        
        self.filtered_data = []
        
        for item in self.data:
            # Search logic
            search_match = True
            if search_text:
                search_match = any(search_text in str(value).lower() for value in item.values())
            
            # Filter logic (basic implementation)
            filter_match = True
            if filter_text != "All":
                # Add filter logic here based on your needs
                pass
            
            if search_match and filter_match:
                self.filtered_data.append(item)
        
        self.populate_data()
    
    def update_stats(self):
        """Update the stats label"""
        total = len(self.data)
        filtered = len(self.filtered_data)
        self.stats_label.setText(f"Showing {filtered} of {total} items")
    
    def add_filter_option(self, option):
        """Add a filter option to the dropdown"""
        self.filter_combo.addItem(option)
    
    def clear_selection(self):
        """Clear table selection"""
        self.table.clearSelection()
    
    def get_selected_row(self):
        """Get the currently selected row data"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row_index = selected_rows[0].row()
            return self.filtered_data[row_index] if row_index < len(self.filtered_data) else None
        return None


class InventoryTable(DataTableWidget):
    """Specialized table for inventory management with status badges"""
    
    def __init__(self, parent=None):
        columns = ["Name", "Category", "Stock Status", "Expiry", "Quantity", "Price", "Actions"]
        super().__init__(parent, "Medicine Inventory", columns, [])
        
        # Add filter options
        self.add_filter_option("Low Stock")
        self.add_filter_option("In Stock")
        self.add_filter_option("Expired")
    
    def populate_data(self):
        """Populate with inventory data and status badges"""
        self.table.setRowCount(len(self.filtered_data))
        
        for row, item in enumerate(self.filtered_data):
            # Name
            name_item = QTableWidgetItem(item.get('name', ''))
            name_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 0, name_item)
            
            # Category
            category_item = QTableWidgetItem(item.get('category', ''))
            category_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 1, category_item)
            
            # Stock Status (with badge styling)
            stock_status = item.get('stock_status', 'Unknown')
            stock_item = QTableWidgetItem(stock_status)
            stock_item.setFont(QFont("Segoe UI", 10))
            
            # Set color based on status
            if stock_status == 'Low Stock':
                stock_item.setForeground(QColor(MODERN_COLORS['warning']))
            elif stock_status == 'Out of Stock':
                stock_item.setForeground(QColor(MODERN_COLORS['danger']))
            else:
                stock_item.setForeground(QColor(MODERN_COLORS['success']))
            
            self.table.setItem(row, 2, stock_item)
            
            # Expiry
            expiry_item = QTableWidgetItem(item.get('expiry_date', ''))
            expiry_item.setFont(QFont("Segoe UI", 10))
            
            # Set color based on expiry status
            expiry_status = item.get('expiry_status', 'Valid')
            if expiry_status == 'Expired':
                expiry_item.setForeground(QColor(MODERN_COLORS['danger']))
            elif expiry_status == 'Near Expiry':
                expiry_item.setForeground(QColor(MODERN_COLORS['warning']))
            
            self.table.setItem(row, 3, expiry_item)
            
            # Quantity
            qty_item = QTableWidgetItem(str(item.get('quantity', 0)))
            qty_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 4, qty_item)
            
            # Price
            price_item = QTableWidgetItem(f"₹{item.get('price', 0):.2f}")
            price_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 5, price_item)
            
            # Actions (Edit/Delete buttons)
            actions_widget = self.create_action_buttons(row)
            self.table.setCellWidget(row, 6, actions_widget)
    
    def create_action_buttons(self, row):
        """Create Edit and Delete buttons for each row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setFixedHeight(25)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MODERN_COLORS['secondary']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {MODERN_COLORS['secondary_dark']};
            }}
        """)
        edit_btn.clicked.connect(lambda: self.edit_row(row))
        
        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setFixedHeight(25)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MODERN_COLORS['danger']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {MODERN_COLORS['danger']};
            }}
        """)
        delete_btn.clicked.connect(lambda: self.delete_row(row))
        
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.addStretch()
        
        return widget
    
    def edit_row(self, row):
        """Handle edit button click"""
        if row < len(self.filtered_data):
            item = self.filtered_data[row]
            print(f"Edit medicine: {item.get('name', 'Unknown')}")
            # TODO: Implement edit dialog
    
    def delete_row(self, row):
        """Handle delete button click"""
        if row < len(self.filtered_data):
            item = self.filtered_data[row]
            print(f"Delete medicine: {item.get('name', 'Unknown')}")
            # TODO: Implement delete confirmation and database update


class SalesTable(DataTableWidget):
    """Specialized table for sales data"""
    
    def __init__(self, parent=None):
        columns = ["Invoice", "Customer", "Date", "Amount"]
        super().__init__(parent, "Recent Sales", columns, [])