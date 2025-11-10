import pandas as pd


class DataEnricher:
    
    def __init__(self, products_data, users_data):
        self.products_data = products_data
        self.users_data = users_data
        
        
    def safe_get(self, d, key):
        return d.get(key) if isinstance(d, dict) else None
        
    
    def _convert_products_to_df(self):
        # Columns I want: id, category, price, quentity, rrating
        
        return pd.DataFrame([{
            "id": item.get("id"),
            "category": item.get("category", None),
            "price": item.get("price", None),
            "quantity": self.safe_get(item.get("rating"), "count"),
            "rating": self.safe_get(item.get("rating"), "rate")
        } for item in self.products_data])
        
        
    def _convert_users_to_df(self):
        # Username, email, name
        return pd.DataFrame([{
            "id": item.get("id", None),
            "email": item.get("email", None),
            "user_name": item.get("username", None),
            "first_name" : self.safe_get(item.get("name"), "firstname"),
            "last_name" : self.safe_get(item.get("name"), "lastname"),
        } for item in self.users_data])
    
        
    def _join_data(self):
        products_df = self._convert_products_to_df()
        users_df = self._convert_users_to_df()
        
        # merged_df = pd.me 
        return pd.merge(products_df, users_df, on='id', how='left')
    
    
    def enrich_data(self):
        enriched_df = self._join_data()
        enriched_df["revenue"] = enriched_df["quantity"] * enriched_df["price"]
        
        return enriched_df