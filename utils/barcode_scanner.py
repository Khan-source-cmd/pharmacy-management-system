#!/usr/bin/env python3
"""
Barcode Scanner Integration Module
- Simulates barcode scanning functionality
- Integrates with inventory management
- Real-time stock updates
"""
import time
import random
from typing import Optional, Dict, List
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                           QFrame, QMessageBox)
from PyQt6.QtGui import QFont, QColor
from database.modern_db import get_medicines, create_sale

class BarcodeScanner(QObject):
    """Barcode scanner simulation with real-time updates"""
    
    barcode_scanned = pyqtSignal(str)
    scan_error = pyqtSignal(str)
    item_added = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.is_scanning = False
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self._simulate_scan)
        self.scan_timer.setInterval(1000)  # Simulate scan every second
        
        # Mock barcode mappings
        self.barcode_map = {
            "1234567890123": 1,  # Paracetamol
            "2345678901234": 2,  # Amoxicillin
            "3456789012345": 3,  # Ibuprofen
            "4567890123456": 4,  # Lisinopril
            "5678901234567": 5,  # Metformin
        }
    
    def start_scanning(self):
        """Start barcode scanning simulation"""
        if not self.is_scanning:
            self.is_scanning = True
            self.scan_timer.start()
            print("Barcode scanner started")
    
    def stop_scanning(self):
        """Stop barcode scanning"""
        if self.is_scanning:
            self.is_scanning = False
            self.scan_timer.stop()
            print("Barcode scanner stopped")
    
    def _simulate_scan(self):
        """Simulate barcode scanning with random success/failure"""
        # Simulate scanning process
        if random.random() < 0.1:  # 10% chance of scan
            # Generate random barcode
            barcode = f"{random.randint(1000000000000, 9999999999999)}"
            
            if barcode in self.barcode_map:
                medicine_id = self.barcode_map[barcode]
                self.barcode_scanned.emit(str(barcode))
                
                # Get medicine details
                medicines = get_medicines()
                for med in medicines:
                    if med['id'] == medicine_id:
                        self.item_added.emit({
                            'medicine_id': medicine_id,
                            'name': med['name'],
                            'price': med['price'],
                            'quantity': 1
                        })
                        break
            else:
                self.scan_error.emit(f"Unknown barcode: {barcode}")

class BarcodeScannerDialog(QDialog):
    """Barcode scanner dialog for sales processing"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Barcode Scanner")
        self.setModal(True)
        self.resize(500, 400)
        
        self.scanner = BarcodeScanner()
        self.scanner.barcode_scanned.connect(self.on_barcode_scanned)
        self.scanner.scan_error.connect(self.on_scan_error)
        self.scanner.item_added.connect(self.on_item_added)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup barcode scanner UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("Barcode Scanner")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        
        subtitle = QLabel("Scan medicine barcodes to add to bill")
        subtitle.setStyleSheet("color: #7f8c8d;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_frame)
        
        # Scanner status
        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(20, 15, 20, 15)
        
        self.status_label = QLabel("Scanner Status: Ready")
        self.status_label.setFont(QFont("Segoe UI", 12))
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        
        self.scan_button = QPushButton("Start Scanning")
        self.scan_button.setFixedHeight(40)
        self.scan_button.setStyleSheet("""
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
        self.scan_button.clicked.connect(self.toggle_scanning)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.scan_button)
        
        layout.addWidget(status_frame)
        
        # Current scan display
        scan_frame = QFrame()
        scan_layout = QVBoxLayout(scan_frame)
        scan_layout.setContentsMargins(20, 15, 20, 15)
        
        scan_title = QLabel("Last Scan:")
        scan_title.setFont(QFont("Segoe UI", 12))
        scan_title.setStyleSheet("color: #2c3e50;")
        
        self.scan_result = QLabel("No scans yet")
        self.scan_result.setFont(QFont("Segoe UI", 14))
        self.scan_result.setStyleSheet("color: #7f8c8d;")
        
        scan_layout.addWidget(scan_title)
        scan_layout.addWidget(self.scan_result)
        
        layout.addWidget(scan_frame)
        
        # Items table
        items_frame = QFrame()
        items_layout = QVBoxLayout(items_frame)
        items_layout.setContentsMargins(20, 15, 20, 15)
        
        items_title = QLabel("Scanned Items:")
        items_title.setFont(QFont("Segoe UI", 12))
        items_title.setStyleSheet("color: #2c3e50;")
        
        self.items_table = QTableWidget(0, 4)
        self.items_table.setHorizontalHeaderLabels(["Medicine", "Quantity", "Price", "Total"])
        self.items_table.horizontalHeader().setSectionResizeMode(0, 2)  # Stretch first column
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setAlternatingRowColors(True)
        self.items_table.setStyleSheet("""
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
                border: none;
                padding: 8px;
            }
        """)
        
        items_layout.addWidget(items_title)
        items_layout.addWidget(self.items_table)
        
        layout.addWidget(items_frame)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear All")
        clear_btn.setFixedHeight(40)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_btn.clicked.connect(self.clear_items)
        
        done_btn = QPushButton("Done")
        done_btn.setFixedHeight(40)
        done_btn.setStyleSheet("""
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
        done_btn.clicked.connect(self.accept)
        
        controls_layout.addWidget(clear_btn)
        controls_layout.addWidget(done_btn)
        
        layout.addLayout(controls_layout)
    
    def toggle_scanning(self):
        """Toggle scanning on/off"""
        if self.scanner.is_scanning:
            self.scanner.stop_scanning()
            self.status_label.setText("Scanner Status: Stopped")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.scan_button.setText("Start Scanning")
            self.scan_button.setStyleSheet("""
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
        else:
            self.scanner.start_scanning()
            self.status_label.setText("Scanner Status: Active")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.scan_button.setText("Stop Scanning")
            self.scan_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
    
    def on_barcode_scanned(self, barcode):
        """Handle successful barcode scan"""
        self.scan_result.setText(f"Scanned: {barcode}")
        self.scan_result.setStyleSheet("color: #27ae60; font-weight: bold;")
    
    def on_scan_error(self, error_msg):
        """Handle scan error"""
        self.scan_result.setText(f"Error: {error_msg}")
        self.scan_result.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def on_item_added(self, item):
        """Handle item added to bill"""
        # Check if item already exists
        existing_row = -1
        for row in range(self.items_table.rowCount()):
            if self.items_table.item(row, 0).text() == item['name']:
                existing_row = row
                break
        
        if existing_row >= 0:
            # Update existing item quantity
            current_qty = int(self.items_table.item(existing_row, 1).text())
            new_qty = current_qty + 1
            new_total = new_qty * item['price']
            
            self.items_table.item(existing_row, 1).setText(str(new_qty))
            self.items_table.item(existing_row, 3).setText(f"₹{new_total:.2f}")
        else:
            # Add new item
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)
            
            name_item = QTableWidgetItem(item['name'])
            qty_item = QTableWidgetItem("1")
            price_item = QTableWidgetItem(f"₹{item['price']:.2f}")
            total_item = QTableWidgetItem(f"₹{item['price']:.2f}")
            
            for item_widget in [name_item, qty_item, price_item, total_item]:
                item_widget.setFont(QFont("Segoe UI", 10))
            
            self.items_table.setItem(row, 0, name_item)
            self.items_table.setItem(row, 1, qty_item)
            self.items_table.setItem(row, 2, price_item)
            self.items_table.setItem(row, 3, total_item)
    
    def clear_items(self):
        """Clear all scanned items"""
        self.items_table.setRowCount(0)
        self.scan_result.setText("Cleared all items")
        self.scan_result.setStyleSheet("color: #7f8c8d;")
    
    def get_items(self) -> List[Dict]:
        """Get all scanned items"""
        items = []
        for row in range(self.items_table.rowCount()):
            items.append({
                'medicine_id': self.get_medicine_id_by_name(self.items_table.item(row, 0).text()),
                'quantity': int(self.items_table.item(row, 1).text()),
                'unit_price': float(self.items_table.item(row, 2).text().replace('₹', '')),
                'line_total': float(self.items_table.item(row, 3).text().replace('₹', ''))
            })
        return items
    
    def get_medicine_id_by_name(self, name: str) -> int:
        """Get medicine ID by name (simplified for demo)"""
        medicine_map = {
            "Paracetamol 500mg": 1,
            "Amoxicillin 250mg": 2,
            "Ibuprofen 200mg": 3,
            "Lisinopril 10mg": 4,
            "Metformin 500mg": 5,
        }
        return medicine_map.get(name, 1)  # Default to Paracetamol
    
    def closeEvent(self, event):
        """Clean up when dialog closes"""
        self.scanner.stop_scanning()
        super().closeEvent(event)

class RealTimeStockMonitor(QObject):
    """Real-time stock level monitoring with alerts"""
    
    stock_alert = pyqtSignal(str, str)  # message, severity
    expiry_alert = pyqtSignal(str, str)  # message, severity
    
    def __init__(self):
        super().__init__()
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.check_stock_levels)
        self.monitor_timer.start(30000)  # Check every 30 seconds
    
    def check_stock_levels(self):
        """Check stock levels and send alerts"""
        medicines = get_medicines()
        
        for med in medicines:
            # Check low stock
            if med['quantity'] <= med['reorder_level']:
                message = f"Low stock alert: {med['name']} (Current: {med['quantity']}, Reorder: {med['reorder_level']})"
                self.stock_alert.emit(message, "warning")
            
            # Check expiry
            from datetime import datetime
            expiry_date = datetime.strptime(med['expiry_date'], '%Y-%m-%d')
            today = datetime.now()
            days_until_expiry = (expiry_date - today).days
            
            if days_until_expiry < 0:
                message = f"Expired medicine: {med['name']} (Expired {abs(days_until_expiry)} days ago)"
                self.expiry_alert.emit(message, "critical")
            elif days_until_expiry <= 30:
                message = f"Near expiry: {med['name']} (Expires in {days_until_expiry} days)"
                self.expiry_alert.emit(message, "warning")

def show_barcode_scanner_dialog(parent):
    """Show barcode scanner dialog"""
    dialog = BarcodeScannerDialog(parent)
    if dialog.exec():
        return dialog.get_items()
    return []

# Convenience function for sales integration
def process_barcode_sale(customer_id=None, user_id=1):
    """Process sale using barcode scanner"""
    try:
        # This would be called from the sales module
        # For now, return mock data
        return [
            {'medicine_id': 1, 'quantity': 2, 'unit_price': 1.50, 'line_total': 3.00},
            {'medicine_id': 3, 'quantity': 1, 'unit_price': 2.25, 'line_total': 2.25}
        ]
    except Exception as e:
        print(f"Barcode sale processing failed: {e}")
        return []
