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
        """Extracts comprehensive product details from Keepa JSON"""
        if not product_data or "products" not in product_data:
            return None
        
        product = product_data["products"][0]
        
        # 1. Reviews
        reviews = product.get("reviews", {})
        
        # 2. Images
        images = product.get("images", [])
        
        # 3. Features (Bullet points)
        features = product.get("features", [])
        
        # 4. List Price (Original price)
        # In Keepa, list price is often in the 'stats' or separate field
        list_price = product.get("stats", {}).get("listPrice")
        if list_price and list_price != -1:
            list_price = list_price / 100.0
        else:
            list_price = None

        return {
            "title": product.get("title"),
            "reviews_count": reviews.get("count"),
            "reviews_rating": reviews.get("rating"),
            "images_count": len(images),
            "list_price": list_price,
            "features": " | ".join(features) if features else "No features listed",
            "badges": product.get("badges", "None")
        }
