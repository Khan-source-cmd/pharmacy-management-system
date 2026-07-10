#!/usr/bin/env python3
"""
Modern PyQt6 Login Window with Material Design
"""
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QFrame, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QPixmap
from database.modern_db import authenticate_user

class ModernLoginWindow(QMainWindow):
    def __init__(self, main_app=None):
        super().__init__()
        self.main_app = main_app  # Reference to the main app window
        self.setWindowTitle("MediSys - Pharmacy Management System")
        self.resize(500, 650)
        self.setMinimumSize(400, 550)
        self.center_window()
        
        # Set up main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Create gradient background
        self.set_background_gradient()
        
        # Setup UI
        self.setup_ui(main_widget)
    
    def center_window(self):
        """Center window on screen"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def set_background_gradient(self):
        """Set gradient background"""
        # Use stylesheet for gradient background
        self.setStyleSheet("""
            QMainWindow {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1AAE4A,
                    stop: 1 #0f5b26
                );
            }
        """)
    
    def setup_ui(self, main_widget):
        """Setup modern login UI"""
        # Main layout - vertical
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 80, 0, 60)  # Perfect centering with no left margin
        main_layout.setSpacing(25)  # Reduced spacing for better proportion
        
        # Logo section
        logo_layout = QVBoxLayout()
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
        
        logo_layout.addWidget(logo_label)
        
        # App title
        title_label = QLabel("MediSys")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle_label = QLabel("Pharmacy Management System")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_layout.addWidget(title_label)
        logo_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(logo_layout)
        
        # Center the form container horizontally
        center_layout = QHBoxLayout()
        center_layout.addStretch()  # Push form to center
        
        # Form container
        form_container = QFrame()
        form_container.setMaximumWidth(400)  # Limit maximum width for professional appearance
        form_container.setMinimumWidth(380)  # Further increased minimum width to prevent squishing
        form_container.setMinimumHeight(450)  # Increased minimum height to prevent compression and show full border
        form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                padding: 20px;
            }
        """)
        
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(30)  # Increased spacing to prevent collision
        form_layout.setContentsMargins(20, 20, 20, 20)  # Add padding inside the form
        
        # Email field
        email_layout = QVBoxLayout()
        email_label = QLabel("Email Address")
        email_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Medium))
        email_label.setStyleSheet("color: #333333; margin-left: -20px;")
        email_label.setFixedHeight(55)
        email_label.setMinimumHeight(55)
        email_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setFixedHeight(55)
        self.email_input.setMinimumHeight(55)
        self.email_input.setFont(QFont("Segoe UI", 12))
        self.email_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d0d0d0;
                border-radius: 8px;
                padding: 12px 10px;
                background-color: #ffffff;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #1AAE4A;
                background-color: #ffffff;
                border-width: 3px;
            }
        """)
        
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        email_layout.setSpacing(30)  # Gap between email label and input field
        
        # Password field
        password_layout = QVBoxLayout()
        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Medium))
        password_label.setStyleSheet("color: #333333; margin-left: -20px;")
        password_label.setFixedHeight(55)
        password_label.setMinimumHeight(55)
        password_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(55)
        self.password_input.setMinimumHeight(55)
        self.password_input.setFont(QFont("Segoe UI", 12))
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                background-color: #fafafa;
            }
            QLineEdit:focus {
                border-color: #1AAE4A;
                background-color: white;
            }
        """)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        password_layout.setSpacing(30)  # Gap between password label and input field
        
        # Login button
        self.login_button = QPushButton("Sign In")
        self.login_button.setFixedHeight(50)
        self.login_button.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #1AAE4A;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #168f3c;
            }
            QPushButton:pressed {
                background-color: #127a32;
            }
        """)
        self.login_button.clicked.connect(self.on_login)
        
        # Hint for obtaining credentials
        hint_label = QLabel("Demo: admin@medisys.com / admin123 (for initial setup only)\nAdmin can create staff accounts in Settings")
        hint_label.setFont(QFont("Segoe UI", 8))
        hint_label.setStyleSheet("color: #999999;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        form_layout.addLayout(email_layout)
        form_layout.addSpacing(15)  # Add more space between email input field and password label
        form_layout.addLayout(password_layout)
        form_layout.addSpacing(25)  # Add more spacing above the signup button
        form_layout.addWidget(self.login_button)
        form_layout.addWidget(hint_label)
        
        center_layout.addWidget(form_container)
        center_layout.addStretch()  # Push form to center
        
        main_layout.addLayout(center_layout)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: white;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        main_widget.setLayout(main_layout)
    
    def on_login(self):
        """Handle login attempt"""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not email or not password:
            self.show_message("Please enter both email and password", error=True)
            return
        # Use database authentication
        user = authenticate_user(email, password)
        if user:
            # Keep a minimal user object for the app (don't expose password_hash)
            self.authenticated_user = {
                'id': user.get('id'),
                'email': user.get('email'),
                'role': user.get('role')
            }
            self.show_message("Login successful! Opening dashboard...", error=False)
            QTimer.singleShot(1000, self.open_dashboard)
        else:
            self.show_message("Invalid credentials.", error=True)
    
    def show_message(self, message, error=False):
        """Show status message with animation"""
        color = "#ff4444" if error else "#44ff44"
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # Animation effect
        animation = QPropertyAnimation(self.status_label, b"windowOpacity")
        animation.setDuration(500)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        animation.start()
    
    def open_dashboard(self):
        """Open main dashboard"""
        self.status_label.setText("Loading dashboard...")
        
        try:
            if self.main_app:
                # Returning from logout - reuse existing main app
                self.main_app.user = getattr(self, 'authenticated_user', None)
                self.main_app.on_app_shown()
                self.main_app.show()
                self.hide()  # Just hide, don't close
            else:
                # First login - create new main app
                from modern_main_fixed import ModernMainApp
                app = QApplication.instance()
                main_window = ModernMainApp(getattr(self, 'authenticated_user', None))
                main_window.show()
                self.hide()  # Just hide, don't close
        except ImportError as e:
            print(f"Failed to import main application: {e}")
            self.show_message("Application loading failed. Please check installation.", error=True)

def main():
    app = QApplication(sys.argv)
    window = ModernLoginWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
