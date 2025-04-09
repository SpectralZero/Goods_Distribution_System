# ui/login_screen.py

# UI Module: Contains the login screen class and related GUI logic.

# - Uses bcrypt-based authentication from auth.py.
#   3 times login failed, the program closes.
# -  validation and error feedback.



import logging
import customtkinter as ctk
import tkinter
from tkinter import messagebox
from PIL import Image


from core.auth import authenticate_user, register_user
from core.session import set_session
from utils.style_utils import apply_theme
from utils.constants import BG_DEFAULT

BG_PATH = BG_DEFAULT

apply_theme() # darrk or light mode GUI

class LoginScreen:
    """
    >> login/registration window for user authentication.
    """

    def __init__(self,root):
        # Configure CustomTkinter theme.
        ctk.set_default_color_theme("dark-blue")  # can be changed to any built-in theme
        # Appearance can be toggled to "light" or "system" as well
        ctk.set_appearance_mode("dark")

        self.window = ctk.CTkToplevel()
        self.window.title("Sign In")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        self.window.withdraw()

        # In a real application, you might pass in a shared DB connection or a service.
        self.attempts = 0
        self._login_window()

    def _login_window(self, event=None) -> None:
        """
        Creates the login window with background image and input widgets.

        """
        self.window.title("Sign In")
        self.window.bind('<Return>', self._login)

        # Background image
        try:
            bg_image = ctk.CTkImage(
                dark_image=Image.open(BG_PATH).resize((500, 600)),
                size=(500, 600)
            )
            bg_label = ctk.CTkLabel(master=self.window, image=bg_image, text="")
            bg_label.place(x=0, y=0)
        except Exception as e:
            logging.warning(f"Could not load background image 'bg.jpg': {e}")
            # Fallback: just create a regular background color
            bg_label = ctk.CTkLabel(master=self.window, text="")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Main frame
        self.frame = ctk.CTkFrame(
            master=bg_label,
            width=320,
            height=360,
            corner_radius=15
        )
        self.frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        # Title label
        self.login_label = ctk.CTkLabel(
            master=self.frame,
            text="Log in",
            font=('Century Gothic', 30)
        )
        self.login_label.place(x=100, y=45)

        # Username entry
        self.username_entry = ctk.CTkEntry(
            master=self.frame,
            width=220,
            placeholder_text='Username'
        )
        self.username_entry.place(x=50, y=110)

        # Password entry
        self.password_entry = ctk.CTkEntry(
            master=self.frame,
            width=220,
            placeholder_text='Password',
            show="*"
        )
        self.password_entry.place(x=50, y=165)

        # Toggle link to switch from login to register
        self.toggle_link = ctk.CTkLabel(
            master=self.frame,
            text="Don't have an account? Register",
            font=('Century Gothic', 13),
            cursor="hand2"
        )
        self.toggle_link.place(x=50, y=210)
        self.toggle_link.bind("<Button-1>", self._register_window)

        # Login button
        login_button = ctk.CTkButton(
            master=self.frame,
            width=220,
            text="Login",
            corner_radius=6,
            command=self._login
        )
        login_button.place(x=50, y=250)

    def _register_window(self, event=None) -> None:
        """
        Switches the frame UI to display the registration window.
        """
        self.window.title("Create an account")
        self.window.unbind('<Return>')
        self.window.bind('<Return>', self._register)

        self.login_label.configure(text="Register")
        self.toggle_link.configure(text="Already have an account? Sign in")
        self.toggle_link.bind("<Button-1>", self._login_window)

        # Update button to call the register method
        register_button = ctk.CTkButton(
            master=self.frame,
            width=220,
            text="Create Account",
            corner_radius=6,
            command=self._register
        )
        register_button.place(x=50, y=250)

    def _login(self, event=None) -> None:
        """
        Authenticates the user by checking the provided username and password.
        Sets session if successful, otherwise shows an error.
        """
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Basic validation
        if not username or not password:
            messagebox.showerror("Login Error", "Username and password must not be empty.")
            return

        # Attempt to authenticate
        user_row = authenticate_user(username, password)
        if user_row:
            user_id, role = user_row
            set_session(user_id, role)
            logging.info(f"User '{username}' logged in successfully. Role = {role}")
            self.window.quit()
            self.window.destroy()
            
        else:
            self.attempts += 1
            logging.warning(f"Login failed for user '{username}': Invalid credentials")
            messagebox.showerror("Login Failed", f"Invalid credentials ({self.attempts}/3)")
            if self.attempts >= 3:
                messagebox.showerror("Access Denied", "Maximum attempts reached. The system will close.")
                self.window.destroy()

    def _register(self, event=None) -> None:
        
       #registers a new user by inserting them into the DB (hashed password).
       
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Validate input
        if not username or not password:
            messagebox.showerror("Error", "Username/Password cannot be empty.")
            return
        if len(username) > 20 or len(password) > 50:
            messagebox.showerror("Error", "Username/Password is too long.")
            return

        success, msg = register_user(username, password)
        if success:
            logging.info(f"User '{username}' registered successfully.")
            messagebox.showinfo("Success", "Account created successfully!")
            # Clear the entry fields
            self.username_entry.delete(0, tkinter.END)
            self.password_entry.delete(0, tkinter.END)
            # Switch back to login window
            self._login_window()
            # Don't destroy the window - just bring it to front
            self.window.deiconify()
            
        else:
            logging.warning(f"Registration failed for user '{username}': {msg}")
            messagebox.showerror("Error", msg)
