#!/usr/bin/env python3
"""
Simple entry point to run the Pharmacy Management System
This file provides a direct way to launch the application without going through the login screen
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_direct():
    """Run the application directly with a mock admin user"""
    from PyQt6.QtWidgets import QApplication
    from ui.modern_main_fixed import ModernMainApp
    
    # Create a mock admin user
    mock_user = {
        'id': 1, 
        'email': 'admin@medisys.com', 
        'role': 'admin', 
        'is_active': True
    }
    
    # Create and run the application
    app = QApplication(sys.argv)
    main_app = ModernMainApp(mock_user)
    main_app.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_direct()