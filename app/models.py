from pydantic import BaseModel, Field, validator


class Customer(BaseModel):
    firstName: str = Field(..., min_length=1, description="Customer's first name")
    lastName: str = Field(..., min_length=1, description="Customer's last name")
    age: int = Field(..., ge=18, description="Customer's age (must be 18 or older)")
    id: int = Field(..., ge=1, description="Unique customer ID")

    @validator("firstName", "lastName")
    def validate_names(cls, v):
        if v.strip() == "":
            raise ValueError("Name cannot be empty or only whitespace")
        return v.strip()


class CustomerResponse(BaseModel):
    customers: list[Customer]
    total: int