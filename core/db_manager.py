# core/db_manager.py
"""
Handles all database connection logic and schema initialization for the Goods Distribution System.
<<<  Manages SQLite connection

"""

import logging
import sqlite3
import os

def get_connection() -> sqlite3.Connection:
    db_path = os.path.join("database", "goods_system.db")
    if not os.path.exists("database"):
        os.makedirs("database", exist_ok=True)
        logging.info("Created 'database' folder for storing SQLite DB.")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    _init_schema(conn)
    return conn
# Initialize the database schema
def _init_schema(conn: sqlite3.Connection) -> None:
    
    try:
        cursor = conn.cursor()
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'USER'
            );
        """)
        # Branches table with UNIQUE constraint on name
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS branches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                UNIQUE(name)
            );
        """)
        # Goods table with UNIQUE constraint on name
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                price REAL NOT NULL DEFAULT 0.0,
                UNIQUE(name)
            );
        """)
        # Sales table (only one definition)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                good_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                sale_date TEXT NOT NULL,
                sold_by_user_id INTEGER,
                branch_id INTEGER,
                FOREIGN KEY(good_id) REFERENCES goods(id) ON DELETE CASCADE,
                FOREIGN KEY(sold_by_user_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY(branch_id) REFERENCES branches(id) ON DELETE CASCADE
            );
        """)
        # Branch inventories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS branch_inventories (
                branch_id INTEGER NOT NULL,
                good_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (branch_id, good_id),
                FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE,
                FOREIGN KEY (good_id) REFERENCES goods(id) ON DELETE CASCADE
            );
        """)
        # Distributions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS distributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                good_id INTEGER NOT NULL,
                from_branch_id INTEGER,
                to_branch_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                distribution_date TEXT NOT NULL,
                distributed_by_user_id INTEGER,
                FOREIGN KEY (good_id) REFERENCES goods(id) ON DELETE CASCADE,
                FOREIGN KEY (from_branch_id) REFERENCES branches(id) ON DELETE SET NULL,
                FOREIGN KEY (to_branch_id) REFERENCES branches(id) ON DELETE CASCADE,
                FOREIGN KEY (distributed_by_user_id) REFERENCES users(id) ON DELETE SET NULL
            );
        """)
        # Imported goods table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS imported_goods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                good_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                import_date TEXT NOT NULL,
                import_place TEXT NOT NULL,
                import_cost REAL NOT NULL
            );
        """)
        conn.commit()
        logging.info("✅ Database schema initialized.")
    except Exception as e:
        logging.error(f"Schema initialization error: {e}", exc_info=True)

# functions for updating and deleting records

def update_branch(branch_id: int, name: str, location: str) -> bool:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE branches SET name = ?, location = ? WHERE id = ?", (name, location, branch_id))
            conn.commit()
        logging.info(f"Branch {branch_id} updated to name: {name}, location: {location}.")
        return True
    except Exception as e:
        logging.error(f"Error updating branch {branch_id}: {e}", exc_info=True)
        return False

def delete_branch(branch_id: int) -> bool:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM branches WHERE id = ?", (branch_id,))
            conn.commit()
        logging.info(f"Branch {branch_id} deleted successfully.")
        return True
    except Exception as e:
        logging.error(f"Error deleting branch {branch_id}: {e}", exc_info=True)
        return False

def update_good(good_id: int, name: str, price: float) -> bool:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE goods SET name = ?, price = ? WHERE id = ?", (name, price, good_id))
            conn.commit()
        logging.info(f"Good {good_id} updated to name: {name}, price: {price}.")
        return True
    except Exception as e:
        logging.error(f"Error updating good {good_id}: {e}", exc_info=True)
        return False

def delete_good(good_id: int) -> bool:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM goods WHERE id = ?", (good_id,))
            conn.commit()
        logging.info(f"Good {good_id} deleted successfully.")
        return True
    except Exception as e:
        logging.error(f"Error deleting good {good_id}: {e}", exc_info=True)
        return False

#  add sample seed data >> optioanl 
def seed_sample_data():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO branches (id, name, location) VALUES (1, 'Main', 'City Center')")
            cursor.execute("INSERT OR IGNORE INTO branches (id, name, location) VALUES (2, 'East', 'East Side')")
            cursor.execute("INSERT OR IGNORE INTO goods (id, name, quantity, price) VALUES (1, 'Laptop', 100, 999.99)")
            cursor.execute("INSERT OR IGNORE INTO goods (id, name, quantity, price) VALUES (2, 'Mouse', 150, 25.50)")
            conn.commit()
            logging.info("Seed data inserted.")
    except Exception as e:
        logging.error(f"Error seeding data: {e}", exc_info=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_sample_data()
