# core/goods_handler.py

"""
Handles operations related to goods in the Warehouse:
>>  Add new GOODS with QUANTITY and PRICE.
>> retrieve list of all goods.
>> Get unit price or quantity for a specific good.
>> support price updates and quantity adjustments .

"""


import logging
from core.db_manager import get_connection
from typing import Optional
def add_good(name: str, quantity: int, price: float) -> bool: # boolean return
    """
    Adds a new good or increases quantity if it exists (after user confirmation).

    >> name param: product name
    >> quantity parame: quantity to add
    >> price : price of the product
    >> return: True if added or updated successfully
    """
    if not name or quantity < 0 or price < 0:
        logging.warning("Invalid input for good.")
        return False

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Check if good already exists (case-insensitive)
            cursor.execute("SELECT id, quantity FROM goods WHERE LOWER(name) = LOWER(?)", (name,))
            row = cursor.fetchone()

            if row:
                # Good exists >> update quantity
                good_id, current_qty = row
                new_qty = current_qty + quantity
                cursor.execute("UPDATE goods SET quantity = ? WHERE id = ?", (new_qty, good_id))
                conn.commit()
                logging.info(f"Updated '{name}' quantity to {new_qty}")
                return True
            else:
                # New good >>>> insert
                cursor.execute(
                    "INSERT INTO goods (name, quantity, price) VALUES (?, ?, ?)",
                    (name.strip(), quantity, price)
                )
                conn.commit()
                logging.info(f"Added new good: {name}, Qty: {quantity}, Price: {price}")
                return True

    except Exception as e:
        logging.error(f"Error adding/updating good: {e}", exc_info=True)
        return False

def get_good_unit_price(good_id: int) -> Optional[float]:
    """
    Retrieve the unit price of the good with the given good_id.
    Returns the price as a float if found, or None otherwise.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT price FROM goods WHERE id = ?", (good_id,))
            row = cursor.fetchone()
            if row:
                return row[0]
            else:
                logging.warning(f"Good with id {good_id} not found.")
                return None
    except Exception as e:
        logging.error(f"Error fetching unit price for good_id {good_id}: {e}", exc_info=True)
        return None
    
def get_existing_good(name: str):
    """
    Fetch a good by name (case-insensitive). Returns (id, quantity, price) or None.

    >> name: Name of the good
    >> return: Tuple (id, quantity, price) or None
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, quantity, price FROM goods WHERE LOWER(name) = LOWER(?)", (name,))
            return cursor.fetchone()
    except Exception as e:
        logging.error(f"Error checking existing good: {e}", exc_info=True) #exc_info=True to log the traceback
        return None

def update_good_inventory(good_id: int, quantity: int, unit_cost: float, import_date: str, supplier: str, sale_price: float) -> bool:
    """
    Updates the goods table by adding the imported quantity and updating pricing and import details.
    Assumes that the goods table has extra columns (for example, last_import_date, supplier, unit_cost)
    to store these additional details.
    6 parameters (good_id, quantity, unit_cost, import_date, supplier, sale_price)
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Update the total quantity
            cursor.execute("UPDATE goods SET quantity = quantity + ? WHERE id = ?", (quantity, good_id))
            # Update the selling price if needed
            cursor.execute("UPDATE goods SET price = ? WHERE id = ?", (sale_price, good_id))
            # Optionally, store additional import details if your schema supports them:
            cursor.execute("""
                UPDATE goods
                SET last_import_date = ?, supplier = ?, unit_cost = ?
                WHERE id = ?
            """, (import_date, supplier, unit_cost, good_id))
            conn.commit()
        logging.info(f"Good {good_id} updated with additional quantity {quantity}.")
        return True
    except Exception as e:
        logging.error(f"Error updating good inventory: {e}", exc_info=True)
        return False
    
def get_all_goods() -> list[tuple]: # output is a list of tuples
    """
    Retrieves all goods from the database.

    >> return: List of tuples (id, name, quantity, price)
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, quantity, price FROM goods")
            return cursor.fetchall()
    except Exception as e:
        logging.error(f"Error retrieving goods: {e}", exc_info=True)
        return []