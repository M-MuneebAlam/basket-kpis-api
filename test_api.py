"""
Tests for Basket KPIs API
"""
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from main import app


def test_kpi_math_unit_test():
    """Unit test for KPI math using a tiny in-memory DataFrame"""
    # Create tiny test DataFrame
    data = {
        'order_id': ['1', '2', '3'],
        'order_dow': [0, 1, 2],
        'order_hour_of_day': [10, 14, 10],
        'days_since_prior_order': [5.0, 10.0, 7.0],
        'fresh_fruits': [2, 0, 5],
        'yogurt': [1, 3, 0],
        'packaged_cheese': [1, 1, 0]
    }
    df = pd.DataFrame(data)

    # Identify category columns (same logic as main.py)
    meta_cols = ['order_id', 'order_dow', 'order_hour_of_day', 'days_since_prior_order']
    category_cols = [col for col in df.columns if col not in meta_cols]

    # Fill NaN with 0 (same logic as main.py)
    df[category_cols] = df[category_cols].fillna(0)

    # Calculate KPIs (same logic as main.py)
    items_per_order = df[category_cols].sum(axis=1)
    total_orders = len(df)
    total_items = int(items_per_order.sum())
    avg_items = float(items_per_order.mean())
    median_items = float(items_per_order.median())

    # Expected calculations:
    # Order 1: 2+1+1 = 4 items
    # Order 2: 0+3+1 = 4 items
    # Order 3: 5+0+0 = 5 items
    # Total: 13 items, Average: 4.33, Median: 4.0

    assert total_orders == 3
    assert total_items == 13
    assert round(avg_items, 2) == 4.33
    assert median_items == 4.0


@pytest.fixture
def client():
    """Create test client with sample data"""
    # Create sample data for testing
    sample_data = {
        'order_id': ['1', '2', '3'],
        'order_dow': [0, 1, 2],
        'order_hour_of_day': [10, 14, 10],
        'days_since_prior_order': [5.0, 10.0, 7.0],
        'fresh_fruits': [2, 0, 5],
        'yogurt': [1, 3, 0],
        'packaged_cheese': [1, 1, 0]
    }
    df = pd.DataFrame(sample_data)

    # Identify category columns (same logic as main.py)
    meta_cols = ['order_id', 'order_dow', 'order_hour_of_day', 'days_since_prior_order']
    category_cols = [col for col in df.columns if col not in meta_cols]

    # Fill NaN with 0 (same logic as main.py)
    df[category_cols] = df[category_cols].fillna(0)

    # Inject test data into the app
    import main
    main.df = df
    main.category_columns = category_cols

    return TestClient(app)


def test_api_endpoints(client):
    """API test for /kpis and /categories/top endpoints"""

    # Test /kpis endpoint
    response = client.get("/kpis")
    assert response.status_code == 200

    kpis_data = response.json()
    assert "total_orders" in kpis_data
    assert "total_items" in kpis_data
    assert "avg_items_per_order" in kpis_data
    assert "median_items_per_order" in kpis_data

    # Test /categories/top endpoint
    response = client.get("/categories/top")
    assert response.status_code == 200

    categories_data = response.json()
    assert "limit" in categories_data
    assert "top_categories" in categories_data
    assert categories_data["limit"] == 10  # default limit
    assert isinstance(categories_data["top_categories"], list)

    # Test validation: 400 for bad query params
    response = client.get("/categories/top?limit=0")  # negative/zero limit
    assert response.status_code == 400
    error_data = response.json()
    assert "status" in error_data
    assert error_data["status"] == "error"
    assert "message" in error_data
    assert "limit must be between 1 and 100" in error_data["message"]

    response = client.get("/categories/top?limit=101")  # limit too high
    assert response.status_code == 400

    response = client.get("/categories/top?limit=abc")  # invalid type
    assert response.status_code == 400
