import pandas as pd

class DataEnricher:
    def __init__(self, products, users):
        self.products = products
        self.users = users

    def enrich_data(self):
        # Convert lists of dictionaries into pandas DataFrames
        df_products = pd.DataFrame(self.products)
        df_users = pd.DataFrame(self.users)

        print("Products columns:", df_products.columns.tolist())
        print("Users columns:", df_users.columns.tolist())
        print(df_products.head())
        print(df_users.head())

        # Merge product data with user data using the userId column
        # Some products may not have a matching user — we use a LEFT JOIN to keep all products
        df_merged = pd.merge(
            df_products,
            df_users,
            how="left",
            left_on="id",  # column in products
            right_on="id",     # column in users
            suffixes=("_product", "_user")
        )

        # Handle missing users (fill empty fields with 'Unknown')
        df_merged["username"] = df_merged.get("username", "Unknown").fillna("Unknown")
        df_merged["email"] = df_merged.get("email", "Unknown").fillna("Unknown")

        # Compute revenue = price * rating.count
        # We assume rating.count is "quantity sold"
        df_merged["revenue"] = df_merged.apply(
            lambda row: row["price"] * row["rating"]["count"] if isinstance(row["rating"], dict) else 0,
            axis=1
        )

        return df_merged

