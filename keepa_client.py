import requests
import os
from dotenv import load_dotenv

load_dotenv()

class KeepaClient:
    def __init__(self):
        self.api_key = os.getenv("KEEPA_API_KEY")
        self.base_url = "https://api.keepa.com/product"
        if not self.api_key:
            raise ValueError("API Key not found in .env file")

    def get_product_data(self, asin, domain=1):
        """
        Fetch product data for a given ASIN.
        domain=1 is Amazon.com
        """
        params = {
            "key": self.api_key,
            "domain": domain,
            "asin": asin
        }
        
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            print(f"Error fetching data for {asin}: {response.status_code}")
            return None
        
        return response.json()

    def extract_current_price(self, product_data, price_type="new"):
        """
        Extracts the latest price from Keepa's CSV format.
        price_type: 'amazon' (index 0) or 'new' (index 1)
        """
        if not product_data or "products" not in product_data:
            return None
        
        product = product_data["products"][0]
        csv = product.get("csv", [])
        
        # Index 0: Amazon, Index 1: New
        idx = 0 if price_type == "amazon" else 1
        
        if len(csv) <= idx:
            return None
            
        price_history = csv[idx]
        if not price_history:
            return None
            
        # Keepa price history is [time, price, time, price...]
        # The last value is the most recent price
        latest_price = price_history[-1]
        
        if latest_price == -1: # -1 means no price available
            return None
            
        # Prices are in cents, convert to decimal
        return latest_price / 100.0

    def get_buybox_price(self, product_data):
        """Extracts current Buy Box price if available"""
        if not product_data or "products" not in product_data:
            return None
        
        product = product_data["products"][0]
        # Buy Box is often in the 'stats' or direct price fields
        # For simplicity, we use the latest 'New' price as Buy Box proxy 
        # unless we dive deeper into the 'offers' data.
        return self.extract_current_price(product_data, "new")
