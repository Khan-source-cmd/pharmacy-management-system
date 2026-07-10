#!/usr/bin/env python3
"""
Animation Utilities for PyQt6
Provides smooth animations and transitions for the pharmacy management system
"""

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup, QTimer, QPoint, QRect
from PyQt6.QtWidgets import QWidget, QFrame, QLabel, QPushButton, QTableWidget, QHeaderView
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtCore import Qt
import time

class AnimationManager:
    """Central animation manager for the application"""
    
    def __init__(self):
        self.animations = []
    
    def animate_widget_opacity(self, widget, start_opacity=0.0, end_opacity=1.0, duration=500):
        """Animate widget opacity from start to end"""
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(start_opacity)
        animation.setEndValue(end_opacity)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        self.animations.append(animation)
        return animation
    
    def animate_widget_position(self, widget, start_pos, end_pos, duration=500):
        """Animate widget position from start to end"""
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        self.animations.append(animation)
        return animation
    
    def animate_widget_size(self, widget, start_size, end_size, duration=500):
        """Animate widget size from start to end"""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        start_rect = QRect(start_pos, start_size) if hasattr(start_pos, '__len__') else QRect(widget.pos(), start_size)
        end_rect = QRect(end_pos, end_size) if hasattr(end_pos, '__len__') else QRect(widget.pos(), end_size)
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        self.animations.append(animation)
        return animation
    
    def animate_background_color(self, widget, start_color, end_color, duration=500):
        """Animate widget background color"""
        animation = QPropertyAnimation(widget, b"styleSheet")
        animation.setDuration(duration)
        
        # Create color transition
        start_hex = self.color_to_hex(start_color)
        end_hex = self.color_to_hex(end_color)
        
        # For smooth color transitions, we'll use a timer-based approach
        def update_color(progress):
            r = int(start_color.red() + (end_color.red() - start_color.red()) * progress)
            g = int(start_color.green() + (end_color.green() - start_color.green()) * progress)
            b = int(start_color.blue() + (end_color.blue() - start_color.blue()) * progress)
            color = QColor(r, g, b)
            widget.setStyleSheet(f"background-color: {self.color_to_hex(color)};")
        
        timer = QTimer()
        timer.timeout.connect(lambda: update_color(timer.elapsed() / duration))
        timer.start(16)  # ~60 FPS
        
        return timer
    
    def animate_button_press(self, button, duration=100):
        """Animate button press effect"""
        original_size = button.size()
        pressed_size = original_size.width() - 4, original_size.height() - 2
        
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(button.geometry())
        animation.setEndValue(QRect(button.pos(), pressed_size))
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()
        
        # Return to original size
        QTimer.singleShot(duration, lambda: self.animate_widget_size(button, pressed_size, original_size, duration))
        
        return animation
    
    def animate_table_row_highlight(self, table, row, duration=300):
        """Animate table row highlight effect"""
        if row >= table.rowCount():
            return
        
        # Store original colors
        original_colors = []
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                original_colors.append(item.foreground())
        
        # Animate highlight
        def highlight_step(progress):
            # Create a pulsing effect
            alpha = int(255 * (1 - abs(progress - 0.5) * 2))
            color = QColor(26, 174, 74, alpha)
            
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    item.setForeground(color)
        
        timer = QTimer()
        step = 0
        def update_highlight():
            nonlocal step
            progress = step / 100
            highlight_step(progress)
            step += 5
            if step > 100:
                timer.stop()
                # Restore original colors
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item and col < len(original_colors):
                        item.setForeground(original_colors[col])
        
        timer.timeout.connect(update_highlight)
        timer.start(16)  # ~60 FPS
        
        return timer
    
    def animate_kpi_counter(self, label, start_value, end_value, duration=1000):
        """Animate KPI counter from start to end value"""
        start_time = time.time()
        
        def update_counter():
            elapsed = time.time() - start_time
            progress = min(elapsed / (duration / 1000), 1.0)
            
            # Ease out cubic
            eased_progress = 1 - pow(1 - progress, 3)
            
            current_value = start_value + (end_value - start_value) * eased_progress
            
            if isinstance(end_value, int):
                label.setText(f"{int(current_value)}")
            else:
                label.setText(f"{current_value:.2f}")
            
            if progress >= 1.0:
                timer.stop()
        
        timer = QTimer()
        timer.timeout.connect(update_counter)
        timer.start(16)  # ~60 FPS
        
        return timer
    
    def animate_sidebar_toggle(self, sidebar, is_expanded, duration=300):
        """Animate sidebar expand/collapse"""
        if is_expanded:
            target_width = 250
        else:
            target_width = 60
        
        animation = QPropertyAnimation(sidebar, b"minimumWidth")
        animation.setDuration(duration)
        animation.setStartValue(sidebar.minimumWidth())
        animation.setEndValue(target_width)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        
        return animation
    
    def animate_page_transition(self, old_widget, new_widget, duration=300):
        """Animate page transition with fade effect"""
        # Fade out old widget
        if old_widget:
            self.animate_widget_opacity(old_widget, 1.0, 0.0, duration // 2)
        
        # Fade in new widget
        if new_widget:
            new_widget.setWindowOpacity(0.0)
            new_widget.show()
            self.animate_widget_opacity(new_widget, 0.0, 1.0, duration // 2)
        
        return True
    
    def animate_chart_loading(self, chart_widget, duration=800):
        """Animate chart loading effect"""
        # Create a loading overlay
        overlay = QWidget(chart_widget)
        overlay.setGeometry(chart_widget.rect())
        overlay.setStyleSheet("background-color: rgba(255, 255, 255, 0.8); border-radius: 8px;")
        overlay.show()
        
        # Animate overlay fade out
        self.animate_widget_opacity(overlay, 1.0, 0.0, duration)
        
        # Remove overlay after animation
        QTimer.singleShot(duration, overlay.deleteLater)
        
        return overlay
    
    def animate_search_filter(self, table, duration=200):
        """Animate search filter effect on table"""
        # Create a subtle highlight effect
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    # Store original style
                    original_font = item.font()
                    
                    # Create animation effect
                    animation = QPropertyAnimation(item, b"font")
                    animation.setDuration(duration)
                    animation.setStartValue(original_font)
                    
                    # Temporarily make font bold
                    bold_font = QFont(original_font)
                    bold_font.setBold(True)
                    animation.setEndValue(bold_font)
                    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                    animation.start()
                    
                    # Return to normal
                    QTimer.singleShot(duration, lambda f=original_font, i=item: i.setFont(f))
    
    def animate_status_change(self, label, old_status, new_status, duration=300):
        """Animate status label change"""
        # Flash effect
        original_style = label.styleSheet()
        
        # Quick flash to white
        label.setStyleSheet("background-color: white; color: black; padding: 2px 8px; border-radius: 4px;")
        
        # Animate back to new status color
        QTimer.singleShot(100, lambda: self.animate_background_color(
            label, 
            QColor("white"), 
            self.get_status_color(new_status),
            duration
        ))
    
    def get_status_color(self, status):
        """Get color for status"""
        from config.theme import MODERN_COLORS
        if status.lower() in ['low', 'warning', 'near expiry']:
            return QColor(MODERN_COLORS['warning'])
        elif status.lower() in ['critical', 'expired', 'out of stock']:
            return QColor(MODERN_COLORS['danger'])
        else:
            return QColor(MODERN_COLORS['success'])
    
    def color_to_hex(self, color):
        """Convert QColor to hex string"""
        return f"#{color.red():02x}{color.green():02x}{color.blue():02x}"
    
    def cleanup(self):
        """Clean up all animations"""
        for animation in self.animations:
            if animation:
                animation.stop()
        self.animations.clear()

class HoverEffects:
    """Hover effect utilities"""
    
    @staticmethod
    def add_hover_effect(widget, hover_color="#f8f9fa", normal_color="#ffffff"):
        """Add hover effect to widget"""
        widget.enterEvent = lambda event: widget.setStyleSheet(f"background-color: {hover_color};")
        widget.leaveEvent = lambda event: widget.setStyleSheet(f"background-color: {normal_color};")
    
    @staticmethod
    def add_button_hover_effect(button, hover_scale=1.05):
        """Add hover effect to button with scaling"""
        original_size = button.size()
        
        def mouse_enter(event):
            new_size = original_size * hover_scale
            button.resize(new_size)
        
        def mouse_leave(event):
            button.resize(original_size)
        
        button.enterEvent = mouse_enter
        button.leaveEvent = mouse_leave

class LoadingAnimations:
    """Loading animation utilities"""
    
    @staticmethod
    def create_loading_spinner(parent, size=20):
        """Create a simple loading spinner"""
        spinner = QLabel(parent)
        spinner.setFixedSize(size, size)
        spinner.setStyleSheet(f"""
            border: 2px solid {parent.palette().color(QPalette.ColorRole.Light)};
            border-top: 2px solid #1AAE4A;
            border-radius: {size//2}px;
        """)
        
        def rotate():
            current_rotation = getattr(spinner, '_rotation', 0)
            new_rotation = (current_rotation + 10) % 360
            spinner._rotation = new_rotation
            spinner.setStyleSheet(f"""
                border: 2px solid {parent.palette().color(QPalette.ColorRole.Light)};
                border-top: 2px solid #1AAE4A;
                border-radius: {size//2}px;
                qproperty-rotation: {new_rotation}deg;
            """)
        
        timer = QTimer()
        timer.timeout.connect(rotate)
        timer.start(50)
        
        return spinner, timer

# Global animation manager instance
animation_manager = AnimationManager()