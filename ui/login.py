"""
Login Window - Exact replica of screenshot #1
Centered login card with MediSys logo
"""
import tkinter as tk
from tkinter import ttk
import bcrypt
from config.database import get_connection
from config.theme import THEME, FONTS
from .main_window import MainWindow

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("MediSys - Sign In")
        
        # Create main frame (centered)
        self.main_frame = tk.Frame(root, bg='white')
        self.main_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        self.setup_login_ui()
    
    def setup_login_ui(self):
        """Create login form matching screenshot"""
        # Logo section
        logo_frame = tk.Frame(self.main_frame, bg='white')
        logo_frame.pack(pady=40)
        
        logo_label = tk.Label(logo_frame, text="MediSys", 
                            font=('Segoe UI', 36, 'bold'),
                            fg=THEME['primary_green'], bg='white')
        logo_label.pack()
        
        subtitle = tk.Label(logo_frame, text="Pharmacy Management System",
                          font=FONTS['subtitle'], fg=THEME['text_secondary'], bg='white')
        subtitle.pack(pady=(0, 20))
        
        # Form frame
        form_frame = tk.Frame(self.main_frame, bg='white')
        form_frame.pack(pady=20)
        
        # Email field
        tk.Label(form_frame, text="Email", font=FONTS['heading'], 
                fg=THEME['text_primary'], bg='white').pack(anchor='w')
        self.email_var = tk.StringVar()
        email_entry = tk.Entry(form_frame, textvariable=self.email_var, 
                              font=FONTS['body'], width=30, relief='solid', bd=1)
        email_entry.pack(pady=(5, 15), fill='x', ipady=8)
        
        # Password field
        tk.Label(form_frame, text="Password", font=FONTS['heading'], 
                fg=THEME['text_primary'], bg='white').pack(anchor='w')
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(form_frame, textvariable=self.password_var, 
                                 show="*", font=FONTS['body'], width=30, 
                                 relief='solid', bd=1)
        password_entry.pack(pady=(5, 20), fill='x', ipady=8)
        password_entry.bind('<Return>', lambda e: self.login())
        
        # Sign In button (exact screenshot style)
        signin_btn = tk.Button(form_frame, text="Sign In", 
                              font=('Segoe UI', 12, 'bold'),
                              bg=THEME['primary_green'], fg='white',
                              relief='flat', cursor='hand2', height=2,
                              command=self.login)
        signin_btn.pack(fill='x', pady=10)
        signin_btn.bind('<Enter>', lambda e: signin_btn.configure(bg=THEME['hover_green']))
        signin_btn.bind('<Leave>', lambda e: signin_btn.configure(bg=THEME['primary_green']))
        
        # Focus on email
        email_entry.focus()
    
    def login(self):
        """Handle login logic"""
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()

        if not email or not password:
            self.show_error("Please enter email and password")
            return

        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    "SELECT id, password_hash, role FROM users WHERE email = ?",
                    (email,)
                )
                user = cursor.fetchone()
                
                if user and bcrypt.checkpw(password.encode(), bytes.fromhex(user['password_hash'])):
                    # Login successful - open main window
                    self.root.withdraw()  # Hide login
                    main_window = MainWindow(self.root, user)
                    self.root.deiconify()  # Show main
                else:
                    self.show_error("Invalid email or password")
        except Exception as e:
            self.show_error(f"Database error: {str(e)}")
    
    def show_error(self, message):
        """Show error message"""
        tk.messagebox.showerror("Login Error", message)
