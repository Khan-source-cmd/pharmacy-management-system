"""
Reports Module - Screenshot #5
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from config.theme import THEME, FONTS
import sqlite3
import csv
import pandas as pd
from datetime import datetime

class ReportsView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=THEME['card_bg'])
        self.setup_reports()
    
    def setup_reports(self):
        """Reports generation UI"""
        title = tk.Label(self, text="Reports", font=('Segoe UI', 24, 'bold'),
                        fg=THEME['text_primary'], bg=THEME['card_bg'])
        title.pack(pady=(30, 10))
        
        subtitle = tk.Label(self, text="Generate and view various reports for sales, inventory, and more.",
                           font=FONTS['body'], fg=THEME['text_secondary'], bg=THEME['card_bg'])
        subtitle.pack(pady=(0, 40))
        
        # Generate Report card (center)
        report_card = tk.Frame(self, bg='white', relief='solid', bd=1, width=500, height=300)
        report_card.pack(expand=True)
        report_card.place(relx=0.5, rely=0.5, anchor='center')
        report_card.pack_propagate(False)
        
        tk.Label(report_card, text="Generate Report", font=FONTS['subtitle'],
                fg=THEME['text_primary'], bg='white').pack(pady=(40, 20), anchor='center')
        
        # Report type dropdown
        report_frame = tk.Frame(report_card, bg='white')
        report_frame.pack(pady=20)
        tk.Label(report_frame, text="Report Type:", font=FONTS['body'],
                fg=THEME['text_primary'], bg='white').pack(anchor='w', padx=50)
        
        self.report_var = tk.StringVar(value="Daily Sales Report")
        report_combo = ttk.Combobox(report_frame, textvariable=self.report_var,
                                   font=FONTS['body'], width=25, state='readonly')
        report_combo['values'] = ['Daily Sales Report', 'Monthly Sales Report', 
                                 'Low Stock Report', 'Expiry Report', 'Purchase History']
        report_combo.pack(pady=(10, 30), padx=50)
        
        # Generate button
        generate_btn = tk.Button(report_card, text="Generate", font=FONTS['heading'],
                               bg=THEME['primary_green'], fg='white', relief='flat',
                               cursor='hand2', height=2, command=self.generate_report)
        generate_btn.pack(pady=20)
    
    def generate_report(self):
        """Generate selected report"""
        report_type = self.report_var.get()
        
        # Create export buttons
        self.create_export_buttons(report_type)
        
        # Generate and display report data
        if report_type == "Daily Sales Report":
            self.generate_daily_sales_report()
        elif report_type == "Monthly Sales Report":
            self.generate_monthly_sales_report()
        elif report_type == "Low Stock Report":
            self.generate_low_stock_report()
        elif report_type == "Expiry Report":
            self.generate_expiry_report()
        elif report_type == "Purchase History":
            self.generate_purchase_history()
    
    def create_export_buttons(self, report_type):
        """Create export buttons for the report"""
        # Remove existing export buttons if any
        for widget in self.winfo_children():
            if hasattr(widget, 'export_buttons'):
                widget.destroy()
        
        # Export buttons frame
        export_frame = tk.Frame(self, bg=THEME['card_bg'])
        export_frame.pack(pady=(20, 0))
        export_frame.export_buttons = True  # Mark for cleanup
        
        tk.Label(export_frame, text="Export Options:", font=FONTS['body'],
                fg=THEME['text_primary'], bg=THEME['card_bg']).pack(pady=(0, 10))
        
        # CSV Export
        csv_btn = tk.Button(export_frame, text="📄 Export to CSV", font=FONTS['body'],
                          bg='#3498db', fg='white', relief='flat', cursor='hand2',
                          command=lambda: self.export_to_csv(report_type))
        csv_btn.pack(side='left', padx=5)
        
        # Excel Export
        excel_btn = tk.Button(export_frame, text="📊 Export to Excel", font=FONTS['body'],
                            bg='#2ecc71', fg='white', relief='flat', cursor='hand2',
                            command=lambda: self.export_to_excel(report_type))
        excel_btn.pack(side='left', padx=5)
        
        # PDF Export
        pdf_btn = tk.Button(export_frame, text="📄 Export to PDF", font=FONTS['body'],
                          bg='#9b59b6', fg='white', relief='flat', cursor='hand2',
                          command=lambda: self.export_to_pdf(report_type))
        pdf_btn.pack(side='left', padx=5)
    
    def generate_daily_sales_report(self):
        """Generate daily sales report"""
        try:
            with get_connection() as conn:
                cursor = conn.execute("""
                    SELECT s.invoice_number, c.name as customer_name, 
                           s.sale_date, s.total_amount
                    FROM sales s
                    LEFT JOIN customers c ON s.customer_id = c.id
                    WHERE date(s.sale_date) = date('now')
                    ORDER BY s.sale_date DESC
                """)
                
                data = cursor.fetchall()
                
                if data:
                    messagebox.showinfo("Report Generated", 
                                      f"Daily Sales Report: {len(data)} sales found")
                else:
                    messagebox.showinfo("Report Generated", "No sales found for today")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def generate_monthly_sales_report(self):
        """Generate monthly sales report"""
        try:
            with get_connection() as conn:
                cursor = conn.execute("""
                    SELECT strftime('%Y-%m', sale_date) as month,
                           COUNT(*) as total_sales,
                           SUM(total_amount) as total_revenue
                    FROM sales
                    WHERE strftime('%Y-%m', sale_date) = strftime('%Y-%m', 'now')
                    GROUP BY strftime('%Y-%m', sale_date)
                """)
                
                data = cursor.fetchall()
                
                if data:
                    month_data = data[0]
                    messagebox.showinfo("Report Generated", 
                                      f"Monthly Sales Report:\n"
                                      f"Month: {month_data[0]}\n"
                                      f"Total Sales: {month_data[1]}\n"
                                      f"Total Revenue: ₹{month_data[2]:.2f}")
                else:
                    messagebox.showinfo("Report Generated", "No sales found for this month")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def generate_low_stock_report(self):
        """Generate low stock report"""
        try:
            with get_connection() as conn:
                cursor = conn.execute("""
                    SELECT name, category, quantity, reorder_level
                    FROM medicines
                    WHERE quantity <= reorder_level
                    ORDER BY quantity ASC
                """)
                
                data = cursor.fetchall()
                
                if data:
                    report_text = "Low Stock Report:\n\n"
                    for item in data:
                        report_text += f"{item[0]} ({item[1]}): {item[2]} units (Reorder at: {item[3]})\n"
                    
                    messagebox.showinfo("Report Generated", report_text)
                else:
                    messagebox.showinfo("Report Generated", "No items are low in stock")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def generate_expiry_report(self):
        """Generate expiry report"""
        try:
            with get_connection() as conn:
                cursor = conn.execute("""
                    SELECT name, category, expiry_date
                    FROM medicines
                    WHERE expiry_date < date('now', '+30 days')
                    ORDER BY expiry_date ASC
                """)
                
                data = cursor.fetchall()
                
                if data:
                    report_text = "Expiry Report (Items expiring within 30 days):\n\n"
                    for item in data:
                        report_text += f"{item[0]} ({item[1]}): Expires on {item[2]}\n"
                    
                    messagebox.showinfo("Report Generated", report_text)
                else:
                    messagebox.showinfo("Report Generated", "No items are expiring soon")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def generate_purchase_history(self):
        """Generate purchase history report"""
        try:
            with get_connection() as conn:
                cursor = conn.execute("""
                    SELECT m.name, p.purchase_date, p.quantity, p.total_cost
                    FROM purchases p
                    JOIN medicines m ON p.medicine_id = m.id
                    ORDER BY p.purchase_date DESC
                    LIMIT 20
                """)
                
                data = cursor.fetchall()
                
                if data:
                    messagebox.showinfo("Report Generated", 
                                      f"Purchase History: {len(data)} purchases found")
                else:
                    messagebox.showinfo("Report Generated", "No purchase history found")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def export_to_csv(self, report_type):
        """Export report to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title=f"Save {report_type} as CSV"
            )
            
            if filename:
                # Generate data based on report type
                data = self.get_report_data(report_type)
                
                if data:
                    df = pd.DataFrame(data)
                    df.to_csv(filename, index=False)
                    messagebox.showinfo("Export Success", f"Report exported to {filename}")
                else:
                    messagebox.showwarning("Export Warning", "No data to export")
                    
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to CSV: {e}")
    
    def export_to_excel(self, report_type):
        """Export report to Excel"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title=f"Save {report_type} as Excel"
            )
            
            if filename:
                # Generate data based on report type
                data = self.get_report_data(report_type)
                
                if data:
                    df = pd.DataFrame(data)
                    df.to_excel(filename, index=False)
                    messagebox.showinfo("Export Success", f"Report exported to {filename}")
                else:
                    messagebox.showwarning("Export Warning", "No data to export")
                    
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to Excel: {e}")
    
    def export_to_pdf(self, report_type):
        """Export report to PDF"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title=f"Save {report_type} as PDF"
            )
            
            if filename:
                # Generate data based on report type
                data = self.get_report_data(report_type)
                
                if data:
                    # Create simple PDF using reportlab or matplotlib
                    from reportlab.lib.pagesizes import letter
                    from reportlab.pdfgen import canvas
                    
                    c = canvas.Canvas(filename, pagesize=letter)
                    width, height = letter
                    
                    # Title
                    c.setFont("Helvetica-Bold", 16)
                    c.drawString(50, height - 50, f"{report_type}")
                    c.setFont("Helvetica", 12)
                    c.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Data
                    y = height - 100
                    for row in data[:20]:  # Limit to first 20 rows
                        c.drawString(50, y, str(row))
                        y -= 15
                        if y < 50:
                            c.showPage()
                            y = height - 50
                    
                    c.save()
                    messagebox.showinfo("Export Success", f"Report exported to {filename}")
                else:
                    messagebox.showwarning("Export Warning", "No data to export")
                    
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to PDF: {e}")
    
    def get_report_data(self, report_type):
        """Get report data based on type"""
        try:
            with get_connection() as conn:
                if report_type == "Daily Sales Report":
                    cursor = conn.execute("""
                        SELECT s.invoice_number, c.name as customer_name, 
                               s.sale_date, s.total_amount
                        FROM sales s
                        LEFT JOIN customers c ON s.customer_id = c.id
                        WHERE date(s.sale_date) = date('now')
                        ORDER BY s.sale_date DESC
                    """)
                elif report_type == "Monthly Sales Report":
                    cursor = conn.execute("""
                        SELECT strftime('%Y-%m', sale_date) as month,
                               COUNT(*) as total_sales,
                               SUM(total_amount) as total_revenue
                        FROM sales
                        WHERE strftime('%Y-%m', sale_date) = strftime('%Y-%m', 'now')
                        GROUP BY strftime('%Y-%m', sale_date)
                    """)
                elif report_type == "Low Stock Report":
                    cursor = conn.execute("""
                        SELECT name, category, quantity, reorder_level
                        FROM medicines
                        WHERE quantity <= reorder_level
                        ORDER BY quantity ASC
                    """)
                elif report_type == "Expiry Report":
                    cursor = conn.execute("""
                        SELECT name, category, expiry_date
                        FROM medicines
                        WHERE expiry_date < date('now', '+30 days')
                        ORDER BY expiry_date ASC
                    """)
                elif report_type == "Purchase History":
                    cursor = conn.execute("""
                        SELECT m.name, p.purchase_date, p.quantity, p.total_cost
                        FROM purchases p
                        JOIN medicines m ON p.medicine_id = m.id
                        ORDER BY p.purchase_date DESC
                        LIMIT 20
                    """)
                else:
                    return []
                
                return cursor.fetchall()
                
        except Exception as e:
            print(f"Error getting report data: {e}")
            return []
