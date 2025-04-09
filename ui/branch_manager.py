# ui/branch_manager.py

"""
{{Branch management interface for ADMIN users.}}
>> Allows viewing, adding, editing, and deleting branch records.
>>  Accessible by ADMIN role. (Remember if this must be in admin only or not >>) i have to check this later and handle it.
"""


import tkinter
import customtkinter as ctk
from tkinter import messagebox, simpledialog
from core.branch_handler import get_all_branches, add_branch, edit_branch, delete_branch_record
from core.session import get_session

class BranchManagerScreen:
    def __init__(self, parent):
        self.parent = parent
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Branch Manager")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        self.session = get_session()
        if self.session["role"] != "ADMIN":
            messagebox.showerror("Access Denied", "You do not have permission to manage branches.")
            self.window.destroy()
            return
        self.build_ui()
        self.refresh_branches()

    def build_ui(self):
        # Main container frame
        self.frame = ctk.CTkFrame(master=self.window, width=380, height=480, corner_radius=15)
        self.frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        self.title_label = ctk.CTkLabel(self.frame, text="Branch Manager", font=("Century Gothic", 24))
        self.title_label.pack(pady=(20, 10))
        
        # Scrollable frame for displaying branches
        self.branch_list_frame = ctk.CTkScrollableFrame(self.frame, width=340, height=220, corner_radius=10)
        self.branch_list_frame.pack(pady=10)
        
        # Action buttons
        self.add_button = ctk.CTkButton(self.frame, text="Add Branch", command=self.add_branch)
        self.add_button.pack(pady=5)
        self.edit_button = ctk.CTkButton(self.frame, text="Edit Branch", command=self.edit_branch)
        self.edit_button.pack(pady=5)
        self.delete_button = ctk.CTkButton(self.frame, text="Delete Branch", command=self.delete_branch)
        self.delete_button.pack(pady=5)
        self.refresh_button = ctk.CTkButton(self.frame, text="Refresh Branches", command=self.refresh_branches)
        self.refresh_button.pack(pady=5)
        self.back_button = ctk.CTkButton(self.frame, text="Back", command=self.go_back)
        self.back_button.pack(pady=5)

    def refresh_branches(self):
        # Clear existing branch labels
        for widget in self.branch_list_frame.winfo_children():
            widget.destroy()
        branches = get_all_branches()
        for branch in branches:
            branch_label = ctk.CTkLabel(
                self.branch_list_frame,
                text=f"{branch[0]} - {branch[1]} - {branch[2]}",
                font=("Century Gothic", 14)
            )
            branch_label.pack(pady=2, padx=2, anchor="w")

    def add_branch(self):
        name = simpledialog.askstring("New Branch", "Enter branch name:")
        location = simpledialog.askstring("New Branch", "Enter branch location:")
        if not name or not location:
            messagebox.showwarning("Warning", "Branch name/location cannot be empty.")
            return
        success = add_branch(name, location)
        if success:
            messagebox.showinfo("Success", "Branch added successfully!")
            self.refresh_branches()
        else:
            messagebox.showerror("Error", "Failed to add branch. Check logs.")

    def edit_branch(self):
        branch_id = simpledialog.askinteger("Edit Branch", "Enter branch ID to edit:")
        if not branch_id:
            return
        name = simpledialog.askstring("Edit Branch", "Enter new branch name:")
        location = simpledialog.askstring("Edit Branch", "Enter new branch location:")
        if not name or not location:
            messagebox.showwarning("Warning", "Branch name/location cannot be empty.")
            return
        success = edit_branch(branch_id, name, location)
        if success:
            messagebox.showinfo("Success", "Branch updated successfully!")
            self.refresh_branches()
        else:
            messagebox.showerror("Error", "Failed to update branch. Check logs.")

    def delete_branch(self):
        branch_id = simpledialog.askinteger("Delete Branch", "Enter branch ID to delete:")
        if not branch_id:
            return
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this branch?")
        if confirm:
            success = delete_branch_record(branch_id)
            if success:
                messagebox.showinfo("Success", "Branch deleted successfully!")
                self.refresh_branches()
            else:
                messagebox.showerror("Error", "Failed to delete branch. Check logs.")

    def go_back(self):
        self.window.destroy()
        self.parent.deiconify()

# Test usage: 
# if __name__ == "__main__":
#     root = ctk.CTk()
#     BranchManagerScreen(root)
#     root.mainloop()
