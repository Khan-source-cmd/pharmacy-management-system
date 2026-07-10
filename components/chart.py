#!/usr/bin/env python3
"""
Modern Chart Component for PyQt6
Matplotlib integration for dashboard charts
"""
import sys
import os
# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

from config.theme import MODERN_COLORS
from database.modern_db import get_sales_summary, get_recent_sales

# Set matplotlib style
plt.style.use('default')


class ModernChartWidget(QWidget):
    """Modern chart widget with matplotlib integration"""
    
    def __init__(self, parent=None, title="Chart", chart_type="bar"):
        super().__init__(parent)
        self.title = title
        self.chart_type = chart_type
        
        # Setup matplotlib
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        
        self.setup_ui()
        self.setup_chart()
    
    def setup_ui(self):
        """Setup the chart UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with title and controls
        header_layout = QHBoxLayout()
        
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {MODERN_COLORS['text_primary']};")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addWidget(self.canvas)
    
    def setup_chart(self):
        """Setup the matplotlib chart"""
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        
        # Set colors
        self.figure.patch.set_facecolor(MODERN_COLORS['bg_primary'])
        self.ax.set_facecolor(MODERN_COLORS['bg_primary'])
        
        # Remove spines
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        
        # Set grid
        self.ax.grid(True, color=MODERN_COLORS['bg_secondary'], linestyle='-', alpha=0.5)
        
        # Set colors for text
        self.ax.tick_params(colors=MODERN_COLORS['text_secondary'])
        self.ax.xaxis.label.set_color(MODERN_COLORS['text_secondary'])
        self.ax.yaxis.label.set_color(MODERN_COLORS['text_secondary'])
        
        # Draw sample data
        self.draw_sample_chart()
    
    def draw_sample_chart(self):
        """Draw sample sales chart"""
        # Sample data
        dates = [datetime.now() - timedelta(days=i) for i in range(7)]
        dates.reverse()
        
        # Generate some sample sales data
        np.random.seed(42)
        sales_data = np.random.randint(50, 200, 7)
        
        # Create the chart
        if self.chart_type == "bar":
            bars = self.ax.bar(range(len(dates)), sales_data, color=MODERN_COLORS['primary'], alpha=0.8)
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                           f'₹{height}', ha='center', va='bottom',
                           fontfamily='Segoe UI', fontsize=9, color=MODERN_COLORS['text_primary'])
        
        elif self.chart_type == "line":
            line = self.ax.plot(range(len(dates)), sales_data, color=MODERN_COLORS['primary'], 
                              linewidth=3, marker='o', markersize=6)
            
            # Add value labels
            for i, value in enumerate(sales_data):
                self.ax.annotate(f'₹{value}', (i, value), textcoords="offset points", 
                               xytext=(0,10), ha='center',
                               fontfamily='Segoe UI', fontsize=9, color=MODERN_COLORS['text_primary'])
        
        # Format x-axis
        self.ax.set_xticks(range(len(dates)))
        self.ax.set_xticklabels([d.strftime('%b %d') for d in dates], fontfamily='Segoe UI', fontsize=9)
        
        # Format y-axis
        self.ax.set_ylabel('Sales (₹)', fontfamily='Segoe UI', fontsize=10, color=MODERN_COLORS['text_secondary'])
        
        # Remove y-axis ticks
        self.ax.set_yticks([])
        
        # Set title
        self.ax.set_title(self.title, fontfamily='Segoe UI', fontsize=12, fontweight='bold', 
                         color=MODERN_COLORS['text_primary'], pad=20)
        
        # Tight layout
        self.figure.tight_layout()
        self.canvas.draw()
    
    def update_chart(self, data):
        """Update chart with new data"""
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        
        # Setup styling again
        self.figure.patch.set_facecolor(MODERN_COLORS['bg_primary'])
        self.ax.set_facecolor(MODERN_COLORS['bg_primary'])
        
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        
        self.ax.grid(True, color=MODERN_COLORS['bg_secondary'], linestyle='-', alpha=0.5)
        self.ax.tick_params(colors=MODERN_COLORS['text_secondary'])
        
        # Draw with actual data
        if self.chart_type == "bar" and 'sales_data' in data:
            dates = data['dates']
            sales = data['sales_data']
            
            bars = self.ax.bar(range(len(dates)), sales, color=MODERN_COLORS['primary'], alpha=0.8)
            
            for i, bar in enumerate(bars):
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                           f'₹{int(height)}', ha='center', va='bottom',
                           fontfamily='Segoe UI', fontsize=9, color=MODERN_COLORS['text_primary'])
            
            self.ax.set_xticks(range(len(dates)))
            self.ax.set_xticklabels([d.strftime('%b %d') for d in dates], 
                                  fontfamily='Segoe UI', fontsize=9)
            self.ax.set_ylabel('Sales (₹)', fontfamily='Segoe UI', fontsize=10, 
                             color=MODERN_COLORS['text_secondary'])
        
        elif self.chart_type == "line" and 'sales_data' in data:
            dates = data['dates']
            sales = data['sales_data']
            
            line = self.ax.plot(range(len(dates)), sales, color=MODERN_COLORS['primary'], 
                              linewidth=3, marker='o', markersize=6)
            
            for i, value in enumerate(sales):
                self.ax.annotate(f'₹{int(value)}', (i, value), textcoords="offset points", 
                               xytext=(0,10), ha='center',
                               fontfamily='Segoe UI', fontsize=9, color=MODERN_COLORS['text_primary'])
            
            self.ax.set_xticks(range(len(dates)))
            self.ax.set_xticklabels([d.strftime('%b %d') for d in dates], 
                                  fontfamily='Segoe UI', fontsize=9)
            self.ax.set_ylabel('Sales (₹)', fontfamily='Segoe UI', fontsize=10, 
                             color=MODERN_COLORS['text_secondary'])
        
        self.ax.set_title(self.title, fontfamily='Segoe UI', fontsize=12, fontweight='bold', 
                         color=MODERN_COLORS['text_primary'], pad=20)
        
        self.figure.tight_layout()
        self.canvas.draw()


class SalesChartWidget(ModernChartWidget):
    """Specialized sales chart widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "Sales Overview", "bar")
        self.load_sales_data()
    
    def load_sales_data(self):
        """Load actual sales data from database"""
        try:
            # Get recent sales data
            recent_sales = get_recent_sales(7)
            
            if recent_sales:
                # Process data for chart
                dates = []
                sales_data = []
                
                # Group by date
                sales_by_date = {}
                for sale in recent_sales:
                    date_str = sale['sale_date'][:10]  # Get date part only
                    if date_str not in sales_by_date:
                        sales_by_date[date_str] = 0
                    sales_by_date[date_str] += sale['total_amount']
                
                # Sort by date
                sorted_dates = sorted(sales_by_date.keys())
                
                for date_str in sorted_dates:
                    dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
                    sales_data.append(sales_by_date[date_str])
                
                # Update chart
                self.update_chart({
                    'dates': dates,
                    'sales_data': sales_data
                })
            else:
                # Use sample data if no real data
                self.draw_sample_chart()
                
        except Exception as e:
            print(f"Error loading sales data: {e}")
            self.draw_sample_chart()


class InventoryChartWidget(ModernChartWidget):
    """Specialized inventory chart widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "Inventory Status", "bar")
        self.load_inventory_data()
    
    def load_inventory_data(self):
        """Load inventory data for chart"""
        try:
            # Get medicines data
            from database.modern_db import get_medicines
            medicines = get_medicines()
            
            if medicines:
                # Group by category
                categories = {}
                for med in medicines:
                    category = med['category']
                    if category not in categories:
                        categories[category] = 0
                    categories[category] += med['quantity']
                
                # Prepare data for chart
                labels = list(categories.keys())
                values = list(categories.values())
                
                # Create pie chart instead of bar for inventory
                self.figure.clear()
                self.ax = self.figure.add_subplot(111)
                
                # Setup styling
                self.figure.patch.set_facecolor(MODERN_COLORS['bg_primary'])
                self.ax.set_facecolor(MODERN_COLORS['bg_primary'])
                
                # Create pie chart
                colors = [MODERN_COLORS['primary'], MODERN_COLORS['secondary'], 
                         MODERN_COLORS['warning'], MODERN_COLORS['success'], 
                         MODERN_COLORS['danger']]
                
                wedges, texts, autotexts = self.ax.pie(values, labels=labels, autopct='%1.1f%%',
                                                     colors=colors[:len(labels)],
                                                     startangle=90)
                
                # Style text
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontfamily('Segoe UI')
                    autotext.set_fontsize(9)
                    autotext.set_fontweight('bold')
                
                for text in texts:
                    text.set_fontfamily('Segoe UI')
                    text.set_fontsize(9)
                    text.set_color(MODERN_COLORS['text_primary'])
                
                self.ax.set_title("Inventory by Category", fontfamily='Segoe UI', 
                                fontsize=12, fontweight='bold', 
                                color=MODERN_COLORS['text_primary'], pad=20)
                
                self.figure.tight_layout()
                self.canvas.draw()
            else:
                self.draw_sample_chart()
                
        except Exception as e:
            print(f"Error loading inventory data: {e}")
            self.draw_sample_chart()


class DashboardChart(ModernChartWidget):
    """Main dashboard chart combining multiple metrics"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "Performance Metrics", "line")
        self.load_dashboard_data()
    
    def load_dashboard_data(self):
        """Load dashboard metrics data"""
        try:
            # Get sales summary
            summary = get_sales_summary(30)  # Last 30 days
            
            # Generate trend data for the last 7 days
            dates = [datetime.now() - timedelta(days=i) for i in range(7)]
            dates.reverse()
            
            # Generate sample trend data based on summary
            base_value = summary['total_revenue'] / 30 if summary['total_revenue'] > 0 else 100
            trend_data = [base_value + np.random.randint(-20, 30) for _ in range(7)]
            
            self.update_chart({
                'dates': dates,
                'sales_data': trend_data
            })
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            self.draw_sample_chart()