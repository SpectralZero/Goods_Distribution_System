# ui/sales_screen.py


# This is the sales recording interface.
# Users can select a branch, pick a good, specify quantity and price, 
# and record a sale directly to the database.
#
# Also performs stock validation and ensures real-time sales tracking. that's it.

import logging
import tkinter
import customtkinter as ctk
from tkinter import messagebox



from core.sales_handler import record_sale
from core.branch_handler import get_all_branches
from core.goods_handler import get_all_goods, get_good_unit_price  # get_good_unit_price 
from core.distribution_handler import get_stock
from core.session import get_session

class RecordSaleScreen:
    def __init__(self, parent):
        self.parent = parent
        self.session = get_session()
        if self.session["role"] not in ("ADMIN", "STAFF"):
            messagebox.showerror("Access Denied", "You do not have permission to record sales.")
            return
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Record Sale")
        self.window.geometry("550x650")  # increased height for additional info
        self.window.resizable(False, False)
        self.build_ui()
    
    def build_ui(self):
        self.frame = ctk.CTkFrame(self.window, width=500, height=600, corner_radius=15)
        self.frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        
        self.title_label = ctk.CTkLabel(self.frame, text="Record Sale", font=("Century Gothic", 24))
        self.title_label.pack(pady=10)
        
        # Branch selection 
        branches = get_all_branches()
        branch_options = [f"{b[0]} - {b[1]}" for b in branches]
        self.branch_var = tkinter.StringVar(value=branch_options[0] if branch_options else "")
        ctk.CTkLabel(self.frame, text="Select Branch", font=("Century Gothic", 14)).pack(pady=5)
        self.branch_menu = ctk.CTkOptionMenu(self.frame, variable=self.branch_var, values=branch_options)
        self.branch_menu.pack(pady=5)
        
        # Goods selection 
        goods = get_all_goods()
        good_options = [f"{g[0]} - {g[1]}" for g in goods]
        self.good_var = tkinter.StringVar(value=good_options[0] if good_options else "")
        ctk.CTkLabel(self.frame, text="Select Good", font=("Century Gothic", 14)).pack(pady=5)
        self.good_menu = ctk.CTkOptionMenu(self.frame, variable=self.good_var, values=good_options, command=self.update_unit_price)
        self.good_menu.pack(pady=5)
        
        # Display the unit price fetched from the DB; this reflects how much it costs (or the sale price)
        self.unit_price_label = ctk.CTkLabel(self.frame, text="Unit Price: N/A", font=("Century Gothic", 14))
        self.unit_price_label.pack(pady=5)
        
        # Entry for quantity to sell
        ctk.CTkLabel(self.frame, text="Quantity to Sell", font=("Century Gothic", 14)).pack(pady=5)
        self.qty_var = tkinter.StringVar(value="1")
        self.qty_entry = ctk.CTkEntry(self.frame, textvariable=self.qty_var, width=200)
        self.qty_entry.pack(pady=5)
        
        # Label to display available stock in the selected branch
        self.stock_label = ctk.CTkLabel(self.frame, text="Available Stock: N/A", font=("Century Gothic", 14))
        self.stock_label.pack(pady=5)
        
        # Button to check available stock
        self.check_stock_button = ctk.CTkButton(self.frame, text="Check Stock", command=self.check_stock)
        self.check_stock_button.pack(pady=5)
        
        # TODo: Add a Customer field if you later choose to record customer details with a sale.
        ctk.CTkLabel(self.frame, text="Customer (optional)", font=("Century Gothic", 14)).pack(pady=5)
        self.customer_var = tkinter.StringVar()
        self.customer_entry = ctk.CTkEntry(self.frame, textvariable=self.customer_var, width=200)
        self.customer_entry.pack(pady=5)
        
        # Button to record the sale
        self.sale_button = ctk.CTkButton(self.frame, text="Record Sale", command=self.record_sale)
        self.sale_button.pack(pady=10)
        
        # Back button to close this screen and return to the parent
        self.back_button = ctk.CTkButton(self.frame, text="Back", command=self.go_back)
        self.back_button.pack(pady=5)
        
        # Initialize unit price display for the selected good
        self.update_unit_price(self.good_var.get())
    
    def update_unit_price(self, good_str):
        """Fetches the unit price of the selected good from the DB and displays it."""
        try:
            good_id = int(good_str.split(" - ")[0])
            unit_price = get_good_unit_price(good_id)
            if unit_price is not None:
                self.unit_price_label.configure(text=f"Unit Price: {unit_price:.2f}")
            else:
                self.unit_price_label.configure(text="Unit Price: N/A")
        except Exception as e:
            logging.error(f"Error updating unit price: {e}")
            self.unit_price_label.configure(text="Unit Price: N/A")
    
    def check_stock(self):
        branch_str = self.branch_var.get()
        good_str = self.good_var.get()
        if not branch_str or not good_str:
            messagebox.showerror("Error", "Select both branch and good.")
            return
        try:
            branch_id = int(branch_str.split(" - ")[0])
            good_id = int(good_str.split(" - ")[0])
        except Exception as e:
            messagebox.showerror("Error", "Invalid branch or good selection.")
            return
        
        stock_info = get_stock(good_id, branch_id)
        if stock_info["success"]:
            self.stock_label.configure(text=f"Available Stock: {stock_info['stock']}")
        else:
            self.stock_label.configure(text="Available Stock: N/A")
            messagebox.showerror("Error", f"Could not retrieve stock: {stock_info.get('reason', '')}")
    
    def record_sale(self):
        branch_str = self.branch_var.get()
        good_str = self.good_var.get()
        if not branch_str or not good_str:
            messagebox.showerror("Error", "Select both branch and good.")
            return
        
        try:
            branch_id = int(branch_str.split(" - ")[0])
            good_id = int(good_str.split(" - ")[0])
            quantity = int(self.qty_var.get())
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer.")
            return
        
        # Customer input is optional; extend record_sale() in sales_handler to store this if needed or keep it for now if not .
        customer = self.customer_var.get().strip()  
        result = record_sale(good_id, branch_id, quantity, self.session.get("user_id", 0))
        if result["success"]:
            messagebox.showinfo("Success", "Sale recorded successfully!")
            self.qty_var.set("1")
            self.check_stock()
        else:
            reason = result.get("reason", "Sale failed.")
            available = result.get("available", "N/A")
            messagebox.showerror("Error", f"Sale failed: {reason}\nAvailable: {available}")
    
    def go_back(self):
        self.window.destroy()
        self.parent.deiconify()
