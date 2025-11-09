# tests/test_api_client.py
import pytest
from unittest.mock import patch, MagicMock
from omnicart_pipeline.pipeline.api_client import APIClient

@pytest.fixture
def client():
    return APIClient(base_url="https://fakestoreapi.com", limit=5)

def test_get_all_products_pagination(client):
    # Mock two sequential responses: one with data, one empty (to stop loop)
    first_response = MagicMock()
    first_response.json.return_value = [{"id": 1, "title": "Product 1"}]
    first_response.raise_for_status = MagicMock()

    second_response = MagicMock()
    second_response.json.return_value = []  # stop condition
    second_response.raise_for_status = MagicMock()

    with patch("omnicart_pipeline.pipeline.api_client.requests.get", side_effect=[first_response, second_response]) as mock_get:
        result = client.get_all_products()

        # Assertions
        assert len(result) == 1
        assert result[0]["title"] == "Product 1"
        assert mock_get.call_count == 2  # once for data, once for empty list

def test_get_all_users_success(client):
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": 1, "name": "John"}]
    mock_response.raise_for_status = MagicMock()

    with patch("omnicart_pipeline.pipeline.api_client.requests.get", return_value=mock_response) as mock_get:
        users = client.get_all_users()

        assert users == [{"id": 1, "name": "John"}]
        mock_get.assert_called_once_with("https://fakestoreapi.com/users")
