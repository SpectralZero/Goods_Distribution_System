# ui/record_import.py


"""

>>>>>>     UI screen for manually recording imported goods into the system.
 *** Allows the user to input quantity, unit price (fetched from DB), import date, 
***  source (customer/place), and desired selling price.

 >>>> Validates and stores import data in the database for sales and inventory tracking.


 !!!! maybe delete it ??? if sales screen is enough (REMEMBER JIMMIE :))

"""
import logging
import tkinter
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image


from core.session import get_session
from core.db_manager import get_connection
from utils.constants import BG_DEFAULT


BG_PATH = BG_DEFAULT


def record_import_screen(parent):
    ctk.set_appearance_mode("Dark")
    session = get_session()
    role = session.get("role", "USER")

    if role not in ("ADMIN", "STAFF"):
        messagebox.showerror("Access Denied", "You do not have permission to record imports.")
        return

    # Create a top-level window attached to the parent
    window = ctk.CTkToplevel(parent)
    window.title("Record Import (Warehouse)")
    window.geometry("500x700")
    window.resizable(False, False)

    # Attempt to load and display a background image
    try:
        bg_image = ctk.CTkImage(
            dark_image=Image.open(BG_PATH).resize((500, 700)),
            size=(500, 700)
        )
        bg_label = ctk.CTkLabel(master=window, image=bg_image, text="", fg_color="transparent")
        bg_label.place(x=0, y=0)
    except Exception as e:
        logging.warning(f"Background error: {e}")
        bg_label = ctk.CTkLabel(master=window, text="", fg_color="transparent")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Create a frame for input widgets
    frame = ctk.CTkFrame(master=bg_label, width=320, height=450, corner_radius=15)
    frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    ctk.CTkLabel(frame, text="Record New Import", font=("Century Gothic", 22)).pack(pady=(20, 10))

    # Load the list of goods from the central goods table
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM goods")
            goods = cursor.fetchall()
    except Exception as e:
        logging.error(f"Error loading goods: {e}")
        goods = []

    goods_names = [f"{g[0]} - {g[1]}" for g in goods]
    selected_good = tkinter.StringVar(value=goods_names[0] if goods_names else "")

    ctk.CTkLabel(frame, text="Select Good", font=("Century Gothic", 14)).pack(pady=5)
    goods_menu = ctk.CTkOptionMenu(frame, variable=selected_good, values=goods_names)
    goods_menu.pack(pady=5)

    # Input fields for import details
    qty_var = tkinter.StringVar()
    date_var = tkinter.StringVar()
    place_var = tkinter.StringVar()
    cost_var = tkinter.StringVar()
    price_var = tkinter.StringVar()  # New selling price (if update is needed)

    inputs = [
        ("Quantity", qty_var),
        ("Unit Price", price_var),
        ("Import Date (YYYY-MM-DD)", date_var),
        ("Import Place", place_var),
        ("Import Cost", cost_var),
    ]

    for label_text, var in inputs:
        ctk.CTkLabel(frame, text=label_text, font=("Century Gothic", 14)).pack(pady=(10, 0))
        ctk.CTkEntry(frame, textvariable=var, width=220).pack(pady=5)

    def submit_import():
        try:
            # Extract good information from the "id - name" string
            good_data = selected_good.get().split(" - ")
            good_id = int(good_data[0])
            good_name = " - ".join(good_data[1:]).strip()
            price = float(price_var.get())
            quantity = int(qty_var.get())
            import_date = date_var.get().strip()
            import_place = place_var.get().strip()
            import_cost = float(cost_var.get())
        except Exception:
            messagebox.showerror("Error", "Invalid input. Please ensure all fields are filled correctly.")
            return

        if not import_date or not import_place:
            messagebox.showerror("Error", "Import Date and Import Place are required.")
            return

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                # update the central warehouse goods quantity (adding the imported amount) 
                cursor.execute("UPDATE goods SET quantity = quantity + ? WHERE id = ?", (quantity, good_id))
                
                # update the selling price 
                cursor.execute("UPDATE goods SET price = ? WHERE id = ?", (price, good_id))
                
                # Record the import transaction in the imported_goods table
                cursor.execute("""
                    INSERT INTO imported_goods (good_name, price, quantity, import_date, import_place, import_cost)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (good_name, price, quantity, import_date, import_place, import_cost))
                conn.commit()
                messagebox.showinfo("Success", "Import recorded and warehouse quantity updated.")
                # Clear the fields after success
                for var in (qty_var, date_var, place_var, cost_var, price_var):
                    var.set("")
        except Exception as e:
            logging.error(f"Error recording import: {e}")
            messagebox.showerror("Error", "Failed to record import.")

    ctk.CTkButton(frame, text="Record Import", command=submit_import).pack(pady=20)


# must return to main 
    def go_back():
        window.destroy()
        parent.deiconify()

    ctk.CTkButton(frame, text="Back", command=go_back).pack(pady=(0, 20))

    window.mainloop()
