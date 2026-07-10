#!/usr/bin/env python3
"""
Pharmacy Settings Management Module
Handles pharmacy configuration for invoices and reports
"""

from database.modern_db import db
from typing import Dict, Optional

def get_pharmacy_settings() -> Dict:
    """Get current pharmacy settings"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pharmacy_name, address_line1, city, pincode, gst_number, license_number, phone, email, logo_path
                FROM pharmacy_settings 
                WHERE id = 1
            """)
            
            result = cursor.fetchone()
            if result:
                return {
                    'pharmacy_name': result[0],
                    'address': result[1],
                    'city': result[2],
                    'pincode': result[3],
                    'gstin': result[4],
                    'license_number': result[5],
                    'phone': result[6],
                    'email': result[7],
                    'logo_path': result[8]
                }
            else:
                # Return default settings if none found
                return {
                    'pharmacy_name': 'YOUR PHARMACY NAME',
                    'address': 'Your Address Here',
                    'city': 'City',
                    'pincode': 'PINCODE',
                    'gstin': '',
                    'license_number': '',
                    'phone': '',
                    'email': '',
                    'logo_path': ''
                }
    except Exception as e:
        print(f"Error getting pharmacy settings: {e}")
        return {
            'pharmacy_name': 'YOUR PHARMACY NAME',
            'address': 'Your Address Here',
            'city': 'City',
            'pincode': 'PINCODE',
            'gstin': '',
            'license_number': '',
            'phone': '',
            'email': '',
            'logo_path': ''
        }

def update_pharmacy_settings(settings: Dict) -> bool:
    """Update pharmacy settings"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pharmacy_settings 
                SET pharmacy_name = ?, address_line1 = ?, city = ?, pincode = ?, 
                    gst_number = ?, license_number = ?, phone = ?, email = ?
                WHERE id = 1
            """, (
                settings.get('pharmacy_name', ''),
                settings.get('address', ''),
                settings.get('city', ''),
                settings.get('pincode', ''),
                settings.get('gstin', ''),
                settings.get('license_number', ''),
                settings.get('phone', ''),
                settings.get('email', '')
            ))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating pharmacy settings: {e}")
        return False

def get_pharmacy_address() -> str:
    """Get formatted pharmacy address for invoices"""
    settings = get_pharmacy_settings()
    address_parts = []
    
    if settings['address']:
        address_parts.append(settings['address'])
    if settings['city']:
        address_parts.append(settings['city'])
    if settings['pincode']:
        address_parts.append(settings['pincode'])
    
    return ', '.join(address_parts) if address_parts else 'Address not configured'

def get_pharmacy_contact_info() -> str:
    """Get formatted pharmacy contact information"""
    settings = get_pharmacy_settings()
    contact_parts = []
    
    if settings['phone']:
        contact_parts.append(f"Phone: {settings['phone']}")
    if settings['email']:
        contact_parts.append(f"Email: {settings['email']}")
    if settings['gstin']:
        contact_parts.append(f"GSTIN: {settings['gstin']}")
    if settings['license_number']:
        contact_parts.append(f"License: {settings['license_number']}")
    
    return ' | '.join(contact_parts) if contact_parts else 'Contact information not configured'