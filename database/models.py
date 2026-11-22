import sqlite3

DB_NAME  = "monti.db"

def init_db():

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                phone TEXT, -- <-- Исправлено!
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_key TEXT PRIMARY KEY,
                name TEXT,
                size TEXT,
                price INTEGER,
                is_available INTEGER DEFAULT 1
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                items TEXT,
                total_price INTEGER,
                status TEXT DEFAULT 'new',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        conn.commit()

def save_user(user_id: int, name: str, phone: str):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(
            """
    INSERT INTO users(user_id,name,phone)
    VALUES(?,?,?)ON CONFLICT(user_id) DO UPDATE SET
    name = excluded.name,
    phone = excluded.phone
        """,(user_id,name,phone)
        )
    conn.commit()


def save_orders(user_id: int, items_json: str, total_price: int):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO orders(user_id,items,total_price)
            VALUES(?,?,?)""",(user_id,items_json,total_price)

        )
        conn.commit()
        return cur.lastrowid


def show_orders():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT user_id, items, total_price FROM orders ORDER BY order_id DESC LIMIT 5"""
        )

        order_id = cur.lastrowid
        return order_id

def get_all_users():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT user_id FROM users")
        return [row[0] for row in cur.fetchall()] 

def get_all_sum():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT sum(total_price) FROM orders")
        result = cur.fetchone()
        return result[0] if result and result[0] else 0

def get_all_count():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) from orders")
        result = cur.fetchone()
        return result[0] if result and result[0] else 0


def get_user_by_id(order_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM orders WHERE order_id = ?",(order_id,))
        result = cur.fetchone()
        return result[0] if result and result[0] else 0
    