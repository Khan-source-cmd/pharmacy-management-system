"""
Dashboard View - EXACT screenshot #2
KPI Cards + Sales Chart + Recent Sales Table
"""
import tkinter as tk
from tkinter import ttk
from config.theme import THEME, FONTS
from components.card import DashboardCards
from components.table import DataTableWidget
import sqlite3
from config.database import get_connection

class DashboardView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=THEME['card_bg'])
        self.setup_dashboard()
        self.load_dashboard_data()
    
    def setup_dashboard(self):
        """Create complete dashboard matching screenshot #2"""
        
        # Page title
        title_frame = tk.Frame(self, bg=THEME['card_bg'])
        title_frame.pack(fill='x', pady=(20, 30))
        
        title = tk.Label(title_frame, text="Dashboard", 
                        font=('Segoe UI', 24, 'bold'),
                        fg=THEME['text_primary'], bg=THEME['card_bg'])
        title.pack()
        
        subtitle = tk.Label(title_frame, text="Welcome back! Here's what's happening with your pharmacy.",
                          font=FONTS['body'], fg=THEME['text_secondary'], 
                          bg=THEME['card_bg'])
        subtitle.pack(pady=(5, 30))
        
        # KPI Cards row (EXACT screenshot layout)
        kpi_section = tk.Frame(self, bg=THEME['card_bg'])
        kpi_section.pack(fill='x', pady=(0, 30))
        self.kpi_cards = DashboardCards(kpi_section)
        
        # Main content row - Chart (left) + Recent Sales (right)
        main_row = tk.Frame(self, bg=THEME['card_bg'])
        main_row.pack(fill='both', expand=True)
        
        # Left: Sales Overview Chart (60% width)
        chart_frame = tk.Frame(main_row, bg='#F0F2F5', relief='solid', bd=1)
        chart_frame.pack(side='left', fill='both', expand=True, padx=(0, 20))
        
        tk.Label(chart_frame, text="Sales Overview", font=FONTS['subtitle'],
                fg=THEME['text_primary'], bg='white').pack(pady=(20, 10))
        tk.Label(chart_frame, text="This week's sales trend", font=FONTS['small'],
                fg=THEME['text_secondary'], bg='white').pack(pady=(0, 20))
        
        # Chart placeholder (matplotlib will replace this)
        self.chart_canvas = tk.Canvas(chart_frame, bg='white', height=300, relief='solid', bd=1)
        self.chart_canvas.pack(pady=20, padx=20, fill='both', expand=True)
        
        # Generate sample chart
        self.draw_sales_chart()
        
        # Right: Recent Sales Table (40% width)
        sales_frame = tk.Frame(main_row, bg='#F0F2F5', relief='solid', bd=1)
        sales_frame.pack(side='right', fill='both')
        
        tk.Label(sales_frame, text="Recent Sales", font=FONTS['subtitle'],
                fg=THEME['text_primary'], bg='white').pack(pady=(20, 10), anchor='w', padx=20)
        self.sales_subtitle = tk.Label(sales_frame, text="Loading sales data...", font=FONTS['small'],
                                     fg=THEME['text_secondary'], bg='white')
        self.sales_subtitle.pack(pady=(0, 20), anchor='w', padx=20)
        
        # Recent sales table
        columns = ["Customer", "Date", "Amount"]
        self.sales_table = DataTableWidget(sales_frame, "Recent Sales", columns, [])
        self.sales_table.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
    def load_dashboard_data(self):
        """Load real data for dashboard"""
        try:
            # Load KPI data
            self.kpi_cards.load_kpi_data()
            self.kpi_cards.setup_cards()
            
            # Load recent sales data
            self.load_recent_sales()
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
    
    def load_recent_sales(self):
        """Load recent sales data"""
        try:
            with get_connection() as conn:
                cursor = conn.execute("""
                    SELECT s.invoice_number, 
                           COALESCE(c.name, 'Walk-in Customer') as customer_name,
                           s.sale_date, s.total_amount
                    FROM sales s
                    LEFT JOIN customers c ON s.customer_id = c.id
                    ORDER BY s.sale_date DESC
                    LIMIT 5
                """)
                
                sales_data = []
                for row in cursor.fetchall():
                    sales_data.append({
                        'Customer': row[1],
                        'Date': row[2][:10],  # Just date part
                        'Amount': f"₹{row[3]:.2f}"
                    })
                
                if sales_data:
                    self.sales_table.set_data(sales_data)
                    self.sales_subtitle.config(text=f"You made {len(sales_data)} sales recently.")
                else:
                    self.sales_subtitle.config(text="No sales found.")
                    
        except Exception as e:
            print(f"Error loading recent sales: {e}")
            self.sales_subtitle.config(text="Error loading sales data.")
    
    def draw_sales_chart(self):
        """Draw sales chart using matplotlib"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import numpy as np
            from datetime import datetime, timedelta
            
            # Clear any existing canvas content
            self.chart_canvas.delete("all")
            
            # Create figure with proper DPI and size
            fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
            fig.patch.set_facecolor('#F0F2F5')
            ax.set_facecolor('#F0F2F5')
            
            # Get sales data for the last 7 days
            dates = []
            sales_data = []
            
            for i in range(7):
                date = datetime.now() - timedelta(days=i)
                dates.append(date.strftime('%b %d'))
                
                # Get sales for this date
                with get_connection() as conn:
                    cursor = conn.execute("""
                        SELECT COALESCE(SUM(total_amount), 0) as daily_sales
                        FROM sales 
                        WHERE date(sale_date) = date(?, 'localtime')
                    """, (date.strftime('%Y-%m-%d'),))
                    
                    result = cursor.fetchone()
                    sales_data.append(result[0] if result[0] else 0)
            
            # Reverse to show oldest first
            dates.reverse()
            sales_data.reverse()
            
            # Create bar chart with better styling
            bars = ax.bar(range(len(dates)), sales_data, color='#1AAE4A', alpha=0.8, 
                         edgecolor='white', linewidth=1)
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height + max(sales_data)*0.05,
                           f'₹{int(height)}', ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            # Customize chart
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels(dates, fontsize=9, fontweight='bold')
            ax.set_ylabel('Sales (₹)', fontsize=10, color='#2c3e50', fontweight='bold')
            ax.set_title('Sales Overview - Last 7 Days', fontsize=12, fontweight='bold', color='#2c3e50')
            
            # Remove y-axis ticks and labels
            ax.set_yticks([])
            ax.set_yticklabels([])
            
            # Remove spines
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            # Add grid with better styling
            ax.grid(True, color='#d5dbdb', linestyle='-', alpha=0.3, axis='y')
            
            # Set y-axis limits for better visualization
            max_sales = max(sales_data) if sales_data else 1
            ax.set_ylim(0, max_sales * 1.2)
            
            plt.tight_layout()
            
            # Embed in tkinter with proper cleanup
            if hasattr(self, '_chart_canvas_widget'):
                self._chart_canvas_widget.destroy()
            
            canvas = FigureCanvasTkAgg(fig, self.chart_canvas)
            canvas.draw()
            self._chart_canvas_widget = canvas.get_tk_widget()
            self._chart_canvas_widget.pack(fill='both', expand=True)
            
            # Keep reference to prevent garbage collection
            self._chart_canvas = canvas
            
        except Exception as e:
            print(f"Error drawing chart: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to simple text
            self.chart_canvas.create_text(150, 100, text="Chart loading...", 
                                        font=('Segoe UI', 12), fill='#7f8c8d')
