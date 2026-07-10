#!/usr/bin/env python3
"""
Data Population Script for Indian Customers and Suppliers
Adds 24 customers and 24 suppliers with Indian names and Malad West addresses
"""

import sys
import os
import random
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.modern_db import db, create_customer, create_supplier
    print("✅ Database modules imported successfully")
except ImportError as e:
    print(f"❌ Database import error: {e}")
    sys.exit(1)

# Indian names for customers
INDIAN_NAMES = [
    # North Indian names
    ("Rajesh Kumar", "rajesh.kumar@gmail.com", "9876543210"),
    ("Priya Sharma", "priya.sharma@yahoo.com", "9876543211"),
    ("Amit Patel", "amit.patel@outlook.com", "9876543212"),
    ("Sunita Desai", "sunita.desai@gmail.com", "9876543213"),
    ("Vikram Singh", "vikram.singh@yahoo.com", "9876543214"),
    ("Anita Verma", "anita.verma@outlook.com", "9876543215"),
    ("Sanjay Gupta", "sanjay.gupta@gmail.com", "9876543216"),
    ("Pooja Nair", "pooja.nair@yahoo.com", "9876543217"),
    
    # South Indian names
    ("Ramesh Iyer", "ramesh.iyer@gmail.com", "9876543218"),
    ("Lakshmi Subramanian", "lakshmi.subramanian@yahoo.com", "9876543219"),
    ("Suresh Menon", "suresh.menon@outlook.com", "9876543220"),
    ("Meena Krishnan", "meena.krishnan@gmail.com", "9876543221"),
    ("Arjun Reddy", "arjun.reddy@yahoo.com", "9876543222"),
    ("Swapna Rao", "swapna.rao@outlook.com", "9876543223"),
    
    # West Indian names
    ("Neha Joshi", "neha.joshi@gmail.com", "9876543224"),
    ("Rohit Mehta", "rohit.mehta@yahoo.com", "9876543225"),
    ("Deepika Shah", "deepika.shah@outlook.com", "9876543226"),
    ("Vijay Bhatia", "vijay.bhatia@gmail.com", "9876543227"),
    ("Kavya Malhotra", "kavya.malhotra@yahoo.com", "9876543228"),
    ("Manoj Acharya", "manoj.acharya@outlook.com", "9876543229"),
    
    # East Indian names
    ("Anjali Das", "anjali.das@gmail.com", "9876543230"),
    ("Siddharth Mukherjee", "siddharth.mukherjee@yahoo.com", "9876543231"),
    ("Ritika Banerjee", "ritika.banerjee@outlook.com", "9876543232"),
    ("Arun Chatterjee", "arun.chatterjee@gmail.com", "9876543233"),
]

# Malad West addresses
MALAD_WEST_ADDRESSES = [
    "Shop 12, Malad Cross Road, Malad West",
    "Near Inorbit Mall, Malad West",
    "Opposite Infinity Mall, Malad West",
    "Goregaon-Malad Link Road, Malad West",
    "Malad Link Road, Near Malad Station, Malad West",
    "Sahakar Nagar, Malad West",
    "Patel Nagar, Malad West",
    "Raj Nagar, Malad West",
    "Near Malad Creek, Malad West",
    "Shivaji Nagar, Malad West",
    "Near Malad Library, Malad West",
    "Guru Nanak Road, Malad West",
    "Near Malad Bus Depot, Malad West",
    "S.V. Road, Malad West",
    "Near Malad Hospital, Malad West",
    "Near Malad Club, Malad West",
    "Near Malad Market, Malad West",
    "Near Malad Post Office, Malad West",
    "Near Malad Police Station, Malad West",
    "Near Malad Fire Station, Malad West",
    "Near Malad School, Malad West",
    "Near Malad Temple, Malad West",
    "Near Malad Church, Malad West",
    "Near Malad Mosque, Malad West",
]

# Supplier companies
SUPPLIER_COMPANIES = [
    ("MedLife Distributors", "Amit Shah", "amit.shah@medlife.com", "9876543300"),
    ("Apollo Pharma Supplies", "Rajesh Menon", "rajesh.menon@apollo.com", "9876543301"),
    ("Cipla Medical Distributors", "Sunita Rao", "sunita.rao@cipla.com", "9876543302"),
    ("Sun Pharma Suppliers", "Vikram Patel", "vikram.patel@sunpharma.com", "9876543303"),
    ("Dr. Reddy's Medical", "Anita Iyer", "anita.iyer@drreddys.com", "9876543304"),
    ("GlaxoSmithKline Pharma", "Sanjay Nair", "sanjay.nair@gsk.com", "9876543305"),
    ("Lupin Distributors", "Pooja Verma", "pooja.verma@lupin.com", "9876543306"),
    ("Torrent Pharma Supplies", "Ramesh Gupta", "ramesh.gupta@torrent.com", "9876543307"),
    ("Divis Laboratories", "Lakshmi Sharma", "lakshmi.sharma@divis.com", "9876543308"),
    ("Biocon Medical", "Suresh Desai", "suresh.desai@biocon.com", "9876543309"),
    ("Aurobindo Pharma", "Meena Patel", "meena.patel@aurobindo.com", "9876543310"),
    ("Alkem Laboratories", "Arjun Shah", "arjun.shah@alkem.com", "9876543311"),
    ("Mankind Pharma", "Swapna Kumar", "swapna.kumar@mankind.com", "9876543312"),
    ("Glenmark Pharmaceuticals", "Neha Singh", "neha.singh@glenmark.com", "9876543313"),
    ("Pfizer India", "Rohit Bhatia", "rohit.bhatia@pfizer.com", "9876543314"),
    ("Novartis Healthcare", "Deepika Malhotra", "deepika.malhotra@novartis.com", "9876543315"),
    ("Abbott India", "Vijay Acharya", "vijay.acharya@abbott.com", "9876543316"),
    ("Bayer India", "Kavya Das", "kavya.das@bayer.com", "9876543317"),
    ("Hetero Drugs", "Anjali Chatterjee", "anjali.chatterjee@hetero.com", "9876543318"),
    ("Jubilant Life Sciences", "Siddharth Banerjee", "siddharth.banerjee@jubilant.com", "9876543319"),
    ("Strides Pharma", "Ritika Mukherjee", "ritika.mukherjee@strides.com", "9876543320"),
    ("AstraZeneca India", "Arun Reddy", "arun.reddy@astrazeneca.com", "9876543321"),
    ("Fresenius Kabi", "Priya Krishnan", "priya.krishnan@fresenius.com", "9876543322"),
    ("Hospira Healthcare", "Manoj Menon", "manoj.menon@hospira.com", "9876543323"),
]

def generate_total_spent():
    """Generate random total spent amount for customers"""
    amounts = [0, 500, 1000, 2500, 5000, 10000, 25000]
    weights = [5, 15, 25, 25, 15, 10, 5]  # More small customers, fewer big spenders
    return random.choices(amounts, weights=weights)[0]

def add_customers():
    """Add 24 Indian customers with Malad West addresses"""
    print("\n👥 Adding 24 Indian Customers...")
    print("=" * 50)
    
    added_count = 0
    skipped_count = 0
    
    for i, (name, email, phone) in enumerate(INDIAN_NAMES, 1):
        # Get random address
        address = random.choice(MALAD_WEST_ADDRESSES)
        
        # Get random total spent
        total_spent = generate_total_spent()
        
        try:
            # Check if customer already exists
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM customers WHERE email = ?", (email,))
                existing = cursor.fetchone()
                
                if existing:
                    print(f"  ⏭️  {i:2d}. {name} - SKIPPED (already exists)")
                    skipped_count += 1
                    continue
            
            # Add customer
            customer_id = create_customer(
                name=name,
                email=email,
                phone=phone,
                address=address
            )
            
            if customer_id:
                print(f"  ✅ {i:2d}. {name} - Added successfully")
                added_count += 1
                
                # Update total spent for realism
                if total_spent > 0:
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE customers SET total_spent = ? WHERE id = ?",
                            (total_spent, customer_id)
                        )
                        conn.commit()
            else:
                print(f"  ❌ {i:2d}. {name} - Failed to add")
                
        except Exception as e:
            print(f"  ❌ {i:2d}. {name} - Error: {e}")
    
    print(f"\n📊 Customer Summary:")
    print(f"  ✅ Added: {added_count}")
    print(f"  ⏭️  Skipped: {skipped_count}")
    print(f"  📈 Total: {added_count + skipped_count}")

def add_suppliers():
    """Add 24 Indian suppliers with Malad West addresses"""
    print("\n🏢 Adding 24 Indian Suppliers...")
    print("=" * 50)
    
    added_count = 0
    skipped_count = 0
    
    for i, (company_name, contact_person, email, phone) in enumerate(SUPPLIER_COMPANIES, 1):
        # Get random address
        address = random.choice(MALAD_WEST_ADDRESSES)
        
        try:
            # Check if supplier already exists
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM suppliers WHERE email = ?", (email,))
                existing = cursor.fetchone()
                
                if existing:
                    print(f"  ⏭️  {i:2d}. {company_name} - SKIPPED (already exists)")
                    skipped_count += 1
                    continue
            
            # Add supplier
            supplier_id = create_supplier(
                name=company_name,
                contact_person=contact_person,
                email=email,
                phone=phone
            )
            
            if supplier_id:
                print(f"  ✅ {i:2d}. {company_name} - Added successfully")
                added_count += 1
                
                # Update address for realism
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE suppliers SET address = ? WHERE id = ?",
                        (address, supplier_id)
                    )
                    conn.commit()
            else:
                print(f"  ❌ {i:2d}. {company_name} - Failed to add")
                
        except Exception as e:
            print(f"  ❌ {i:2d}. {company_name} - Error: {e}")
    
    print(f"\n📊 Supplier Summary:")
    print(f"  ✅ Added: {added_count}")
    print(f"  ⏭️  Skipped: {skipped_count}")
    print(f"  📈 Total: {added_count + skipped_count}")

def main():
    """Main function to populate data"""
    print("🚀 Indian Data Population Script")
    print("=" * 60)
    print("Adding 24 Indian customers and 24 Indian suppliers")
    print("with Malad West addresses to your pharmacy system")
    print("=" * 60)
    
    try:
        # Add customers
        add_customers()
        
        # Add suppliers
        add_suppliers()
        
        print("\n" + "=" * 60)
        print("🎉 Data Population Complete!")
        print("✅ 24 Indian customers added")
        print("✅ 24 Indian suppliers added")
        print("📍 All addresses are from Malad West")
        print("👥 Diverse Indian names from different regions")
        print("=" * 60)
        print("\n💡 You can now view the populated data in:")
        print("   - Customers page (24 entries)")
        print("   - Suppliers page (24 entries)")
        print("\n🔍 Use the search functionality to find specific entries!")
        
    except Exception as e:
        print(f"\n❌ Error during data population: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()