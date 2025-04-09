# ui/add_goods.py

"""
GUI screen for adding new goods to the system. >> remember Jamal if this  must be in admin only or not >>
>> allows entry of name, quantity, and unit price.
>> checks for duplicates and updates quantity if needed.
* Accessible by ADMIN and STAFF roles. 
"""
import logging
import tkinter
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image


# internal modules 
from core.goods_handler import add_good
from core.session import get_session
from core.db_manager import get_connection
from utils.constants import BG_DEFAULT

BG_PATH = BG_DEFAULT

def add_goods_screen(parent):
    ctk.set_appearance_mode("Dark")
    session = get_session()
    role = session.get("role", "USER")

    # if role not in ("ADMIN", "STAFF"):     Delete button instead in user gui 
    #     messagebox.showerror("Access Denied", "You do not have permission to add goods.")
    #     return

    window = ctk.CTkToplevel()
    window.title("Add Goods")
    window.geometry("500x500")
    window.resizable(False, False)

    try:
        bg_image = ctk.CTkImage(
            dark_image=Image.open(BG_PATH).resize((500, 500)),
            size=(500, 500)
        )
        bg_label = ctk.CTkLabel(master=window, image=bg_image, text="", fg_color="transparent")
        bg_label.place(x=0, y=0)
    except Exception as e:
        logging.warning(f"Could not load background image: {e}")
        bg_label = ctk.CTkLabel(master=window, text="", fg_color="transparent")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    frame = ctk.CTkFrame(master=bg_label, width=300, height=380, corner_radius=15)
    frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    ctk.CTkLabel(frame, text="Add New Good", font=("Century Gothic", 22)).pack(pady=(20, 10))

    name_var = tkinter.StringVar()
    quantity_var = tkinter.StringVar()
    price_var = tkinter.StringVar()

    fields = [
        ("Name", name_var),
        ("Quantity", quantity_var),
        ("Price", price_var),
    ]

    for label_text, var in fields:
        ctk.CTkLabel(frame, text=label_text, font=("Century Gothic", 14)).pack(pady=(10, 0))
        ctk.CTkEntry(frame, textvariable=var, width=220).pack(pady=5)

    def submit_good():
        name = name_var.get().strip()
        try:
            quantity = int(quantity_var.get())
            price = float(price_var.get())
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer and Price must be a number.")
            return

        if not name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, quantity FROM goods WHERE LOWER(name) = LOWER(?)", (name,))
                row = cursor.fetchone()

                if row:
                    good_id, existing_qty = row
                    if messagebox.askyesno("Good Exists", f"'{name}' already exists with quantity {existing_qty}.\nIncrease quantity by {quantity}?"):
                        cursor.execute("UPDATE goods SET quantity = quantity + ? WHERE id = ?", (quantity, good_id))
                        conn.commit()
                        messagebox.showinfo("Updated", f"Quantity updated.\nNew Quantity: {existing_qty + quantity}")
                else:
                    success = add_good(name, quantity, price)
                    if success:
                        messagebox.showinfo("Success", "Good added successfully!")
                    else:
                        raise Exception("Failed to insert into goods table.")

                name_var.set("")
                quantity_var.set("")
                price_var.set("")

        except Exception as e:
            logging.error(f"Error adding good: {e}", exc_info=True)
            messagebox.showerror("Error", "Failed to add good. See logs.")

    add_button = ctk.CTkButton(frame, text="Add Good", width=180, command=submit_good)
    add_button.pack(pady=20)


# Back button needed in project instruction for each screen
    def go_back():
        window.destroy()
        parent.deiconify()

    back_button = ctk.CTkButton(frame, text="Back", width=180, command=go_back)
    back_button.pack(pady=(0, 20))

    window.mainloop()
