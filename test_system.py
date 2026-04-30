from database import Database
from keepa_client import KeepaClient
from monitor import monitor
import pandas as pd

def test_full_system():
    print("Starting Full System Integration Test...")
    db = Database()
    
    # 1. Test Project Creation
    proj_name = "Test_Project_AI"
    if db.create_project(proj_name):
        print(f"Project '{proj_name}' created successfully.")
    else:
        print(f"Project '{proj_name}' already exists.")
    
    # Get project ID
    projects = db.get_projects()
    project_id = next(pid for pid, name in projects if name == proj_name)
    
    # 2. Test Adding ASINs
    test_asins = ["B08N5KWB9H", "B09G9FPHYX"]
    for asin in test_asins:
        if db.add_asin_to_project(project_id, asin):
            print(f"ASIN {asin} added to project.")
        else:
            print(f"ASIN {asin} already exists in project.")
            
    # 3. Test Monitor Logic
    print("\nRunning one cycle of the monitor...")
    # We call monitor with single_run=True to test one cycle
    monitor(single_run=True)
    
    # 4. Verify Data in DB
    with db.get_connection() as conn:
        df_history = pd.read_sql_query("SELECT * FROM price_history ORDER BY timestamp DESC LIMIT 5", conn)
        print("\n--- Latest DB Entries ---")
        print(df_history)
        
    print("\nSystem Integration Test Completed Successfully!")

if __name__ == "__main__":
    test_full_system()
