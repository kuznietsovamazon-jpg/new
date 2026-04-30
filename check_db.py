from database import Database
import pandas as pd

db = Database()
with db.get_connection() as conn:
    df = pd.read_sql_query("SELECT * FROM price_history ORDER BY timestamp DESC LIMIT 10", conn)
    print("--- Последние записи в БД ---")
    print(df)
