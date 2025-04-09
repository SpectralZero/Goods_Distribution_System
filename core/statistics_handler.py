# core/statistics_handler.py

"""
statistical data aggregation:

* Sales totals grouped by branch and product.
** full distribution history with user and date.
** current inventory status across all branches.

<< used later >>used for generating charts and reports in the UI.
"""

import logging
from core.db_manager import get_connection

def get_sales_by_branch() -> list[tuple]: # for each branch !!
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.name as branch_name, g.name as good_name, SUM(s.quantity) as total_sold
                FROM sales s
                JOIN goods g ON s.good_id = g.id
                JOIN branches b ON s.branch_id = b.id
                GROUP BY s.branch_id, s.good_id
            """)
            return cursor.fetchall()
    except Exception as e:
        logging.error("Error fetching sales by branch", exc_info=True)
        return []

def get_distribution_history() -> list[tuple]:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT g.name, 
                       COALESCE(sb.name, 'Warehouse') AS from_branch,
                       tb.name AS to_branch,
                       d.quantity,
                       d.distribution_date,
                       u.username
                FROM distributions d
                LEFT JOIN branches sb ON d.from_branch_id = sb.id
                JOIN branches tb ON d.to_branch_id = tb.id
                JOIN goods g ON d.good_id = g.id
                JOIN users u ON d.distributed_by_user_id = u.id
                ORDER BY d.distribution_date DESC
            """)
            return cursor.fetchall()
    except Exception as e:
        logging.error("Error fetching distribution history", exc_info=True)
        return []

def get_branch_inventory() -> list[tuple]:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.name, g.name, bi.quantity
                FROM branch_inventories bi
                JOIN branches b ON bi.branch_id = b.id
                JOIN goods g ON bi.good_id = g.id
                ORDER BY b.name, g.name
            """)
            return cursor.fetchall()
    except Exception as e:
        logging.error("Error fetching branch inventory", exc_info=True)
        return []
