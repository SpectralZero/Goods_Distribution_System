# ui/settings.py
"""
Tkinter-based settings screen with user management and password controls.
For regular users: shows change password form.
For ADMIN users: shows user list (with bcrypt-hashed passwords), add/delete user controls,
and a form to update the admin's own password.
Uses bcrypt for password hashing and verification.
"""
import logging
import tkinter
import customtkinter as ctk
from PIL import Image
from tkinter import ttk, messagebox
import bcrypt

from core.session import get_session
from core.db_manager import get_connection
from utils.constants import BG_DEFAULT

bg_path = BG_DEFAULT

def hash_password(password):
    """Hash a password using bcrypt and return the hashed password as a string."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def refresh_user_list(tree):
    """Refresh the user list in the treeview"""
    for item in tree.get_children():
        tree.delete(item)
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, password, role FROM users")
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)
    except Exception as e:
        logging.error(f"Failed to load user accounts: {e}", exc_info=True)


# back later to fix the error >>> password not updated in db,  1 hour work 
def create_password_change_frame(parent, is_admin=False):
    """Create a password change form.
    
    If is_admin is True, the title reads 'Change Admin Password'.
    The same function updates the password for the current user.
    """
    frame = ctk.CTkFrame(parent)
    
    title = "Change Admin Password" if is_admin else "Change Your Password"
    ctk.CTkLabel(frame, text=title, font=("Arial", 14)).pack(pady=5)
    
    current_pass = ctk.CTkEntry(frame, placeholder_text="Current Password", show="*", width=200)
    current_pass.pack(pady=5)
    
    new_pass = ctk.CTkEntry(frame, placeholder_text="New Password", show="*", width=200)
    new_pass.pack(pady=5)
    
    confirm_pass = ctk.CTkEntry(frame, placeholder_text="Confirm New Password", show="*", width=200)
    confirm_pass.pack(pady=5)
    
    def handle_password_change():
        session = get_session()
        username = session.get("username")
        current = current_pass.get()
        new = new_pass.get()
        confirm = confirm_pass.get()
        
        if not all([current, new, confirm]):
            messagebox.showerror("Error", "All fields are required")
            return
            
        if new != confirm:
            messagebox.showerror("Error", "New passwords don't match")
            return
            
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                # Get the stored hashed password for current user
                cursor.execute("SELECT password FROM users WHERE username=?", (username,))
                result = cursor.fetchone()
                if not result:
                    messagebox.showerror("Error", "User not found")
                    return
                    
                stored_hash = result[0]
                if not bcrypt.checkpw(current.encode('utf-8'), stored_hash.encode('utf-8')):
                    messagebox.showerror("Error", "Incorrect current password")
                    return
                    
                new_hash = hash_password(new)
                cursor.execute("UPDATE users SET password=? WHERE username=?", (new_hash, username))
                conn.commit()
                messagebox.showinfo("Success", "Password updated successfully")
                current_pass.delete(0, "end")
                new_pass.delete(0, "end")
                confirm_pass.delete(0, "end")
                
        except Exception as e:
            logging.error(f"Password change failed: {e}", exc_info=True)
            messagebox.showerror("Error", "Failed to update password")

    ctk.CTkButton(frame, text="Submit", command=handle_password_change,
                  font=("Arial", 16),
                  fg_color="transparent",
                  hover_color="#212121",
                  anchor="center",
                  width=200,
                  height=40,
                  corner_radius=8
                 ).pack(pady=10)
    return frame

def settings_screen(parent):
    ctk.set_appearance_mode("Dark")

    window = ctk.CTkToplevel()
    window.title("Settings")
    window.geometry("600x650")
    window.resizable(False, False)

    try:
        bg_image = ctk.CTkImage(
            dark_image=Image.open(bg_path).resize((600, 650)),
            size=(600, 650)
        )
        bg_label = ctk.CTkLabel(master=window, image=bg_image, text="", fg_color="transparent")
        bg_label.place(x=0, y=0)
    except Exception as e:
        logging.warning(f"Could not load background image: {e}")
        bg_label = ctk.CTkLabel(master=window, text="", fg_color="transparent")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    main_frame = ctk.CTkFrame(master=bg_label, width=550, height=600, corner_radius=15)
    main_frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    ctk.CTkLabel(main_frame, text="Settings", font=("Arial", 20)).pack(pady=10)

    role = get_session().get("role", "USER")
    current_user = get_session().get("username")

    if role == "ADMIN":
        # User Management Section
        management_frame = ctk.CTkFrame(main_frame)
        management_frame.pack(pady=10, fill="x", padx=20)

        ctk.CTkLabel(management_frame, text="User Management", font=("Arial", 14)).pack(pady=5)

        # User List
        tree = ttk.Treeview(management_frame, columns=("Username", "Hashed Password", "Role"), show='headings', height=4)
        tree.heading("Username", text="Username")
        tree.heading("Hashed Password", text="Hashed Password")
        tree.heading("Role", text="Role")
        tree.column("Username", width=120)
        tree.column("Hashed Password", width=200)
        tree.column("Role", width=80)
        tree.pack(pady=5, fill="x")
        refresh_user_list(tree)

        # Add User Section
        add_frame = ctk.CTkFrame(management_frame)
        add_frame.pack(pady=5, fill="x")

        new_user_entry = ctk.CTkEntry(add_frame, placeholder_text="Username", width=150)
        new_user_entry.pack(side="left", padx=5)
        
        new_pass_entry = ctk.CTkEntry(add_frame, placeholder_text="Password", show="*", width=150)
        new_pass_entry.pack(side="left", padx=5)
        
        role_var = ctk.StringVar(value="USER")
        role_dropdown = ctk.CTkComboBox(add_frame, values=["USER", "ADMIN"], variable=role_var, width=80)
        role_dropdown.pack(side="left", padx=5)

        def add_user():
            username = new_user_entry.get()
            password = new_pass_entry.get()
            user_role = role_var.get()

            if not all([username, password]):
                messagebox.showerror("Error", "All fields are required")
                return

            try:
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT username FROM users WHERE username=?", (username,))
                    if cursor.fetchone():
                        messagebox.showerror("Error", "Username already exists")
                        return

                    hashed_pw = hash_password(password)
                    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                                   (username, hashed_pw, user_role))
                    conn.commit()
                    refresh_user_list(tree)
                    new_user_entry.delete(0, "end")
                    new_pass_entry.delete(0, "end")
                    messagebox.showinfo("Success", "User added successfully")

            except Exception as e:
                logging.error(f"Failed to add user: {e}", exc_info=True)
                messagebox.showerror("Error", "Failed to add user")

        ctk.CTkButton(add_frame, text="Add User", font=("Arial", 16),
                      fg_color="transparent",
                      hover_color="#212121",
                      anchor="center",
                      width=80,
                      height=40,
                      corner_radius=8,
                      command=add_user).pack(side="right", padx=5)

        # Delete User Button
        def delete_user():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Error", "Please select a user")
                return

            username = tree.item(selected[0], "values")[0]
            if username == current_user:
                messagebox.showerror("Error", "Cannot delete your own account")
                return

            try:
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM users WHERE username=?", (username,))
                    conn.commit()
                    refresh_user_list(tree)
                    messagebox.showinfo("Success", "User deleted successfully")
            except Exception as e:
                logging.error(f"Failed to delete user: {e}", exc_info=True)
                messagebox.showerror("Error", "Failed to delete user")

        ctk.CTkButton(management_frame, text="Delete Selected User", font=("Arial", 16),
                      fg_color="transparent",
                      hover_color="#212121",
                      anchor="center",
                      width=200,
                      height=40,
                      corner_radius=8,
                      command=delete_user).pack(pady=5)

        # Admin Password Change Section
        admin_pass_frame = create_password_change_frame(main_frame, is_admin=True)
        admin_pass_frame.pack(pady=10)

    else:
        # Regular User Password Change Section
        user_pass_frame = create_password_change_frame(main_frame)
        user_pass_frame.pack(pady=20)

    # Back Button
    def go_back():
        window.destroy()
        parent.deiconify()

    ctk.CTkButton(main_frame, text="Back", font=("Arial", 16),
                  fg_color="transparent",
                  hover_color="#212121",
                  anchor="center",
                  width=100,
                  height=40,
                  corner_radius=8,
                  command=go_back).pack(pady=10)

    window.mainloop()
