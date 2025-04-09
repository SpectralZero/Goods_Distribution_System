import sqlite3

# Set plaintext password (not secure!)
conn = sqlite3.connect("database/goods_system.db")
cursor = conn.cursor()

cursor.execute("UPDATE users SET password='jamal1234', role='ADMIN' WHERE username='jamal'")
conn.commit()
conn.close()

print("Updated to ADMIN for user 'jamal' with password 'jamal1234'.")

# from PIL import Image
# absolute_path = r"C:\Users\RTX\Desktop\python course project\bg.jpg"
# try:
#     img = Image.open(absolute_path)
#     img.verify()  # just to check it's a valid image
#     print("Successfully opened the image!")
# except Exception as e:
#     print("Failed to open the image:", e)
#-------------------------------------------------------
# SECURE VERSION FOR ADMIN REGISTRATION
# import bcrypt
# username = "jamal"
# default_password = "jamal123"
# hashed_pw = bcrypt.hashpw(default_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# conn = sqlite3.connect("database/goods_system.db")
# cursor = conn.cursor()

# cursor.execute("UPDATE users SET password=?, role='ADMIN' WHERE username=?", (hashed_pw, username))
# conn.commit()
# conn.close()

# print(f"User '{username}' updated to ADMIN with default password '{default_password}'.")