import pytest
import pandas as pd
from omnicart_pipeline.pipeline.data_analyzer import DataAnalyzer


@pytest.fixture
def sample_enriched_df():
    """Creates a small sample of enriched data for testing."""
    data = [
        {"username": "alice", "price": 100, "revenue": 1000, "id": 1},
        {"username": "alice", "price": 200, "revenue": 500, "id": 2},
        {"username": "bob", "price": 300, "revenue": 900, "id": 3},
    ]
    return pd.DataFrame(data)


def test_analyze_returns_correct_aggregations(sample_enriched_df):
    """Checks that the analyzer correctly groups and summarizes data."""
    analyzer = DataAnalyzer(sample_enriched_df)
    result = analyzer.analyze()

    # Expected values:
    # alice → total_revenue = 1000 + 500 = 1500, total_products = 2, avg_price = (100 + 200)/2 = 150
    # bob → total_revenue = 900, total_products = 1, avg_price = 300

    assert result["alice"]["total_revenue"] == 1500
    assert result["alice"]["total_products"] == 2
    assert pytest.approx(result["alice"]["avg_price"], 0.01) == 150

    assert result["bob"]["total_revenue"] == 900
    assert result["bob"]["total_products"] == 1
    assert result["bob"]["avg_price"] == 300


def test_analyze_handles_empty_dataframe():
    """Ensures no crash when given an empty DataFrame."""
    empty_df = pd.DataFrame(columns=["username", "price", "revenue", "id"])
    analyzer = DataAnalyzer(empty_df)
    result = analyzer.analyze()

    assert result == {}
