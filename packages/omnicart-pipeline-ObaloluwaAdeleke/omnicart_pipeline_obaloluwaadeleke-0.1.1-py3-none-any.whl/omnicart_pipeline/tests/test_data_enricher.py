import pytest
import pandas as pd
from omnicart_pipeline.pipeline.data_enricher import DataEnricher

@pytest.fixture
def sample_products():
    return [
        {"id": 1, "title": "Laptop", "price": 1000, "rating": {"count": 5}, "userId": 1},
        {"id": 2, "title": "Phone", "price": 500, "rating": {"count": 10}, "userId": 2},
        {"id": 3, "title": "Headphones", "price": 100, "rating": {"count": 2}, "userId": 99},  # No matching user
    ]

@pytest.fixture
def sample_users():
    return [
        {"id": 1, "username": "techguru", "email": "techguru@mail.com"},
        {"id": 2, "username": "phonemaster", "email": "phonemaster@mail.com"},
    ]

@pytest.fixture
def enricher(sample_products, sample_users):
    """Returns an instance of DataEnricher with sample data."""
    return DataEnricher(sample_products, sample_users)

def test_returns_dataframe(enricher):
    df = enricher.enrich_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

def test_merge_adds_user_info(enricher):
    df = enricher.enrich_data()
    # Products 1 and 2 should have known usernames
    assert "techguru" in df["username"].values
    assert "phonemaster" in df["username"].values

def test_missing_user_filled_with_unknown(enricher):
    df = enricher.enrich_data()
    # Product 3 (userId=99) should have Unknown
    unknown_user_row = df[df["userId"] == 99].iloc[0]
    assert unknown_user_row["username"] == "Unknown"
    assert unknown_user_row["email"] == "Unknown"


def test_revenue_calculation(enricher):
    df = enricher.enrich_data()
    # Example: Laptop (1000 * 5 = 5000)
    laptop_row = df[df["title"] == "Laptop"].iloc[0]
    assert laptop_row["revenue"] == 5000

def test_handles_missing_rating(enricher, sample_products):
    # Modify one product to have no rating
    sample_products[0]["rating"] = None
    df = DataEnricher(sample_products, enricher.users).enrich_data()
    row = df[df["id"] == 1].iloc[0]
    assert row["revenue"] == 0
