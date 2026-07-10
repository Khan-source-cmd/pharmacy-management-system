# Pharmacy Management System

A comprehensive pharmacy management desktop application built with Python and CustomTkinter. Manages inventory, sales, suppliers, customers, and generates reports with a modern UI.

## Features

- 💊 **Medicine Inventory** - Track medicine stock, expiry dates, and pricing
- 🛒 **Sales Management** - Process sales with barcode scanning support
- 👥 **Customer Management** - Maintain customer records and purchase history
- 🏭 **Supplier Management** - Manage supplier information and orders
- 📊 **Dashboard** - Visual analytics with charts and key metrics
- 📈 **Reports** - Generate detailed sales and inventory reports
- 🔮 **Predictive Analytics** - Sales forecasting and inventory predictions
- 📦 **Barcode Scanner** - Scan medicine barcodes for quick checkout
- 📄 **Invoice Generation** - Generate and print professional invoices
- 🎨 **Modern UI** - Built with CustomTkinter for a clean, modern interface

## Tech Stack

- **Language**: Python 3.x
- **UI Framework**: CustomTkinter
- **Database**: SQLite3
- **Charts**: Matplotlib
- **Barcode**: python-barcode, Pillow
- **Export**: ReportLab, openpyxl

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/pharmacy-management-system.git

# Navigate to project
cd pharmacy-management-system

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python database/init_db.py

# Run the application
python run_app.py
```

## Project Structure

```
pharmacy-management-system/
├── main/
│   └── main.py              # Application entry point
├── ui/                       # User interface components
│   ├── login.py              # Login screen
│   ├── dashboard.py          # Main dashboard
│   ├── inventory.py          # Inventory management
│   ├── sales.py              # Sales interface
│   ├── customers.py          # Customer management
│   ├── suppliers.py          # Supplier management
│   ├── reports.py            # Reports generation
│   └── predictive.py         # Predictive analytics
├── models/                   # Data models
│   ├── medicine.py
│   ├── sale.py
│   ├── customer.py
│   ├── supplier.py
│   └── user.py
├── database/                 # Database layer
│   ├── init_db.py
│   └── schema.sql
├── config/                   # Configuration
├── utils/                    # Utility functions
├── components/               # Reusable UI components
├── assets/                   # Icons and assets
├── docs/                     # Documentation
└── requirements.txt
```

## Note

This project was built based on requirements provided by a friend. The implementation and code were written by me.
