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
        params = {
            "key": self.api_key,
            "domain": domain,
            "asin": asin
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            return None
        return response.json()

    def extract_current_price(self, product_data, price_type="new"):
        if not product_data or "products" not in product_data:
            return None
        product = product_data["products"][0]
        csv = product.get("csv", [])
        idx = 0 if price_type == "amazon" else 1
        if len(csv) <= idx:
            return None
        price_history = csv[idx]
        if not price_history:
            return None
        latest_price = price_history[-1]
        if latest_price == -1:
            return None
        return latest_price / 100.0

    def extract_full_details(self, product_data):
        if not product_data or "products" not in product_data:
            return None
        
        product = product_data["products"][0]
        reviews = product.get("reviews", {})
        images = product.get("images", [])
        features = product.get("features", [])
        
        list_price = product.get("stats", {}).get("listPrice")
        if list_price and list_price != -1:
            list_price = list_price / 100.0
        else:
            list_price = None
        
        # EXTRACT SALES RANK
        # In Keepa, sales rank is index 3 in the CSV arrays
        csv = product.get("csv", [])
        sales_rank = None
        if len(csv) > 3:
            sr_history = csv[3]
            if sr_history:
                sales_rank = sr_history[-1] # Last value is the current rank

        return {
            "title": product.get("title"),
            "reviews_count": reviews.get("count"),
            "reviews_rating": reviews.get("rating"),
            "images_count": len(images),
            "list_price": list_price,
            "sales_rank": sales_rank,
            "features": " | ".join(features) if features else "No features listed",
            "badges": product.get("badges", "None")
        }
