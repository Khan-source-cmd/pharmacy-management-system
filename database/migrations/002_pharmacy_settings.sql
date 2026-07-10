-- Pharmacy Settings Migration
-- Adds configurable pharmacy information for invoices

CREATE TABLE IF NOT EXISTS pharmacy_settings (
    id INTEGER PRIMARY KEY,
    pharmacy_name TEXT NOT NULL DEFAULT 'YOUR PHARMACY NAME',
    address TEXT NOT NULL DEFAULT 'Your Address Here',
    city TEXT NOT NULL DEFAULT 'City',
    pincode TEXT NOT NULL DEFAULT 'PINCODE',
    gstin TEXT DEFAULT '',
    license_number TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    logo_path TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default pharmacy settings
INSERT OR REPLACE INTO pharmacy_settings (
    id, pharmacy_name, address, city, pincode, gstin, license_number, phone, email
) VALUES (
    1, 'YOUR PHARMACY NAME', 'Your Address Here', 'City', 'PINCODE', '', '', '', ''
);

-- Create trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_pharmacy_settings_timestamp
AFTER UPDATE ON pharmacy_settings
FOR EACH ROW
BEGIN
    UPDATE pharmacy_settings SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;