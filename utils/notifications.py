#!/usr/bin/env python3
"""
Advanced Notification System
- Real-time alerts for stock levels and expiries
- User-configurable notification preferences
- Toast notifications and system tray integration
"""
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread, Qt
from PyQt6.QtWidgets import (QSystemTrayIcon, QMenu, QMessageBox, QWidget,
                           QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QCheckBox, QSpinBox, QGroupBox, QComboBox)
from PyQt6.QtGui import QIcon, QPixmap, QFont, QColor, QPalette
from database.modern_db import get_medicines

class NotificationType:
    """Notification type constants"""
    LOW_STOCK = "low_stock"
    EXPIRY = "expiry"
    CRITICAL = "critical"
    INFO = "info"
    SUCCESS = "success"

class Notification:
    """Individual notification object"""
    
    def __init__(self, title: str, message: str, notification_type: str, 
                 medicine_name: str = "", priority: int = 1):
        self.title = title
        self.message = message
        self.type = notification_type
        self.medicine_name = medicine_name
        self.priority = priority
        self.timestamp = datetime.now()
        self.read = False
        self.id = id(self)

class NotificationManager(QObject):
    """Central notification management system"""
    
    notification_received = pyqtSignal(Notification)
    notification_count_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.notifications: List[Notification] = []
        self.active_alerts: Dict[str, Notification] = {}
        self.monitoring_enabled = True
        
        # Notification preferences
        self.preferences = {
            'low_stock_threshold': 10,
            'expiry_warning_days': 30,
            'enable_system_tray': True,
            'enable_popup': True,
            'enable_sound': True,
            'check_interval': 60  # seconds
        }
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def add_notification(self, notification: Notification):
        """Add a new notification"""
        self.notifications.append(notification)
        self.notification_received.emit(notification)
        
        # Update active alerts for duplicate prevention
        if notification.type in [NotificationType.LOW_STOCK, NotificationType.EXPIRY]:
            key = f"{notification.type}_{notification.medicine_name}"
            self.active_alerts[key] = notification
        
        self.notification_count_changed.emit(len([n for n in self.notifications if not n.read]))
    
    def mark_as_read(self, notification_id: int):
        """Mark notification as read"""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.read = True
                break
        self.notification_count_changed.emit(len([n for n in self.notifications if not n.read]))
    
    def get_unread_count(self) -> int:
        """Get count of unread notifications"""
        return len([n for n in self.notifications if not n.read])
    
    def get_recent_notifications(self, limit: int = 10) -> List[Notification]:
        """Get recent notifications"""
        return sorted(self.notifications, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring_enabled:
            try:
                self._check_stock_levels()
                self._check_expiry_dates()
            except Exception as e:
                print(f"Monitoring error: {e}")
            
            time.sleep(self.preferences['check_interval'])
    
    def _check_stock_levels(self):
        """Check for low stock items"""
        medicines = get_medicines()
        
        for med in medicines:
            if med['quantity'] <= self.preferences['low_stock_threshold']:
                key = f"{NotificationType.LOW_STOCK}_{med['name']}"
                
                # Prevent duplicate alerts
                if key not in self.active_alerts:
                    notification = Notification(
                        title="Low Stock Alert",
                        message=f"{med['name']} is running low (Current: {med['quantity']})",
                        notification_type=NotificationType.LOW_STOCK,
                        medicine_name=med['name'],
                        priority=2
                    )
                    self.add_notification(notification)
    
    def _check_expiry_dates(self):
        """Check for medicines nearing expiry"""
        medicines = get_medicines()
        warning_days = self.preferences['expiry_warning_days']
        
        for med in medicines:
            try:
                expiry_date = datetime.strptime(med['expiry_date'], '%Y-%m-%d')
                today = datetime.now()
                days_until_expiry = (expiry_date - today).days
                
                if days_until_expiry < 0:
                    # Expired
                    key = f"{NotificationType.CRITICAL}_{med['name']}"
                    if key not in self.active_alerts:
                        notification = Notification(
                            title="Critical: Expired Medicine",
                            message=f"{med['name']} has expired ({abs(days_until_expiry)} days ago)",
                            notification_type=NotificationType.CRITICAL,
                            medicine_name=med['name'],
                            priority=3
                        )
                        self.add_notification(notification)
                
                elif days_until_expiry <= warning_days:
                    # Near expiry
                    key = f"{NotificationType.EXPIRY}_{med['name']}"
                    if key not in self.active_alerts:
                        notification = Notification(
                            title="Expiry Warning",
                            message=f"{med['name']} expires in {days_until_expiry} days",
                            notification_type=NotificationType.EXPIRY,
                            medicine_name=med['name'],
                            priority=2
                        )
                        self.add_notification(notification)
                        
            except ValueError:
                # Invalid date format
                continue

class ToastNotification(QWidget):
    """Toast-style notification popup"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setup_ui()
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_fade)
        self.opacity = 1.0
        self.show_duration = 3000  # ms
        self.fade_duration = 1000  # ms
        
    def setup_ui(self):
        """Setup toast UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # Title
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: white;")
        
        # Message
        self.message_label = QLabel()
        self.message_label.setFont(QFont("Segoe UI", 10))
        self.message_label.setStyleSheet("color: white;")
        self.message_label.setWordWrap(True)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.message_label)
        
        self.setFixedSize(300, 100)
        
    def show_notification(self, notification: Notification):
        """Show toast notification"""
        # Set colors based on type
        colors = {
            NotificationType.LOW_STOCK: "#f39c12",  # Orange
            NotificationType.EXPIRY: "#e67e22",     # Darker orange
            NotificationType.CRITICAL: "#e74c3c",   # Red
            NotificationType.INFO: "#3498db",       # Blue
            NotificationType.SUCCESS: "#2ecc71"     # Green
        }
        
        color = colors.get(notification.type, "#95a5a6")
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
        """)
        
        self.title_label.setText(notification.title)
        self.message_label.setText(notification.message)
        
        # Position at bottom right of screen
        screen = self.screen().geometry()
        x = screen.width() - self.width() - 20
        y = screen.height() - self.height() - 100
        self.move(x, y)
        
        self.opacity = 1.0
        self.setWindowOpacity(self.opacity)
        self.show()
        
        # Start animation
        QTimer.singleShot(self.show_duration, self._start_fade_out)
    
    def _start_fade_out(self):
        """Start fade out animation"""
        self.animation_timer.start(50)  # Update every 50ms
    
    def _animate_fade(self):
        """Animate fade out"""
        self.opacity -= 1.0 / (self.fade_duration / 50)
        if self.opacity <= 0:
            self.opacity = 0
            self.animation_timer.stop()
            self.hide()
        
        self.setWindowOpacity(self.opacity)

class SystemTrayNotifier:
    """System tray integration for notifications"""
    
    def __init__(self, app):
        self.app = app
        self.tray_icon = None
        self.setup_tray()
    
    def setup_tray(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self.app)
            
            # Create tray icon
            icon = QIcon()
            # You would typically load an actual icon file here
            # For now, we'll use a simple colored rectangle
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor("#1AAE4A"))
            icon.addPixmap(pixmap)
            
            self.tray_icon.setIcon(icon)
            self.tray_icon.setVisible(True)
            
            # Create context menu
            menu = QMenu()
            
            show_action = menu.addAction("Show Application")
            show_action.triggered.connect(self.app.activeWindow().show)
            
            quit_action = menu.addAction("Quit")
            quit_action.triggered.connect(self.app.quit)
            
            self.tray_icon.setContextMenu(menu)
            
            # Connect double-click to show app
            self.tray_icon.activated.connect(self._tray_activated)
    
    def show_notification(self, title: str, message: str, duration: int = 5000):
        """Show system tray notification"""
        if self.tray_icon:
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Information,
                duration
            )
    
    def _tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.app.activeWindow():
                self.app.activeWindow().show()

class NotificationPreferencesDialog(QWidget):
    """Dialog for notification preferences"""
    
    def __init__(self, notification_manager: NotificationManager, parent=None):
        super().__init__(parent)
        self.notification_manager = notification_manager
        self.setWindowTitle("Notification Preferences")
        self.setModal(True)
        self.resize(400, 300)
        
        self.setup_ui()
        self.load_preferences()
    
    def setup_ui(self):
        """Setup preferences UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Notification Settings")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Low stock settings
        low_stock_group = QGroupBox("Low Stock Alerts")
        low_stock_layout = QVBoxLayout(low_stock_group)
        
        low_stock_layout.addWidget(QLabel("Minimum stock threshold:"))
        self.low_stock_spin = QSpinBox()
        self.low_stock_spin.setRange(0, 100)
        self.low_stock_spin.setSuffix(" units")
        low_stock_layout.addWidget(self.low_stock_spin)
        
        layout.addWidget(low_stock_group)
        
        # Expiry settings
        expiry_group = QGroupBox("Expiry Alerts")
        expiry_layout = QVBoxLayout(expiry_group)
        
        expiry_layout.addWidget(QLabel("Warning days before expiry:"))
        self.expiry_spin = QSpinBox()
        self.expiry_spin.setRange(1, 90)
        self.expiry_spin.setSuffix(" days")
        expiry_layout.addWidget(self.expiry_spin)
        
        layout.addWidget(expiry_group)
        
        # General settings
        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout(general_group)
        
        self.enable_tray_check = QCheckBox("Enable system tray notifications")
        self.enable_popup_check = QCheckBox("Enable popup notifications")
        self.enable_sound_check = QCheckBox("Enable notification sounds")
        
        general_layout.addWidget(self.enable_tray_check)
        general_layout.addWidget(self.enable_popup_check)
        general_layout.addWidget(self.enable_sound_check)
        
        layout.addWidget(general_group)
        
        # Check interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Check interval:"))
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["30 seconds", "1 minute", "5 minutes", "15 minutes"])
        interval_layout.addWidget(self.interval_combo)
        layout.addLayout(interval_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.setFixedHeight(40)
        save_btn.setStyleSheet("""
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
        save_btn.clicked.connect(self.save_preferences)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setStyleSheet("""
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
        cancel_btn.clicked.connect(self.close)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_preferences(self):
        """Load current preferences"""
        prefs = self.notification_manager.preferences
        self.low_stock_spin.setValue(prefs['low_stock_threshold'])
        self.expiry_spin.setValue(prefs['expiry_warning_days'])
        self.enable_tray_check.setChecked(prefs['enable_system_tray'])
        self.enable_popup_check.setChecked(prefs['enable_popup'])
        self.enable_sound_check.setChecked(prefs['enable_sound'])
        
        intervals = {30: 0, 60: 1, 300: 2, 900: 3}
        current_interval = prefs['check_interval']
        self.interval_combo.setCurrentIndex(intervals.get(current_interval, 1))
    
    def save_preferences(self):
        """Save preferences"""
        self.notification_manager.preferences.update({
            'low_stock_threshold': self.low_stock_spin.value(),
            'expiry_warning_days': self.expiry_spin.value(),
            'enable_system_tray': self.enable_tray_check.isChecked(),
            'enable_popup': self.enable_popup_check.isChecked(),
            'enable_sound': self.enable_sound_check.isChecked(),
            'check_interval': [30, 60, 300, 900][self.interval_combo.currentIndex()]
        })
        
        # Restart monitoring with new interval
        self.notification_manager.monitoring_enabled = False
        time.sleep(1)  # Wait for thread to stop
        self.notification_manager.monitoring_enabled = True
        self.notification_manager.monitor_thread = threading.Thread(
            target=self.notification_manager._monitor_loop, daemon=True
        )
        self.notification_manager.monitor_thread.start()
        
        self.close()

# Global notification manager instance
notification_manager = NotificationManager()

def show_notification_dialog(parent, title, message, notification_type=NotificationType.INFO):
    """Show a simple notification dialog"""
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    # Set icon based on type
    icons = {
        NotificationType.LOW_STOCK: QMessageBox.Icon.Warning,
        NotificationType.EXPIRY: QMessageBox.Icon.Warning,
        NotificationType.CRITICAL: QMessageBox.Icon.Critical,
        NotificationType.INFO: QMessageBox.Icon.Information,
        NotificationType.SUCCESS: QMessageBox.Icon.Information
    }
    
    msg_box.setIcon(icons.get(notification_type, QMessageBox.Icon.Information))
    msg_box.exec()

def create_toast_notification(parent=None):
    """Create and return a toast notification widget"""
    return ToastNotification(parent)

def create_system_tray_notifier(app):
    """Create and return a system tray notifier"""
    return SystemTrayNotifier(app)
