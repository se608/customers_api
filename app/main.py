import uvicorn

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from app.models import Customer, CustomerResponse
from app.storage import storage


app = FastAPI(
    title="Customers API",
    description="A REST API to manage customers with sorted storage",
    version="1.0.0"
)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    try:
        return {"message": "Customers API is running", "total_customers": storage.get_customer_count()}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving health status"
        )


@app.post("/customers", status_code=status.HTTP_201_CREATED, tags=["Customers"])
async def create_customers(customers: list[Customer]):
    """
    Create multiple customers. Validates all customers and maintains sorted order.

    - Validation Rules:
        - All fields must be provided
        - Age must be 18 or older
        - ID must be unique (not used before)
    - Sorting: Customers are stored sorted by lastName, then firstName
    """
    try:
        if not customers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request must contain at least one customer"
            )

        storage.add_customers(customers)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": f"Successfully created {len(customers)} customers",
                "total_customers": storage.get_customer_count()
            }
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/customers", response_model=CustomerResponse, tags=["Customers"])
async def get_customers():
    """
    Get all customers sorted by lastName, then firstName.

    Returns the complete array of customers with all fields.
    """
    try:
        customers_data = storage.get_all_customers()
        return CustomerResponse(
            customers=[Customer(**customer) for customer in customers_data],
            total=len(customers_data)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving customers"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
