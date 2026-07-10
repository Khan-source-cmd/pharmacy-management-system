-- Add discount column to sales table
ALTER TABLE sales ADD COLUMN discount DECIMAL(10,2) DEFAULT 0;