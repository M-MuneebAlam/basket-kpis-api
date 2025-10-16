# Basket KPIs API

FastAPI service that computes basket-level KPIs from orders data.

---

## Assignment Requirements Met

- **Python 3.10+** with FastAPI
- **Pandas** for vectorized operations (no Python loops)
- **CSV loaded once at startup** using lifespan context manager
- **4 Required Endpoints**: `/health`, `/kpis`, `/categories/top`, `/orders/distribution`
- **Validation**: 400 errors with helpful messages for bad query params
- **Tests**: Unit test (KPI math) + API tests (pytest)
- **Type hints** throughout + ruff for linting
- **Dockerfile + make run**
- **Auto-generated API docs** at `/docs`

---

## Quick Start

### Running and Testing

**With Make (Linux/Mac/WSL):**

```bash
make docker-evaluate  # Build, test, lint, and run everything
```

**Without Make (Windows/All Platforms):**

```bash
docker build -t basket-kpis-api .
docker run --rm basket-kpis-api pytest test_api.py -v
docker run --rm basket-kpis-api ruff check main.py test_api.py
docker run -p 8000:8000 basket-kpis-api
```

**Verify it's working:**

```bash
curl http://localhost:8000/health
curl http://localhost:8000/kpis
```

### For Development Only

```bash
pip install -r requirements.txt
uvicorn main:app --reload
# Visit http://localhost:8000/docs
```

---

## API Endpoints

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Response:**

```json
{ "status": "ok" }
```

### 2. Get KPIs

```bash
curl http://localhost:8000/kpis
```

**Response:**

```json
{
  "total_orders": 3421083,
  "total_items": 39123729,
  "avg_items_per_order": 11.43,
  "median_items_per_order": 8.0
}
```

### 3. Top Categories

```bash
curl "http://localhost:8000/categories/top?limit=5"
```

**Response:**

```json
{
  "limit": 5,
  "top_categories": [
    { "category": "fresh_fruits", "total_items": 4824593 },
    { "category": "fresh_vegetables", "total_items": 4019741 },
    { "category": "packaged_vegetables_fruits", "total_items": 3255627 },
    { "category": "yogurt", "total_items": 2847580 },
    { "category": "packaged_cheese", "total_items": 2134650 }
  ]
}
```

**Query Parameters:**

- `limit` (optional, default=10): Number of categories (1-100)
- Invalid params return 400 with helpful error messages

### 4. Order Distribution

```bash
curl http://localhost:8000/orders/distribution
```

**Response:**

```json
{
  "summary": {
    "total_orders": 5000,
    "analysis_period": "All available data"
  },
  "day_of_week_distribution": [
    {
      "day": "Sunday",
      "day_number": 0,
      "orders": 715,
      "percentage": 14.3
    },
    {
      "day": "Monday",
      "day_number": 1,
      "orders": 683,
      "percentage": 13.7
    }
  ],
  "peak_hours": [
    {
      "hour": "10:00 AM",
      "hour_24": 10,
      "orders": 420
    },
    {
      "hour": "11:00 AM",
      "hour_24": 11,
      "orders": 380
    }
  ]
}
```

---

## 📚 Interactive API Documentation

Visit **http://localhost:8000/docs** for Swagger UI with all endpoints and schemas.

---

## 🧪 Test Coverage

- **Unit test**: KPI math validation using in-memory DataFrame
- **API tests**: Basic endpoints including validation error handling

---

## Project Structure

```
├── main.py              # FastAPI application
├── test_api.py          # Test suite
├── requirements.txt     # Python dependencies (pinned versions)
├── Dockerfile           # Container configuration
├── Makefile             # Development commands
├── pyproject.toml       # Ruff configuration
├── .dockerignore        # Docker build exclusions
└── orders.csv           # Data file
```

---

## Design Decisions, Assumptions & Tradeoffs

### Assumptions

1. **Static Data**: Orders data doesn't change after startup (no real-time updates needed)
2. **Missing Values**: NaN in category columns means "item not purchased" (filled with 0)
3. **Memory Capacity**: Server has sufficient RAM to hold entire dataset (~few MB for 5K orders)
4. **Single Data Source**: All data comes from one CSV file (no database integration needed)
5. **Read-Only Operations**: API only reads data, no mutations or write operations

### Key Design Decisions & Tradeoffs

**1. In-Memory Data Loading**

- **Decision**: Load CSV once at startup into memory
- **Pros**: Fast response times (10-50ms), no I/O overhead per request
- **Cons**: Higher memory usage, requires restart to refresh data
- **Tradeoff**: Chose speed over flexibility (acceptable for static datasets)

**2. On-Demand Computation vs Caching**

- **Decision**: Compute KPIs on every request rather than cache results
- **Pros**: Simple implementation, no cache invalidation logic, always fresh
- **Cons**: Slight computational overhead per request
- **Tradeoff**: Calculations are fast enough (~10ms) that caching complexity isn't justified

**3. Pandas vs Polars**

- **Decision**: Used Pandas for data processing
- **Pros**: Mature ecosystem, widely known, sufficient performance
- **Cons**: Polars would be faster for very large datasets
- **Tradeoff**: Chose familiarity and stability over marginal performance gains

**4. Global State for Data**

- **Decision**: Store DataFrame as module-level global variable
- **Pros**: Simple, works well with FastAPI lifespan
- **Cons**: Not ideal for dependency injection, harder to test
- **Tradeoff**: Simplicity over testability (mitigated with fixture-based test data injection)

**5. Type Conversion to Native Python**

- **Decision**: Convert numpy types to Python int/float before returning
- **Rationale**: Ensures proper JSON serialization (numpy types can cause issues)
- **Overhead**: Minimal, worth the reliability

---

## 📦 Dependencies

- **FastAPI** (0.109.2): Web framework
- **Uvicorn** (0.27.1): ASGI server
- **Pandas** (2.2.0): Data processing
- **Pytest** (8.0.0): Testing framework
- **httpx** (0.26.0): HTTP client for testing
- **Ruff** (0.2.1): Fast Python linter and formatter

---

## 👤 Author

**Muhammad Muneeb Alam**
