from .config import ConfigManager
from .api_client import ApiClient
from .data_enricher import DataEnricher
from .data_analyzer import Analyzer
import json


class Pipeline:
    def run(self):
        # Initialize the configuration manager to load base settings (like API URLs)
        config = ConfigManager()

        # Create an API client instance using the base URL from config
        client = ApiClient(config.base_url)

        # Fetch raw data from the API: products and users
        # Then pass both datasets into the DataEnricher for further processing
        enricher = DataEnricher(client.get_all_products(), client.get_all_users())

        # Convert the raw product JSON data into a pandas DataFrame
        enricher.convert_to_dataframe("products")

        # Convert the raw user JSON data into a pandas DataFrame
        enricher.convert_to_dataframe("users")

        # Merge the product and user DataFrames on a common key (e.g., user ID)
        enricher.merge_df()

        # Add a new column (e.g., total revenue per product = price * quantity)
        updated_data = enricher.revenue_col()

        # Initialize the Analyzer class to generate insights from the enriched data
        analyze = Analyzer(enricher.revenue_col())

        # Compute total revenue for a specific seller (example: "derek")
        analyze.total_revenue_per_seller("derek")

        # Calculate how many products this seller has sold
        analyze.no_of_products_sold_per_user("derek")

        # Compute the average product price for this seller
        analyze.average_product_price("derek")

        # Convert the final enriched DataFrame into a Python dictionary for export
        export_to_dict = updated_data.to_dict()

        # Export the seller performance data to a JSON file
        with open("seller_performance_report.json", "w") as f:
            json.dump(export_to_dict, f, indent=4)

        # Print confirmation message when export completes
        print("Exported Successfully!")
