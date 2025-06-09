# Customers API

A REST API to manage customers with automatic sorting and persistence. Built with FastAPI.

## 🐳 Docker Usage

### Start the API
```bash
docker compose up -d
```

### Run Load Test Simulator
```bash
docker compose build simulator
docker compose --profile simulator run --rm simulator
```

### View API Documentation
Open http://localhost:8000/docs

### Stop Services
```bash
docker compose down
```

## 🧪 Testing Against Production API

If you want to test against a production API (without Docker):

```bash
pip install -r requirements.txt

# First, check existing customers to avoid ID conflicts
curl https://customersapi-production.up.railway.app/customers

# Run simulator with a starting ID higher than existing ones
API_BASE_URL=https://customersapi-production.up.railway.app STARTING_CUSTOMER_ID=1 POST_REQUESTS_COUNT=3 GET_REQUESTS_COUNT=4 python run_simulation.py
```

## 🔧 API Endpoints

- **GET /** - Health check
- **POST /customers** - Create customers (batch)
- **GET /customers** - Get all customers (sorted)

Data persists in `./data/customers.json`
