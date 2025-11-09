from .config import ConfigManager
from .api_client import ApiClient
from .data_enricher import DataEnricher
# import pandas as pd


class Analyzer:
    """
    Total revenue per seller (username).
    The number of products sold per seller.
    The average product price for each seller.
    
    """
    def __init__(self, merged_df):
        self.df = merged_df
        self.report_per_seller = {}

    def total_revenue_per_seller(self, username:str):
        # total_revenue_for_each_seller = float(self.df.loc[self.df["username"] == username, "revenue"].values[0])
        total_revenue_for_each_seller = self.df.groupby("username")["revenue"].sum()
        self.total_revenue_for_each_seller = float(total_revenue_for_each_seller[username])

         # Add/update the report per seller
        if username not in self.report_per_seller:
            self.report_per_seller[username] = {
                "revenue": self.total_revenue_for_each_seller
            }
        else:
            self.report_per_seller[username]["revenue"] = self.total_revenue_for_each_seller

        return self.report_per_seller    

    def no_of_products_sold_per_user(self, username:str):
        """The number of products sold per seller"""
        # no_of_products_sold = float(self.df.loc[self.df["username"] == username, "quantity"].values[0])
        no_of_products_sold = self.df.groupby("username")["quantity"].sum()
        self.no_of_products_sold = float(no_of_products_sold[username])

         # Add/update the report per seller
        if username not in self.report_per_seller:
            self.report_per_seller[username] = {
                "quantity": self.no_of_products_sold
            }
        else:
            self.report_per_seller[username]["quantity"] = self.no_of_products_sold

        return self.report_per_seller
    
    def average_product_price(self, username:str):
        """The average product price for each seller"""
        average_price = self.df.groupby("username")["price"].mean()
        self.average_price = float(average_price[username])

         # Add/update the report per seller
        if username not in self.report_per_seller:
            self.report_per_seller[username] = {
                "average_price": self.average_price
            }
        else:
            self.report_per_seller[username]["average_price"] = self.average_price

        return self.report_per_seller


        
    
    
def main():
    config = ConfigManager()
    client = ApiClient(config.base_url)
    # print(client.get_all_products())
    enricher = DataEnricher(client.get_all_products(), client.get_all_users())
    enricher.convert_to_dataframe("products")
    enricher.convert_to_dataframe("users")
    enricher.merge_df()
    enricher.revenue_col()
    analyze = Analyzer(enricher.revenue_col())
    print(analyze.total_revenue_per_seller("derek"))
    print(analyze.no_of_products_sold_per_user("derek"))
    print(analyze.average_product_price("derek"))
    # print(analyze.multiply())

if __name__ == "__main__":
    main()