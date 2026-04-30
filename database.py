import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path="amazon_monitor.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    created_at DATETIME NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tracked_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    asin TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    UNIQUE(project_id, asin)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS product_details (
                    asin TEXT PRIMARY KEY,
                    title TEXT,
                    reviews_count INTEGER,
                    reviews_rating REAL,
                    images_count INTEGER,
                    list_price REAL,
                    sales_rank INTEGER,
                    features TEXT,
                    badges TEXT,
                    updated_at DATETIME
                )
            ''')
            try:
                cursor.execute('ALTER TABLE product_details ADD COLUMN sales_rank INTEGER')
            except sqlite3.OperationalError:
                pass
            
            # Price History
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asin TEXT NOT NULL,
                    price REAL NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            ''')
            
            # NEW: Sales Rank History
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales_rank_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asin TEXT NOT NULL,
                    rank INTEGER NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_asin_p ON price_history(asin)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_asin_s ON sales_rank_history(asin)')
            conn.commit()

    def create_project(self, name):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO projects (name, created_at) VALUES (?, ?)', (name, datetime.now().isoformat()))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def get_projects(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM projects')
            return cursor.fetchall()

    def add_asin_to_project(self, project_id, asin):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO tracked_products (project_id, asin) VALUES (?, ?)', (project_id, asin))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def get_asins_for_project(self, project_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT asin FROM tracked_products WHERE project_id = ?', (project_id,))
            return [row[0] for row in cursor.fetchall()]

    def get_all_tracked_asins(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT asin FROM tracked_products')
            return [row[0] for row in cursor.fetchall()]

    def save_price(self, asin, price):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO price_history (asin, price, timestamp) VALUES (?, ?, ?)', (asin, price, datetime.now().isoformat()))
            conn.commit()

    def save_sales_rank(self, asin, rank):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO sales_rank_history (asin, rank, timestamp) VALUES (?, ?, ?)', (asin, rank, datetime.now().isoformat()))
            conn.commit()

    def save_product_details(self, asin, details):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO product_details 
                (asin, title, reviews_count, reviews_rating, images_count, list_price, sales_rank, features, badges, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (asin, details.get('title'), details.get('reviews_count'), details.get('reviews_rating'), 
                  details.get('images_count'), details.get('list_price'), details.get('sales_rank'), 
                  details.get('features'), details.get('badges'), datetime.now().isoformat()))
            conn.commit()

    def get_product_details(self, asin):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM product_details WHERE asin = ?', (asin,))
            row = cursor.fetchone()
            if row:
                cols = [column[0] for column in cursor.description]
                return dict(zip(cols, row))
            return None

    def get_last_price(self, asin):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT price FROM price_history WHERE asin = ? ORDER BY timestamp DESC LIMIT 1', (asin,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_sales_history(self, asin):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT timestamp, rank FROM sales_rank_history WHERE asin = ? ORDER BY timestamp ASC', (asin,))
            rows = cursor.fetchall()
            return pd.DataFrame(rows, columns=['timestamp', 'rank'])
