#!/usr/bin/env python3
"""
Application Theme Configuration
Color schemes and styling for the pharmacy management system
"""

# Color palette
COLORS = {
    # Primary colors
    'primary': '#1AAE4A',      # Main green
    'primary_dark': '#168f3c', # Darker green
    'primary_light': '#28c76f', # Lighter green
    
    # Secondary colors
    'secondary': '#3498db',    # Blue
    'secondary_dark': '#2980b9',
    'secondary_light': '#5dade2',
    
    # Accent colors
    'accent': '#f39c12',       # Orange
    'accent_dark': '#e67e22',
    'accent_light': '#f1c40f', # Yellow
    
    # Status colors
    'success': '#27ae60',      # Green
    'warning': '#f1c40f',      # Yellow
    'danger': '#e74c3c',       # Red
    'info': '#3498db',         # Blue
    
    # Text colors
    'text_primary': '#2c3e50', # Dark blue-gray
    'text_secondary': '#7f8c8d', # Gray
    'text_light': '#95a5a6',   # Light gray
    'text_white': '#ffffff',
    
    # Background colors
    'bg_primary': '#ecf0f1',   # Light gray
    'bg_secondary': '#f8f9fa', # Very light gray
    'bg_white': '#ffffff',
    'bg_dark': '#2c3e50',      # Dark blue-gray
    
    # Border colors
    'border': '#d5dbdb',       # Light gray
    'border_dark': '#bdc3c7',  # Medium gray
}

# Font configurations
FONTS = {
    'heading': ('Segoe UI', 16, 'bold'),
    'subtitle': ('Segoe UI', 14, 'bold'),
    'body': ('Segoe UI', 11),
    'small': ('Segoe UI', 10),
    'code': ('Consolas', 10),
}

# Modern color scheme for PyQt6
MODERN_COLORS = {
    'primary': '#1AAE4A',
    'primary_hover': '#168f3c',
    'primary_pressed': '#137a33',
    'primary_light': '#28c76f',
    'primary_dark': '#137a33',
    
    'secondary': '#3498db',
    'secondary_hover': '#2980b9',
    'secondary_light': '#5dade2',
    
    'accent': '#f39c12',
    'accent_hover': '#e67e22',
    'accent_light': '#f1c40f',
    
    'success': '#27ae60',
    'warning': '#f1c40f',
    'danger': '#e74c3c',
    'info': '#3498db',
    
    'text_primary': '#2c3e50',
    'text_secondary': '#7f8c8d',
    'text_light': '#95a5a6',
    'text_white': '#ffffff',
    
    'bg_primary': '#ecf0f1',
    'bg_secondary': '#f8f9fa',
    'bg_card': '#ffffff',
    'bg_dark': '#2c3e50',
    
    'border': '#d5dbdb',
    'border_dark': '#bdc3c7',
    'shadow': 'rgba(0, 0, 0, 0.1)',
    
    # New gradient colors for enhanced visuals
    'gradient_start': '#1AAE4A',
    'gradient_end': '#28c76f',
    'card_shadow': 'rgba(0, 0, 0, 0.1)',
    'hover_overlay': 'rgba(255, 255, 255, 0.1)',
}

# Enhanced CSS styles for PyQt6 with animations and modern effects
MODERN_STYLES = f"""
/* Main window background with subtle gradient */
QMainWindow {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 {MODERN_COLORS['bg_primary']},
        stop: 1 {MODERN_COLORS['bg_secondary']}
    );
}}

/* Sidebar styling with enhanced gradient */
QFrame {{
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {MODERN_COLORS['primary']},
        stop: 0.5 {MODERN_COLORS['primary_hover']},
        stop: 1 {MODERN_COLORS['primary_dark']}
    );
    border-right: 2px solid rgba(255, 255, 255, 0.2);
}}

/* Navigation buttons with enhanced styling */
QPushButton {{
    background-color: transparent;
    color: rgba(255, 255, 255, 0.9);
    border: none;
    text-align: left;
    padding: 12px 15px;
    border-radius: 8px;
    font-weight: 500;
    font-family: 'Segoe UI';
    font-size: 12px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
QPushButton:hover {{
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
    transform: translateX(4px);
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.2);
}}
QPushButton:pressed {{
    background-color: rgba(255, 255, 255, 0.2);
    transform: translateX(2px);
}}

/* Content area */
QWidget {{
    background-color: {MODERN_COLORS['bg_primary']};
}}

/* Enhanced Cards with shadow and hover effects */
QFrame[objectName="card"] {{
    background-color: {MODERN_COLORS['bg_card']};
    border-radius: 16px;
    padding: 20px;
    border: 1px solid {MODERN_COLORS['border']};
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
QFrame[objectName="card"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
    border-color: {MODERN_COLORS['primary_light']};
}}

/* Enhanced Tables with better styling */
QTableWidget {{
    border: none;
    gridline-color: {MODERN_COLORS['bg_secondary']};
    background-color: {MODERN_COLORS['bg_card']};
    border-radius: 12px;
    padding: 10px;
}}
QTableWidget::item {{
    padding: 12px 8px;
    border-bottom: 1px solid {MODERN_COLORS['bg_secondary']};
    color: {MODERN_COLORS['text_primary']};
    font-family: 'Segoe UI';
    font-size: 11px;
    font-weight: 500;
    transition: background-color 0.2s ease;
}}
QTableWidget::item:hover {{
    background-color: rgba(26, 174, 74, 0.1);
}}
QTableWidget::item:selected {{
    background-color: rgba(26, 174, 74, 0.2);
    color: {MODERN_COLORS['primary']};
    font-weight: bold;
}}
QHeaderView::section {{
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {MODERN_COLORS['bg_secondary']},
        stop: 1 {MODERN_COLORS['bg_primary']}
    );
    color: {MODERN_COLORS['text_primary']};
    font-weight: bold;
    border: none;
    padding: 10px 8px;
    font-family: 'Segoe UI';
    font-size: 11px;
    border-bottom: 2px solid {MODERN_COLORS['primary']};
}}
QTableCornerButton::section {{
    background-color: {MODERN_COLORS['bg_secondary']};
    border: none;
}}

/* Enhanced Input fields with floating labels effect */
QLineEdit {{
    border: 2px solid {MODERN_COLORS['border']};
    border-radius: 10px;
    padding: 12px 14px;
    background-color: {MODERN_COLORS['bg_card']};
    font-family: 'Segoe UI';
    font-size: 11px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
QLineEdit:focus {{
    border-color: {MODERN_COLORS['primary']};
    box-shadow: 0 0 0 3px rgba(26, 174, 74, 0.1);
    transform: translateY(-1px);
}}
QLineEdit:hover {{
    border-color: {MODERN_COLORS['border_dark']};
}}

/* Enhanced Buttons with gradient and hover effects */
QPushButton[objectName="primary"] {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {MODERN_COLORS['primary']},
        stop: 1 {MODERN_COLORS['primary_hover']}
    );
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    font-weight: bold;
    font-family: 'Segoe UI';
    font-size: 11px;
    box-shadow: 0 4px 6px rgba(26, 174, 74, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
QPushButton[objectName="primary"]:hover {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {MODERN_COLORS['primary_hover']},
        stop: 1 {MODERN_COLORS['primary_dark']}
    );
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(26, 174, 74, 0.4);
}}
QPushButton[objectName="primary"]:pressed {{
    transform: translateY(1px);
    box-shadow: 0 2px 4px rgba(26, 174, 74, 0.3);
}}

QPushButton[objectName="secondary"] {{
    background-color: {MODERN_COLORS['secondary']};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    font-weight: bold;
    font-family: 'Segoe UI';
    font-size: 11px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
QPushButton[objectName="secondary"]:hover {{
    background-color: {MODERN_COLORS['secondary_hover']};
    transform: translateY(-2px);
}}

QPushButton[objectName="danger"] {{
    background-color: {MODERN_COLORS['danger']};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    font-weight: bold;
    font-family: 'Segoe UI';
    font-size: 11px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
QPushButton[objectName="danger"]:hover {{
    background-color: #c0392b;
    transform: translateY(-2px);
}}

/* Enhanced Status badges with animations */
QLabel[objectName="status_low"] {{
    background-color: {MODERN_COLORS['warning']};
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: bold;
    border: 2px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 2px 4px rgba(241, 196, 15, 0.3);
}}
QLabel[objectName="status_critical"] {{
    background-color: {MODERN_COLORS['danger']};
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: bold;
    border: 2px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 2px 4px rgba(231, 76, 60, 0.3);
}}
QLabel[objectName="status_ok"] {{
    background-color: {MODERN_COLORS['success']};
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: bold;
    border: 2px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 2px 4px rgba(39, 174, 96, 0.3);
}}

/* Enhanced Scrollbars */
QScrollBar:vertical {{
    width: 14px;
    background: {MODERN_COLORS['bg_primary']};
    border-radius: 7px;
}}
QScrollBar::handle:vertical {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 {MODERN_COLORS['primary']},
        stop: 1 {MODERN_COLORS['primary_hover']}
    );
    border-radius: 7px;
    min-height: 50px;
    border: 2px solid rgba(255, 255, 255, 0.2);
}}
QScrollBar::handle:vertical:hover {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 {MODERN_COLORS['primary_hover']},
        stop: 1 {MODERN_COLORS['primary_dark']}
    );
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* Headers and Titles */
QLabel[objectName="header"] {{
    font-family: 'Segoe UI';
    font-size: 18px;
    font-weight: bold;
    color: {MODERN_COLORS['text_primary']};
    padding: 10px 0;
}}
QLabel[objectName="subtitle"] {{
    font-family: 'Segoe UI';
    font-size: 12px;
    color: {MODERN_COLORS['text_secondary']};
    padding: 5px 0 20px 0;
}}

/* KPI Cards specific styling */
QFrame[objectName="kpi_card"] {{
    background: white;
    border-radius: 16px;
    padding: 20px;
    border: 1px solid {MODERN_COLORS['border']};
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
QFrame[objectName="kpi_card"]:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}}
"""

# Legacy theme for Tkinter (if needed)
LEGACY_THEME = {
    'card_bg': '#ecf0f1',
    'text_primary': '#2c3e50',
    'text_secondary': '#7f8c8d',
    'text_light': '#95a5a6',
    'primary_green': '#1AAE4A',
    'hover_green': '#168f3c',
    'warning': '#f1c40f',
    'success': '#27ae60',
    'danger': '#e74c3c',
    'border': '#d5dbdb',
}

# Make THEME available for legacy imports
THEME = LEGACY_THEME
FONTS = FONTS
