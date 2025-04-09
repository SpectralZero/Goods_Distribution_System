# main.py
import tkinter as tk
import logging
from core.session import get_session
from ui.login_screen import LoginScreen
from ui.main_menu import MainMenuScreen

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
    logging.info("Application started.")

    # Create a single root window
    root = tk.Tk()
    root.withdraw()  # Hide root initially

    # Show login screen (as Toplevel)
    login = LoginScreen(root)
    login.window.deiconify()

    # One mainloop for entire app
    root.mainloop()

    # After login Toplevel closes, check session
    session = get_session()
    if session.get("user_id") is not None:
        # Show main menu on the same root
        menu = MainMenuScreen(root)
        menu.window.deiconify()
        root.mainloop()
    else:
        logging.info("No user logged in. Exiting...")
        root.destroy()

if __name__ == "__main__":
    main()
