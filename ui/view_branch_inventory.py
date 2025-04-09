# ui/view_branch_inventory.py


"""
------------------------
Displays a detailed inventory for each branch.
Combines data from branches and goods to show current stock levels.
tracking distribution efficiency and stock management across locations.

Done!!
------------------------
"""


import logging
import tkinter
import customtkinter as ctk
from PIL import Image
from tkinter import ttk, messagebox

from core.db_manager import get_connection
from core.session import get_session
from utils.constants import BG_DEFAULT

BG_PATH = BG_DEFAULT

def view_branch_inventory_screen(parent):
    """
    A Toplevel screen listing all branch_inventories records.
    """
    ctk.set_appearance_mode("Dark")

    session = get_session()
    role = session.get("role", "USER")
    # Could restrict if desired
    # if role not in ("ADMIN", "STAFF"):          delete button!!! 
    #     messagebox.showerror("Access Denied", "You do not have permission to view branch inventories.")
    #     return

    window = ctk.CTkToplevel(parent)
    window.title("Branch Inventory")
    window.geometry("700x600")
    window.resizable(False, False)

    # Background
    try:
        bg_image = ctk.CTkImage(
            dark_image=Image.open(BG_PATH).resize((700, 600)),
            size=(700, 600)
        )
        bg_label = ctk.CTkLabel(master=window, image=bg_image, text="", fg_color="transparent")
        bg_label.place(x=0, y=0)
    except Exception as e:
        logging.warning(f"Could not load background image: {e}")

    frame = ctk.CTkFrame(window, width=650, height=500, corner_radius=15)
    frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    title_label = ctk.CTkLabel(frame, text="Branch Inventories", font=("Century Gothic", 24))
    title_label.pack(pady=10)

    # Table area
    table_frame = ctk.CTkFrame(frame, width=600, height=350, corner_radius=10)
    table_frame.pack(pady=5)

    style = ttk.Style()
    style.configure("Inventory.Treeview", font=("Century Gothic", 10), rowheight=25)
    style.configure("Inventory.Treeview.Heading", font=("Century Gothic", 11, "bold"))

    columns = ("branch_id", "good_id", "quantity")
    tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="Inventory.Treeview")
    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=150, anchor=tkinter.CENTER)
    tree.pack(fill=tkinter.BOTH, expand=True)

    # Fetch data
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT bi.branch_id, b.name AS branch_name, bi.good_id, g.name AS good_name, bi.quantity
                FROM branch_inventories bi
                JOIN branches b ON bi.branch_id = b.id
                JOIN goods g ON bi.good_id = g.id
            """
            cursor.execute(query)
            rows = cursor.fetchall()  # (branch_id, branch_name, good_id, good_name, quantity)

        # Insert into table
        for row in rows:
            # Display format: branch_id => branch_name, good_id => good_name
            display_branch = f"{row[0]} - {row[1]}"
            display_good = f"{row[2]} - {row[3]}"
            quantity = row[4]
            tree.insert("", tkinter.END, values=(display_branch, display_good, quantity))

    except Exception as e:
        logging.error(f"Error fetching branch inventory: {e}")
        messagebox.showerror("Error", "Could not fetch branch inventory data.")

    def go_back():
        window.destroy()
        parent.deiconify()

    back_button = ctk.CTkButton(frame, text="Back", corner_radius=6, command=go_back)
    back_button.pack(pady=10)

    window.mainloop()
