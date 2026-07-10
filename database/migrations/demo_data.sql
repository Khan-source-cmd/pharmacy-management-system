-- Demo data for MediSys Pharmacy System
-- Run AFTER schema.sql

-- Demo Admin User (email: admin@medisys.com, password: admin123)
-- Demo Staff User (email: staff@medisys.com, password: staff123)
INSERT OR IGNORE INTO users (email, password_hash, role) VALUES
('admin@medisys.com',
 '24326224313224555153472e754261324c6147336e4d4c576c61364e2e5638577a46712e4563576366626b7153625931793547416e49516470544265',
 'admin'),
('staff@medisys.com',
 '24326224313224712e734b7a344f42327951536f6f412f666634586b657146584e545367704278465a6f4f646b78674f6d2f4536515455556c675743',
 'staff');

-- Demo Medicines (EXACTLY matching screenshot data)
INSERT OR IGNORE INTO medicines (name, category, batch_number, expiry_date, quantity, reorder_level, price) VALUES
('Paracetamol 500mg', 'Analgesics', 'BATCH001', '2026-12-31', 25, 10, 1.50),
('Amoxicillin 250mg', 'Antibiotics', 'BATCH002', '2026-06-15', 8, 10, 3.75),
('Ibuprofen 200mg', 'Analgesics', 'BATCH003', '2025-11-30', 45, 10, 2.25),
('Lisinopril 10mg', 'Cardiovascular', 'BATCH004', '2026-09-20', 32, 10, 4.50),
('Metformin 500mg', 'Antidiabetics', 'BATCH005', '2026-03-10', 18, 10, 2.80),
('Salbutamol Inhaler', 'Respiratory', 'BATCH006', '2026-08-05', 12, 10, 8.99),
('Cetirizine 10mg', 'Antihistamines', 'BATCH007', '2026-07-22', 60, 10, 1.20),
('Atorvastatin 20mg', 'Cardiovascular', 'BATCH008', '2025-12-15', 5, 10, 6.75);

-- Demo Customers (matching screenshot)
INSERT OR IGNORE INTO customers (name, email, phone) VALUES
('John Doe', 'john@example.com', '123-456-7890'),
('Jane Smith', 'jane@example.com', '098-765-4321');

-- Demo Suppliers
INSERT OR IGNORE INTO suppliers (name, contact_person, email, phone) VALUES
('Global Pharma Inc.', 'Sarah Connor', 'global@pharma.com', '555-0101'),
('MediHealth Distributors', 'Mike Ross', 'mike@medihealth.com', '555-0102');
