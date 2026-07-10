"""
Predictive Stock - Sidebar item for admin
"""
import tkinter as tk
from config.theme import THEME, FONTS

class PredictiveView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=THEME['card_bg'])
        self.setup_predictive()
    
    def setup_predictive(self):
        """Predictive stock analysis"""
        title = tk.Label(self, text="Predictive Stock", font=('Segoe UI', 24, 'bold'),
                        fg=THEME['text_primary'], bg=THEME['card_bg'])
        title.pack(pady=(30, 10))
        
        subtitle = tk.Label(self, text="Estimate future stock requirements based on past sales.",
                           font=FONTS['body'], fg=THEME['text_secondary'], bg=THEME['card_bg'])
        subtitle.pack(pady=(0, 40))
        
        info_label = tk.Label(self, text="🔮 Advanced analytics coming soon!\n\n" +
                             "This feature will predict stock needs based on:\n" +
                             "• Sales velocity\n• Seasonal trends\n• Lead times",
                             font=FONTS['body'], fg=THEME['text_secondary'], 
                             bg=THEME['card_bg'], justify='center')
        info_label.pack(expand=True)
