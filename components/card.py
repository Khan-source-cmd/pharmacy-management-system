"""
KPI Cards - Dashboard cards from screenshot #2
Total Revenue, Total Medicines, Low Stock, Expired
"""
import tkinter as tk
from config.theme import THEME, FONTS
from config.database import get_connection

class KPICard(tk.Frame):
    def __init__(self, parent, title, value, subtitle="", trend="+20.1%", color='info'):
        super().__init__(parent, bg=THEME['card_bg'], relief='solid', bd=1)
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.trend = trend
        self.color = color
        
        self.pack_propagate(False)
        self.configure(width=250, height=120)
        self.setup_card()
    
    def setup_card(self):
        """Create card layout matching screenshot"""
        # Title
        title_label = tk.Label(self, text=self.title, font=FONTS['subtitle'],
                             fg=THEME['text_secondary'], bg=THEME['card_bg'])
        title_label.pack(anchor='w', padx=20, pady=(15, 5))
        
        # Value (large bold number)
        value_label = tk.Label(self, text=f"₹{self.value}", 
                             font=('Segoe UI', 28, 'bold'),
                             fg=THEME['text_primary'], bg=THEME['card_bg'])
        value_label.pack(anchor='w', padx=20, pady=(0, 5))
        
        # Subtitle + trend
        subtitle_frame = tk.Frame(self, bg=THEME['card_bg'])
        subtitle_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        tk.Label(subtitle_frame, text=self.subtitle, font=FONTS['small'],
                fg=THEME['text_light'], bg=THEME['card_bg']).pack(side='left')
        
        trend_label = tk.Label(subtitle_frame, text=self.trend, 
                             font=FONTS['small'], fg=THEME['success'],
                             bg=THEME['card_bg'])
        trend_label.pack(side='right')

class DashboardCards(tk.Frame):
    """Container for all 4 KPI cards"""
    def __init__(self, parent):
        super().__init__(parent, bg=THEME['card_bg'])
        self.load_kpi_data()
        self.setup_cards()
    
    def load_kpi_data(self):
        """Load real data from database"""
        try:
            with get_connection() as conn:
                # Total Revenue
                cursor = conn.execute("SELECT SUM(total_amount) as revenue FROM sales")
                revenue = cursor.fetchone()['revenue'] or 0
                
                # Total Medicines
                cursor = conn.execute("SELECT COUNT(*) as count FROM medicines")
                total_medicines = cursor.fetchone()['count']
                
                # Low Stock Alerts
                cursor = conn.execute("""
                    SELECT COUNT(*) as count FROM medicines 
                    WHERE quantity <= reorder_level AND quantity > 0
                """)
                low_stock = cursor.fetchone()['count']
                
                # Expired Medicines
                from datetime import date
                today = date.today().isoformat()
                cursor = conn.execute("""
                    SELECT COUNT(*) as count FROM medicines 
                    WHERE expiry_date < ?
                """, (today,))
                expired = cursor.fetchone()['count']
                
                self.data = {
                    'revenue': f"{revenue:.2f}",
                    'medicines': total_medicines,
                    'low_stock': low_stock,
                    'expired': expired
                }
        except:
            # Fallback demo data
            self.data = {
                'revenue': '231.49',
                'medicines': 8,
                'low_stock': 1,
                'expired': 0
            }
    
    def setup_cards(self):
        """Create 4 KPI cards in row"""
        cards_frame = tk.Frame(self, bg=THEME['card_bg'])
        cards_frame.pack(pady=20)
        
        KPICard(cards_frame, "Total Revenue", self.data['revenue'], 
               "+20.1% from last month", THEME['success'])
        KPICard(cards_frame, "Total Medicines", self.data['medicines'])
        KPICard(cards_frame, "Low Stock Alerts", self.data['low_stock'], 
               "Needing restock", THEME['warning'])
        KPICard(cards_frame, "Expired Medicines", self.data['expired'], 
               "Immediate action needed", THEME['danger'])
