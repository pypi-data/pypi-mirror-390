import pandas as pd


class Analyzer:
    
    def __init__(self, enriched_data):
        self.df = enriched_data
        
        
    def total_revenue_per_seller(self):
        total_revenue_per_seller = self.df.groupby("user_name")["revenue"].sum().reset_index(name="total_revenue")
        
        # Let us sort in descending order
        total_revenue_per_seller = total_revenue_per_seller.sort_values(by="total_revenue", ascending=False).reset_index(drop=True)
        
        return total_revenue_per_seller
    
    
    def total_products_per_seller(self):
        products_per_seller = self.df.groupby("user_name")["quantity"].sum().reset_index(name="number_of_products_sold")
        
        return products_per_seller
    
    
    def average_products_price_per_seller(self):
        average_price_per_seller = self.df.groupby("user_name")["price"].mean().reset_index(name="average_price_per_seller")
        
        return average_price_per_seller
    
    
    def perform_analysis(self):
        total_revenue_per_seller = self.total_revenue_per_seller()
        products_per_seller = self.total_products_per_seller()
        average_price_per_seller = self.average_products_price_per_seller()
        
        # We merge
        merged_seller_performance = pd.merge(total_revenue_per_seller, products_per_seller, on="user_name", how="left")
        merged_seller_performance = pd.merge(merged_seller_performance, average_price_per_seller, on="user_name", how="left")

        return merged_seller_performance.to_dict()