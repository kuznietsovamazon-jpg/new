import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path="amazon_monitor.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize the database with projects and products tracking"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Table for Projects
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    created_at DATETIME NOT NULL
                )
            ''')
            
            # 2. Table for Products (linked to projects)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tracked_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    asin TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    UNIQUE(project_id, asin)
                )
            ''')
            
            # 3. Table for Price History
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asin TEXT NOT NULL,
                    price REAL NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_asin ON price_history(asin)')
            conn.commit()

    # --- Project Management ---
    def create_project(self, name):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO projects (name, created_at) VALUES (?, ?)', 
                               (name, datetime.now().isoformat()))
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
                cursor.execute('INSERT INTO tracked_products (project_id, asin) VALUES (?, ?)', 
                               (project_id, asin))
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
        """Get a unique list of all ASINs across all projects for the monitor"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT asin FROM tracked_products')
            return [row[0] for row in cursor.fetchall()]

    # --- Price History ---
    def save_price(self, asin, price):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO price_history (asin, price, timestamp) VALUES (?, ?, ?)',
                (asin, price, datetime.now().isoformat())
            )
            conn.commit()

    def get_last_price(self, asin):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT price FROM price_history WHERE asin = ? ORDER BY timestamp DESC LIMIT 1',
                (asin,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
