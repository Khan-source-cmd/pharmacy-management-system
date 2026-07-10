"""
CSV/Excel/PDF Export utilities (per synopsis requirements)
"""
import csv
import pandas as pd
from datetime import datetime

class ExportUtils:
    @staticmethod
    def export_to_csv(data, columns, filename=None):
        """Export table data to CSV"""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(data)
        return filename
    
    @staticmethod
    def export_to_excel(data, columns, filename=None):
        """Export table data to Excel"""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        df = pd.DataFrame(data, columns=columns)
        df.to_excel(filename, index=False)
        return filename

# Example usage:
# ExportUtils.export_to_csv([['John', '₹45.75']], ['Name', 'Amount'], 'sales.csv')
