import time
import os
from keepa_client import KeepaClient
from database import Database

# Configuration
ASINS_FILE = "asins.txt"
CHECK_INTERVAL = 3600  # Check every hour

def load_asins():
    if not os.path.exists(ASINS_FILE):
        print(f"Error: {ASINS_FILE} not found!")
        return []
    with open(ASINS_FILE, "r") as f:
        # Read lines, strip whitespace, and ignore empty lines
        return [line.strip() for line in f if line.strip()]

def monitor(single_run=False):
    client = KeepaClient()
    db = Database()
    
    while True:
        # Get all unique ASINs from all projects in the DB
        asins = db.get_all_tracked_asins()
        
        if not asins:
            print("No ASINs found in any project. Waiting for data...")
            time.sleep(60)
            continue

        print(f"Monitoring cycle started for {len(asins)} products across all projects...")
        
        for asin in asins:
            print(f"Checking {asin}...")
            data = client.get_product_data(asin)
            
            if not data:
                print(f"Could not fetch data for {asin}")
                continue
                
            current_price = client.extract_current_price(data, "new")
            
            if current_price is None:
                print(f"Price not available for {asin}")
                continue
                
            last_price = db.get_last_price(asin)
            
            if last_price is not None and last_price != current_price:
                diff = current_price - last_price
                direction = "INCREASED" if diff > 0 else "DECREASED"
                print(f"ALERT: {asin} | {direction} | {last_price}$ -> {current_price}$")
            elif last_price is None:
                print(f"Initial price for {asin} recorded: {current_price}$")
            else:
                print(f"No change for {asin}: {current_price}$")
            
            db.save_price(asin, current_price)
            
        if single_run:
            break
            
        print(f"Cycle complete. Sleeping for {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        # Run once for testing
        monitor(single_run=True)
    except KeyboardInterrupt:
        print("\nMonitor stopped by user.")
