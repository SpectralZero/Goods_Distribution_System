# ui/distribute_goods.py

# UI screen that handles distribution of goods from the warehouse or branches
# to other branches. Includes stock checking, dropdown selectors for goods/branches,
# and input validation. Connected to distribution handler logic.
#
# Jamal alqbail

import logging
import tkinter
import customtkinter as ctk
from tkinter import messagebox


from core.distribution_handler import distribute_goods, get_stock
from core.branch_handler import get_all_branches
from core.db_manager import get_connection  # for goods retrieval
from core.session import get_session

class DistributeGoodsScreen:
    def __init__(self, parent):
        self.parent = parent
        self.session = get_session()
        # if self.session["role"] not in ("ADMIN", "STAFF"):
        #     messagebox.showerror("Access Denied", "You do not have permission to distribute goods.")
        #     return
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Distribute Goods")
        self.window.geometry("600x650")
        self.window.resizable(False, False)
        self.build_ui()
    
    def build_ui(self):
        self.frame = ctk.CTkFrame(self.window, width=580, height=600, corner_radius=15)
        self.frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        
        self.title_label = ctk.CTkLabel(self.frame, text="Distribute Goods", font=("Century Gothic", 24))
        self.title_label.pack(pady=10)
        
        # Source branch dropdown (Warehouse as option)
        branches = get_all_branches()
        branch_options = ["Warehouse (None)"] + [f"{b[0]} - {b[1]}" for b in branches]
        self.source_var = tkinter.StringVar(value=branch_options[0])
        ctk.CTkLabel(self.frame, text="Source (Warehouse/Branch)", font=("Century Gothic", 14)).pack(pady=5)
        self.source_menu = ctk.CTkOptionMenu(self.frame, variable=self.source_var, values=branch_options)
        self.source_menu.pack(pady=5)
        
        # Destination branch dropdown (should not include Warehouse)
        dest_options = [f"{b[0]} - {b[1]}" for b in branches]
        self.dest_var = tkinter.StringVar(value=dest_options[0] if dest_options else "")
        ctk.CTkLabel(self.frame, text="Destination Branch", font=("Century Gothic", 14)).pack(pady=5)
        self.dest_menu = ctk.CTkOptionMenu(self.frame, variable=self.dest_var, values=dest_options)
        self.dest_menu.pack(pady=5)
        
        # Goods dropdown
        goods = self.get_goods_list()
        self.goods_options = [f"{g[0]} - {g[1]}" for g in goods]
        self.good_var = tkinter.StringVar(value=self.goods_options[0] if self.goods_options else "")
        ctk.CTkLabel(self.frame, text="Select Good", font=("Century Gothic", 14)).pack(pady=5)
        self.good_menu = ctk.CTkOptionMenu(self.frame, variable=self.good_var, values=self.goods_options)
        self.good_menu.pack(pady=5)
        
        # Quantity entry
        ctk.CTkLabel(self.frame, text="Quantity to Distribute", font=("Century Gothic", 14)).pack(pady=5)
        self.qty_var = tkinter.StringVar(value="1")
        self.qty_entry = ctk.CTkEntry(self.frame, textvariable=self.qty_var, width=200)
        self.qty_entry.pack(pady=5)
        
        # Stock display label
        self.stock_label = ctk.CTkLabel(self.frame, text="Available Stock: N/A", font=("Century Gothic", 14))
        self.stock_label.pack(pady=5)
        
        # Check Stock button
        self.check_stock_button = ctk.CTkButton(self.frame, text="Check Stock", command=self.check_stock)
        self.check_stock_button.pack(pady=5)
        
        # Distribute button
        self.distribute_button = ctk.CTkButton(self.frame, text="Distribute", command=self.do_distribute)
        self.distribute_button.pack(pady=10)
        
        # Back button
        self.back_button = ctk.CTkButton(self.frame, text="Back", command=self.go_back)
        self.back_button.pack(pady=5)
    
    def get_goods_list(self):
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM goods")
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error fetching goods: {e}")
            return []
    
    def check_stock(self):
        src_text = self.source_var.get()
        good_text = self.good_var.get()
        if not good_text:
            messagebox.showerror("Error", "Select a good.")
            return
        good_id = int(good_text.split(" - ")[0])
        if src_text.startswith("Warehouse"):
            stock_info = get_stock(good_id)
        else:
            branch_id = int(src_text.split(" - ")[0])
            stock_info = get_stock(good_id, branch_id)
        if stock_info["success"]:
            self.stock_label.configure(text=f"Available Stock: {stock_info['stock']}")
        else:
            self.stock_label.configure(text="Available Stock: N/A")
            messagebox.showerror("Error", f"Could not retrieve stock: {stock_info.get('reason', '')}")
    
    def do_distribute(self):
        src_text = self.source_var.get()
        good_text = self.good_var.get()
        dest_text = self.dest_var.get()
        if not good_text or not dest_text:
            messagebox.showerror("Error", "Select both good and destination branch.")
            return
        good_id = int(good_text.split(" - ")[0])
        if src_text.startswith("Warehouse"):
            from_branch_id = None
        else:
            from_branch_id = int(src_text.split(" - ")[0])
        to_branch_id = int(dest_text.split(" - ")[0])
        try:
            quantity = int(self.qty_var.get())
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer.")
            return
        result = distribute_goods(good_id, from_branch_id, to_branch_id, quantity, self.session.get("user_id", 0))
        if result["success"]:
            messagebox.showinfo("Success", "Goods distributed successfully!")
        else:
            reason = result.get("reason", "Distribution failed.")
            available = result.get("available", "N/A")
            messagebox.showerror("Error", f"Distribution failed: {reason}\nAvailable: {available}")
    
    def go_back(self):
        self.window.destroy()
        self.parent.deiconify()

# if need test,  usage:
# if __name__ == "__main__":
#     root = ctk.CTk()
#     DistributeGoodsScreen(root)
#     root.mainloop()
