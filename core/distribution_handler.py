# core/distribution_handler.py


"""
Manages the logic for distributing goods between the warehouse and branches.
>>Checks stock availability before distribution.
>> Updates inventory records according to the distribution.
>>Records distribution history with user and timestamp .


"""

import logging
from datetime import datetime
from typing import Optional, Dict
from core.db_manager import get_connection

def distribute_goods(
    good_id: int,
    from_branch_id: Optional[int],
    to_branch_id: int,
    quantity: int,
    user_id: int
) -> Dict:
    if quantity <= 0:
        logging.warning("Distribution quantity must be positive.")
        return {"success": False, "reason": "Quantity must be positive."}
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if from_branch_id is not None:
                cursor.execute("""
                    SELECT quantity FROM branch_inventories
                    WHERE branch_id = ? AND good_id = ?
                """, (from_branch_id, good_id))
                row = cursor.fetchone()
                if not row:
                    logging.warning(f"No inventory record for good_id={good_id} in branch_id={from_branch_id}.")
                    return {"success": False, "reason": "No inventory record in source branch."}
                current_source_qty = row[0]
                if current_source_qty < quantity:
                    logging.warning(f"Insufficient stock in branch {from_branch_id}. Needed={quantity}, Available={current_source_qty}")
                    return {"success": False, "reason": "Insufficient stock in source branch.", "available": current_source_qty}
                new_source_qty = current_source_qty - quantity
                cursor.execute("""
                    UPDATE branch_inventories
                    SET quantity = ?
                    WHERE branch_id = ? AND good_id = ?
                """, (new_source_qty, from_branch_id, good_id))
            else:
                cursor.execute("SELECT quantity FROM goods WHERE id = ?", (good_id,))
                row = cursor.fetchone()
                if not row:
                    logging.warning(f"No good found with id={good_id}.")
                    return {"success": False, "reason": "Good not found in warehouse."}
                warehouse_qty = row[0]
                if warehouse_qty < quantity:
                    logging.warning(f"Insufficient warehouse stock for good_id={good_id}. Needed={quantity}, Available={warehouse_qty}")
                    return {"success": False, "reason": "Insufficient warehouse stock.", "available": warehouse_qty}
                new_warehouse_qty = warehouse_qty - quantity
                cursor.execute("""
                    UPDATE goods
                    SET quantity = ?
                    WHERE id = ?
                """, (new_warehouse_qty, good_id))
            # Update destination branch inventory
            cursor.execute("""
                SELECT quantity FROM branch_inventories
                WHERE branch_id = ? AND good_id = ?
            """, (to_branch_id, good_id))
            row = cursor.fetchone()
            if row:
                dest_quantity = row[0] + quantity
                cursor.execute("""
                    UPDATE branch_inventories
                    SET quantity = ?
                    WHERE branch_id = ? AND good_id = ?
                """, (dest_quantity, to_branch_id, good_id))
            else:
                cursor.execute("""
                    INSERT INTO branch_inventories (branch_id, good_id, quantity)
                    VALUES (?, ?, ?)
                """, (to_branch_id, good_id, quantity))
            distribution_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO distributions (good_id, from_branch_id, to_branch_id, quantity, distribution_date, distributed_by_user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (good_id, from_branch_id, to_branch_id, quantity, distribution_date, user_id))
            # Optional: Log expected profit calculation
            cursor.execute("SELECT price FROM goods WHERE id = ?", (good_id,))
            price_row = cursor.fetchone()
            if price_row:
                price = price_row[0]
                profit = quantity * price * 0.2  # 20% profit margin
                logging.info(f"Expected profit from this distribution: {profit:.2f}")
            conn.commit()
            logging.info(f"Distributed {quantity} of good_id={good_id} from {from_branch_id} to {to_branch_id}.")
            return {"success": True}
    except Exception as e:
        logging.error(f"Error distributing goods: {e}", exc_info=True)
        return {"success": False, "reason": str(e)}

def get_stock(good_id: int, branch_id: int = None) -> Dict:
    """
    Returns the current stock for a good. If branch_id is provided, returns the branch inventory stock,
    otherwise returns the warehouse stock from the goods table.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if branch_id:
                cursor.execute("""
                    SELECT quantity FROM branch_inventories
                    WHERE branch_id = ? AND good_id = ?
                """, (branch_id, good_id))
            else:
                cursor.execute("SELECT quantity FROM goods WHERE id = ?", (good_id,))
            row = cursor.fetchone()
            if row:
                return {"success": True, "stock": row[0]}
            else:
                return {"success": False, "reason": "No record found."}
    except Exception as e:
        logging.error(f"Error retrieving stock: {e}", exc_info=True)
        return {"success": False, "reason": str(e)}
