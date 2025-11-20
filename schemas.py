"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# --------------------------------------------------
# Crackers Shop Specific Schemas
# --------------------------------------------------

class CrackerProduct(BaseModel):
    """Collection: "crackerproduct"
    Represents a firecracker product in the catalog
    """
    name: str = Field(..., description="Display name of the cracker")
    description: Optional[str] = Field(None, description="Short description")
    price: float = Field(..., ge=0, description="Unit price in local currency")
    category: str = Field(..., description="e.g., Sparklers, Flower Pots, Rockets, Bombs")
    image: Optional[str] = Field(None, description="Public image URL")
    in_stock: bool = Field(True, description="Whether available for sale")
    rating: Optional[float] = Field(4.5, ge=0, le=5, description="Average rating")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="Referenced crackerproduct _id as string")
    name: str = Field(..., description="Snapshot of product name")
    price: float = Field(..., ge=0, description="Unit price at purchase time")
    quantity: int = Field(..., ge=1, description="Quantity ordered")

class CustomerInfo(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: str
    city: str
    pincode: str

class Order(BaseModel):
    """Collection: "order"
    Represents a customer's order
    """
    items: List[OrderItem]
    customer: CustomerInfo
    total_amount: float = Field(..., ge=0)
    status: str = Field("pending", description="pending, confirmed, shipped, delivered, cancelled")
    notes: Optional[str] = None

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
