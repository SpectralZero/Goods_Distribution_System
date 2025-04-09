# ui/view_goods.py

"""
----------------*****------------------
>>>> GUI for viewing and managing warehouse goods.
>>>> Supports adding new items, editing details, deleting records, and refreshing inventory.
>> Used for tracking available stock before distribution.

"""
import logging
import tkinter
import customtkinter as ctk
from tkinter import messagebox, ttk, simpledialog
from PIL import Image

#internal modules
from core.goods_handler import add_good, get_all_goods
from core.db_manager import update_good, delete_good
from core.session import get_session
from utils.constants import BG_WAREHOUSE

BG_PATH = BG_WAREHOUSE

class ViewGoodsScreen:
    def __init__(self, parent):
        self.parent = parent
        self.session = get_session()
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Warehouse Goods Inventory")
        self.window.geometry("800x740")
        self.window.resizable(False, False)
        self.build_ui()
        self.refresh_goods()
    
    def build_ui(self):
        # Main container frame
        self.frame = ctk.CTkFrame(self.window, width=780, height=580, corner_radius=10)
        self.frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        
        # adding a Warehouse Logo at the top , Bepragrammer.org 
        try:
            warehouse_logo = ctk.CTkImage(
                dark_image=Image.open(BG_PATH).resize((600, 220)),
                size=(600, 220)
            )
            self.logo_label = ctk.CTkLabel(self.frame, image=warehouse_logo, text="")
            self.logo_label.image = warehouse_logo  # keep a reference
            self.logo_label.pack(pady=(10, 0))
        except Exception as e:
            logging.warning(f"Could not load warehouse logo image: {e}")
        
       
        self.title_label = ctk.CTkLabel(self.frame, text="Warehouse Goods Inventory", font=("Century Gothic", 24))
        self.title_label.pack(pady=10)
        
        # Treeview for goods display
        self.tree_frame = ctk.CTkFrame(self.frame, width=760, height=400)
        self.tree_frame.pack(pady=10)
        
        self.goods_tree = ttk.Treeview(self.tree_frame, columns=("ID", "Name", "Quantity", "Price"), show='headings', height=15)
        self.goods_tree.heading("ID", text="ID")
        self.goods_tree.heading("Name", text="Name")
        self.goods_tree.heading("Quantity", text="Quantity")
        self.goods_tree.heading("Price", text="Price")
        
        self.goods_tree.column("ID", width=50, anchor=tkinter.CENTER)
        self.goods_tree.column("Name", width=300, anchor=tkinter.W)
        self.goods_tree.column("Quantity", width=150, anchor=tkinter.CENTER)
        self.goods_tree.column("Price", width=150, anchor=tkinter.CENTER)
        
        self.goods_tree.pack(fill=tkinter.BOTH, expand=True)
        
        # Buttons for Add, Edit, Delete, Refresh, and Back
        button_frame = ctk.CTkFrame(self.frame, width=760, height=50)
        button_frame.pack(pady=10)
        
        self.add_button = ctk.CTkButton(button_frame, text="Add Good", command=self.add_good)
        self.add_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.edit_button = ctk.CTkButton(button_frame, text="Edit Good", command=self.edit_good)
        self.edit_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.delete_button = ctk.CTkButton(button_frame, text="Delete Good", command=self.delete_good)
        self.delete_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.refresh_button = ctk.CTkButton(button_frame, text="Refresh", command=self.refresh_goods)
        self.refresh_button.grid(row=0, column=3, padx=5, pady=5)
        
        self.back_button = ctk.CTkButton(button_frame, text="Back", command=self.go_back)
        self.back_button.grid(row=0, column=4, padx=5, pady=5)
    
    def refresh_goods(self):
        # Clear existing entries in tree
        for item in self.goods_tree.get_children():
            self.goods_tree.delete(item)
        # Get goods from the database (warehouse goods)
        goods = get_all_goods()
        for good in goods:
            self.goods_tree.insert("", "end", values=good)
    
    def add_good(self):
        name = simpledialog.askstring("Add Good", "Enter product name:")
        if not name:
            messagebox.showwarning("Warning", "Name cannot be empty.")
            return
        try:
            quantity = int(simpledialog.askstring("Add Good", "Enter quantity:"))
            price = float(simpledialog.askstring("Add Good", "Enter price:"))
        except (TypeError, ValueError):
            messagebox.showerror("Error", "Invalid quantity or price.")
            return
        
        success = add_good(name, quantity, price)
        if success:
            messagebox.showinfo("Success", "Good added successfully!")
        else:
            messagebox.showerror("Error", "Failed to add good. It might already exist.")
        self.refresh_goods()
    
    def edit_good(self):
        selected = self.goods_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a good to edit.")
            return
        values = self.goods_tree.item(selected, "values")
        good_id = int(values[0])
        current_name = values[1]
        current_price = values[3]
        new_name = simpledialog.askstring("Edit Good", "Enter new name:", initialvalue=current_name)
        if not new_name:
            messagebox.showwarning("Warning", "Name cannot be empty.")
            return
        try:
            new_price = float(simpledialog.askstring("Edit Good", "Enter new price:", initialvalue=current_price))
        except (TypeError, ValueError):
            messagebox.showerror("Error", "Invalid price.")
            return
        
        success = update_good(good_id, new_name, new_price)
        if success:
            messagebox.showinfo("Success", "Good updated successfully!")
        else:
            messagebox.showerror("Error", "Failed to update good.")
        self.refresh_goods()
    
    def delete_good(self):
        selected = self.goods_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a good to delete.")
            return
        values = self.goods_tree.item(selected, "values")
        good_id = int(values[0])
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this good?")
        if confirm:
            success = delete_good(good_id)
            if success:
                messagebox.showinfo("Success", "Good deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete good.")
            self.refresh_goods()
    
    def go_back(self):
        self.window.destroy()
        self.parent.deiconify()


# if __name__ == "__main__":
#     root = ctk.CTk()
#     ViewGoodsScreen(root)
#     root.mainloop()
