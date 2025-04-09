# ui/main_menu.py
"""
MAIN MENU screen shown after successful login.   
>>>> Loads (user-specific options) and role-based navigation (Admin, Staff).
# Integrates CustomTkinter sidebar, theme toggling, and routing to all app modules.

 central hub for managing goods, branches, distributions, sales, and settings.  differ by role (ADMIN, STAFF, USER)
"""
import logging
import customtkinter as ctk
import tkinter
from PIL import Image
from typing import List, Tuple, Any  
from core.session import get_session
from utils.constants import BG_DARK
from utils.style_utils import apply_theme, toggle_theme, get_bg_image_path

BG_PATH = BG_DARK

apply_theme()

class MainMenuScreen:
    def __init__(self, root):
        self.root = root
        self.window = ctk.CTkToplevel(self.root)
        self.window.title("Main Menu")
        self.window.geometry("1350x740")
        self.window.resizable(False, False)
        self.window.withdraw()  # Hidden until .deiconify()

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.bg_label = None
        self.frame = None
        self.pil_image = None
        self.bg_image = None

        self._build_ui()
        self.side_menu()
        self._load_buttons()

    def update_background(self):
        try:
            bg_image = Image.open(get_bg_image_path()).resize((1350, 740))
            self.bg_image = ctk.CTkImage(dark_image=bg_image, size=(1350, 740))
            self.bg_label.configure(image=self.bg_image)
            self.bg_label.lower()  # Send background to back
        except Exception as e:
            logging.warning(f"Error updating background: {e}")

    def toggle_theme_gui(self):
        toggle_theme()
        self.update_background()
        self.side_menu()
       

    def _build_ui(self):
        try:
            self.pil_image = Image.open(BG_PATH).resize((1350, 740))
            self.bg_image = ctk.CTkImage(dark_image=self.pil_image, size=(1350, 740))
            self.bg_label = ctk.CTkLabel(
                master=self.window,
                image=self.bg_image,
                text="",
                fg_color="transparent"
            )
            self.bg_label.place(x=0, y=0)
        except Exception as e:
            logging.warning(f"Could not load background image at '{BG_PATH}': {e}")
            self.bg_label = ctk.CTkLabel(master=self.window, text="", fg_color="transparent")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.frame = ctk.CTkFrame(
            master=self.bg_label,
            width=360,
            height=610,
            corner_radius=12
        )
        self.frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    def side_menu(self):
        session = get_session()
        role = session.get("role", "USER")

        # Destroy existing sidebar if it exists
        if hasattr(self, 'sidebar'):
            self.sidebar.destroy()

        # Create new sidebar
        self.sidebar = ctk.CTkFrame(self.window, corner_radius=0, width=250)
        self.sidebar.pack(side="left", fill="y")

        # Theme switch - preserve its state
        current_theme = ctk.get_appearance_mode()
        self.theme_switch = ctk.CTkSwitch(
            master=self.sidebar, 
            text="Dark Mode", 
            command=self.toggle_theme_gui
        )
        self.theme_switch.pack(pady=20, padx=20)
        self.theme_switch.select() if current_theme == "Dark" else self.theme_switch.deselect()

        if role in ("ADMIN", "STAFF"):
            from utils.style_utils import get_theme_colors
            colors = get_theme_colors()

            nav_buttons: List[Tuple[str, Any]] = [
                ("View Goods", self._open_view_goods),
                ("View Branch Inventory", self._open_view_branch_inventory),
                ("Statistics", self._open_statistics)
            ]
            
            for text, command in nav_buttons:
                ctk.CTkButton(
                    master=self.sidebar,
                    text=text,
                    width=210,
                    height=159,
                    font=("Century Gothic", 18, "bold"),
                    fg_color=colors['fg'],
                    hover_color=colors['hover'],
                    text_color=colors['text'],
                    anchor="center",
                    command=command
                ).pack(pady=3, padx=3, anchor="center")

    def _load_buttons(self):
        session = get_session()
        role = session.get("role", "USER")

        title_label = ctk.CTkLabel(
            self.frame,
            fg_color="transparent",
            text=f"Welcome!\nYour role: {role}",
            font=("Century Gothic", 20)
        )
        title_label.place(x=80, y=20)

        y = 100
        def add_button(text, command):
            nonlocal y
            ctk.CTkButton(
                master=self.frame,
                text=text,
                font=("Century Gothic", 16),
                fg_color="#171717",
                hover_color="#838383",
                anchor="center",
                width=260,
                height=40,
                corner_radius=8,
                command=command
            ).place(x=50, y=y)
            y += 50

        if role == "ADMIN":
            add_button("Branch Manager", self._open_branch_manager)

        if role in ("ADMIN", "STAFF"):
            add_button("Distribute Goods", self._open_distribute_goods)
            add_button("Add Goods", self._open_add_goods)
            
            add_button("Sale Items", self._open_record_sale)
            # add_button("View Imported Goods", self._open_view_imported_goods)          moved to sidebar!!! 
            add_button("Record Import", self._open_record_import)
        if role == "USER":    
            add_button("Distribute Goods", self._open_distribute_goods)    
            add_button("Add Goods", self._open_add_goods)               
            add_button("View Goods", self._open_view_goods)               
            add_button("View Branch Inventory", self._open_view_branch_inventory)         
        add_button("Settings", self._open_settings)


# Function to navigate to a new screen 
    def _navigate(self, child_class):
        self.window.withdraw()
        # Instantiate the new screen passing self.window as the parent.
        self.window.after(10, lambda: child_class(self.window))

    def _open_branch_manager(self):
        from ui.branch_manager import BranchManagerScreen
        self._navigate(BranchManagerScreen)

    def _open_add_goods(self):
        from ui.add_goods import add_goods_screen  
        self._navigate(add_goods_screen)

    def _open_distribute_goods(self):
        from ui.distribute_goods import DistributeGoodsScreen
        self._navigate(DistributeGoodsScreen)

    def _open_record_sale(self):
        from ui.sales_screen import RecordSaleScreen
        self._navigate(RecordSaleScreen)

    def _open_view_imported_goods(self):
        from ui.view_goods import ViewGoodsScreen  
        self._navigate(ViewGoodsScreen)

    def _open_record_import(self):
        from ui.record_import import record_import_screen  
        self._navigate(record_import_screen)

    def _open_view_goods(self):
        from ui.view_goods import ViewGoodsScreen  
        self._navigate(ViewGoodsScreen)

    def _open_view_branch_inventory(self):
        from ui.view_branch_inventory import view_branch_inventory_screen  
        self._navigate(view_branch_inventory_screen)

    def _open_statistics(self):
        from ui.statistics import StatisticsScreen  
        self._navigate(StatisticsScreen)

    def _open_settings(self):
        from ui.settings import settings_screen  
        self._navigate(settings_screen)


# if __name__ == "__main__":
#     root = ctk.CTk()
#     MainMenuScreen(root)
#     root.mainloop()
