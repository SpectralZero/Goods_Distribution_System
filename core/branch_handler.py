# core/branch_handler.py

"""
Branch handler module to handle branch-related operations, including adding, editing, and deleting branches.
"""
import logging
from core.db_manager import get_connection, update_branch, delete_branch
from typing import List, Tuple

def get_all_branches() -> List[Tuple]: # a type hint in Python to specify that the function returns a list of tuples 
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, name, location FROM branches"
            cursor.execute(query)
            return cursor.fetchall()
    except Exception as e:
        logging.error(f"Error retrieving branches: {e}", exc_info=True)
        return []

def add_branch(name: str, location: str) -> bool:  # (:) spcifies the type if variable and returns bolean 
    if not name or not location:
        logging.error("Failed to add branch: name or location is empty.")
        return False
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Check for duplicate branch name
            cursor.execute("SELECT id FROM branches WHERE LOWER(name) = LOWER(?)", (name,))
            if cursor.fetchone():
                logging.error(f"Branch with name '{name}' already exists.")
                return False
            query = "INSERT INTO branches (name, location) VALUES (?, ?)"
            cursor.execute(query, (name, location))
            conn.commit()
        logging.info(f"Branch '{name}' added successfully.")
        return True
    except Exception as e:
        logging.error(f"Error adding branch '{name}': {e}", exc_info=True)
        return False

def edit_branch(branch_id: int, name: str, location: str) -> bool:
    if not name or not location:
        logging.error("Failed to edit branch: name or location is empty.")
        return False
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Check if the new name already exists for a different branch
            cursor.execute("SELECT id FROM branches WHERE LOWER(name) = LOWER(?) AND id <> ?", (name, branch_id))
            if cursor.fetchone():
                logging.error(f"Branch name '{name}' already exists.")
                return False
        # Use the db_manager's update_branch function
        return update_branch(branch_id, name, location)
    except Exception as e:
        logging.error(f"Error editing branch {branch_id}: {e}", exc_info=True)
        return False

def delete_branch_record(branch_id: int) -> bool:
    try:
        return delete_branch(branch_id)
    except Exception as e:
        logging.error(f"Error deleting branch {branch_id}: {e}", exc_info=True)
        return False
