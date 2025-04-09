# core/sales_handler.py

"""
 *** sales operations for goods:
>> Record sales transactions by branch and user.
>> Validate quantity against available stock.
>>>> Update branch inventory after sale. 
>> Supports retrieval and verification of good stock.
"""


import logging
from datetime import datetime
from core.db_manager import get_connection
from typing import Optional, Dict

def record_sale(good_id: int, branch_id: int, quantity: int, sold_by_user_id: int) -> Dict:
    if quantity <= 0:
        logging.warning("Sale quantity must be positive.")
        return {"success": False, "reason": "Quantity must be positive."}
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Check stock in branch_inventories
            cursor.execute("""
                SELECT quantity FROM branch_inventories
                WHERE branch_id = ? AND good_id = ?
            """, (branch_id, good_id))
            row = cursor.fetchone()
            if not row:
                logging.warning(f"No inventory row for branch_id={branch_id}, good_id={good_id}")
                return {"success": False, "reason": "No inventory record."}
            current_stock = row[0]
            if current_stock < quantity:
                logging.warning(f"Insufficient stock in branch {branch_id}. Needed={quantity}, Available={current_stock}")
                return {"success": False, "reason": "Insufficient stock", "available": current_stock}
            new_stock = current_stock - quantity
            cursor.execute("""
                UPDATE branch_inventories
                SET quantity = ?
                WHERE branch_id = ? AND good_id = ?
            """, (new_stock, branch_id, good_id))
            sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO sales (good_id, quantity, sale_date, sold_by_user_id, branch_id)
                VALUES (?, ?, ?, ?, ?)
            """, (good_id, quantity, sale_date, sold_by_user_id, branch_id))
            conn.commit()
            logging.info(f"Sale recorded: {quantity} of good_id={good_id} at branch_id={branch_id}")
            return {"success": True}
    except Exception as e:
        logging.error(f"Error recording sale: {e}", exc_info=True)
        return {"success": False, "reason": str(e)}
