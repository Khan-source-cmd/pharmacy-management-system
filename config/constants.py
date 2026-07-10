#!/usr/bin/env python3
"""
Application Constants
Centralized configuration for the pharmacy management system
"""

# Database settings - use absolute path to ensure consistency
import os
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pharmacy.db")
MAX_CONNECTIONS = 10

# Currency symbol used throughout the application
CURRENCY_SYMBOL = "₹"

# Business logic constants
TAX_RATE = 0.05  # 5% sales tax
DEFAULT_REORDER_LEVEL = 10
EXPIRY_WARNING_DAYS = 30

# UI constants
APP_NAME = "MediSys Pharmacy Management"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Chart settings
CHART_WIDTH = 800
CHART_HEIGHT = 400
CHART_DPI = 100

# Export settings
EXPORT_PATH = "exports/"
EXPORT_FORMATS = ['csv', 'excel', 'pdf']

# Security settings
PASSWORD_MIN_LENGTH = 8
SESSION_TIMEOUT = 3600  # 1 hour in seconds

# Audit settings
AUDIT_ENABLED = True
AUDIT_RETENTION_DAYS = 90

# Inventory settings
LOW_STOCK_THRESHOLD = 5
CRITICAL_STOCK_THRESHOLD = 2