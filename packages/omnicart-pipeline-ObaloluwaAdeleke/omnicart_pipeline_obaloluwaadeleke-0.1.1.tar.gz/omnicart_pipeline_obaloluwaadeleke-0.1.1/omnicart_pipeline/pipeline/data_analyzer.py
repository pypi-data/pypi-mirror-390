import pandas as pd

class DataAnalyzer:
    def __init__(self, enriched_df):
        self.df = enriched_df

    def analyze(self):
        # Group by username and calculate the summary stats
        grouped = self.df.groupby('username').agg(
            total_revenue=('revenue', 'sum'),
            total_products=('id', 'count'),
            avg_price=('price', 'mean')
        ).reset_index()

        # Convert to a dictionary format
        result = grouped.set_index('username').to_dict(orient='index')
        return result
