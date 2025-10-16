"""
Basket KPIs API - Main FastAPI Application
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global dataframe - loaded once at startup
df: pd.DataFrame | None = None
category_columns: list[str] = []


def load_data(csv_path: str = "orders.csv") -> tuple[pd.DataFrame, list[str]]:
    """Load orders CSV and prepare data"""
    logger.info(f"Loading data from {csv_path}")
    data = pd.read_csv(csv_path)

    # Identify meta columns and category columns
    meta_cols = ['order_id', 'order_dow', 'order_hour_of_day', 'days_since_prior_order']
    cats = [col for col in data.columns if col not in meta_cols]

    # Fill NaN with 0 for category columns
    data[cats] = data[cats].fillna(0)

    logger.info(f"Loaded {len(data)} orders with {len(cats)} categories")
    return data, cats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    global df, category_columns
    csv_path = Path(__file__).parent / "orders.csv"

    if not csv_path.exists():
        logger.error(f"orders.csv not found at {csv_path}")
        raise FileNotFoundError("orders.csv not found. Please ensure the file exists in the project root.")

    df, category_columns = load_data(str(csv_path))
    logger.info("Application startup completed")

    yield

    # Shutdown (if needed)
    logger.info("Application shutdown")


app = FastAPI(
    title="Basket KPIs API",
    description="API for computing basket-level KPIs from orders data",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/kpis")
async def get_kpis() -> dict[str, Any]:
    """
    Compute and return core KPIs:
    - total_orders: number of orders
    - total_items: sum of all items across all orders
    - avg_items_per_order: average items per order
    - median_items_per_order: median items per order
    """
    if df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")

    # Compute items per order (sum across all category columns)
    items_per_order = df[category_columns].sum(axis=1)

    total_orders = len(df)
    total_items = int(items_per_order.sum())
    avg_items = float(items_per_order.mean())
    median_items = float(items_per_order.median())

    return {
        "total_orders": total_orders,
        "total_items": total_items,
        "avg_items_per_order": round(avg_items, 2),
        "median_items_per_order": round(median_items, 2)
    }


@app.get("/categories/top")
async def get_top_categories(limit: int = Query(default=10, ge=1, le=100, description="Number of top categories to return (1-100)")) -> dict[str, Any]:
    """
    Get top N categories by total item count across all orders

    Args:
        limit: Number of top categories to return (default: 10, min: 1, max: 100)

    Returns:
        Dictionary with top categories and their counts
    """
    if df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")

    # Sum each category column across all orders
    category_totals = df[category_columns].sum().sort_values(ascending=False)

    # Get top N
    top_n = category_totals.head(limit)

    # Convert to list of dicts for cleaner JSON
    top_categories = [
        {"category": cat, "total_items": int(count)}
        for cat, count in top_n.items()
    ]

    return {
        "limit": limit,
        "top_categories": top_categories
    }

@app.get("/orders/distribution")
async def get_order_distribution() -> dict[str, Any]:
    """
    Get order distribution metrics:
    - dow: day of week distribution with readable names
    - top_hours: top 10 hours by order count with readable format
    """
    if df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")

    # Day names mapping
    day_names = {
        0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday",
        4: "Thursday", 5: "Friday", 6: "Saturday"
    }

    # Day of week distribution
    dow_counts = df['order_dow'].value_counts().sort_index()
    total = len(df)

    dow_distribution = [
        {
            "day": day_names[int(dow)],
            "day_number": int(dow),
            "orders": int(count),
            "percentage": round((count / total) * 100, 1)
        }
        for dow, count in dow_counts.items()
    ]

    # Top 10 hours by order count
    hour_counts = df['order_hour_of_day'].value_counts().sort_values(ascending=False).head(10)

    def format_hour(hour):
        """Convert 24-hour to readable format"""
        if hour == 0:
            return "12:00 AM"
        elif hour < 12:
            return f"{hour}:00 AM"
        elif hour == 12:
            return "12:00 PM"
        else:
            return f"{hour-12}:00 PM"

    top_hours = [
        {
            "hour": format_hour(int(hour)),
            "hour_24": int(hour),
            "orders": int(count)
        }
        for hour, count in hour_counts.items()
    ]

    return {
        "summary": {
            "total_orders": total,
            "analysis_period": "All available data"
        },
        "day_of_week_distribution": dow_distribution,
        "peak_hours": top_hours
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    """Custom exception handler for better error messages"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    """Handle validation errors for query parameters"""
    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "message": "Invalid query parameter: limit must be between 1 and 100"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
