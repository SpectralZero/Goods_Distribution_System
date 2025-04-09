#core/auth.py
"""
Handles user authentication and registration logic ONLY for >> 'users' >> table.
The Admin and Staff roles are handled in core/session.py (deafault setup).

I also use bcrypt for password hashing and verification. maybe switch to sha256  better than bcrypt but for easy start for me !!
"""

import logging
import bcrypt
from core.db_manager import get_connection

def authenticate_user(username: str, password: str) -> tuple | None:
    """
    Verifies user credentials in 'users' table.
    - If the stored password is hashed, use bcrypt.checkpw.
    - If the stored password is plaintext (user), compare directly (then optionally re-hash).
    
    >> username parameter: The username string.
    >> password parameter: The password string.
    Return: A tuple (user_id, role) if authentication succeeds, or None if it fails.
    """
    try:
        # Query the database
        with get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT id, password, role 
                FROM users 
                WHERE username = ?
            """
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            if not row:
                return None

            user_id, stored_password, role = row[0], row[1], row[2]

            # Check if stored_password looks like a bcrypt hash:
            # bcrypt hashes typically start with $2b$ or $2a$ or $2y$...
            if stored_password and stored_password.startswith("$2"):
                # Hashed password case
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')): #must use encode to convert to bytes 
                    return (user_id, role)
                else:
                    return None
            else:
                # Plaintext password (legacy). Check direct equality to avoid re-hashing:
                if password == stored_password:
                    return (user_id, role)
                else:
                    return None

    except Exception as e:
        logging.error(f"Error authenticating user '{username}': {e}", exc_info=True) # exc_info=True to log the traceback
        return None


def register_user(username: str, password: str) -> tuple[bool, str]:
    """
    Registers a new user in the 'users' table with default role='USER'.  CAN NOT REGISTER ADMIN 
    >> Hashes the password using bcrypt before storing.
    >> Checks for existing username to avoid duplicates.

    >> username parameter : The new username.
    >> password parameter: The new password.
    >> Return: (True, message) if success, or (False, error_msg) if failed.
    """
    try:
        # Query the database
        with get_connection() as conn:
            cursor = conn.cursor()

            # Check if user already exists:
            check_query = "SELECT 1 FROM users WHERE username = ?"
            cursor.execute(check_query, (username,))
            if cursor.fetchone():
                return False, "Username already exists."

            # Hash the password using bcrypt
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Insert new user with hashed password
            insert_query = """
                INSERT INTO users (username, password, role) 
                VALUES (?, ?, 'USER')
            """
            cursor.execute(insert_query, (username, hashed_pw))
            conn.commit()
            return True, "User created successfully."
    except Exception as e:
        logging.error(f"Error registering user '{username}': {e}", exc_info=True)
        return False, "Registration failed due to an internal error."
