import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents, db
from schemas import CrackerProduct, Order

app = FastAPI(title="Crackers Shop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Helpers
# -----------------------------

def serialize_doc(doc: dict) -> dict:
    d = dict(doc)
    if d.get("_id") is not None:
        d["id"] = str(d.pop("_id"))
    return d


def seed_crackers_if_empty() -> None:
    if db is None:
        return
    count = db["crackerproduct"].count_documents({})
    if count == 0:
        samples = [
            {
                "name": "Sparklers Pack (10)",
                "description": "Bright, long-lasting sparklers perfect for celebrations.",
                "price": 2.99,
                "category": "Sparklers",
                "image": "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=800&auto=format&fit=crop",
                "in_stock": True,
                "rating": 4.8,
            },
            {
                "name": "Flower Pots (Medium)",
                "description": "Colorful fountain with safe height and vibrant effects.",
                "price": 4.5,
                "category": "Flower Pots",
                "image": "https://images.unsplash.com/photo-1508057198894-247b23fe5ade?q=80&w=800&auto=format&fit=crop",
                "in_stock": True,
                "rating": 4.6,
            },
            {
                "name": "Ground Spinners (5)",
                "description": "Fun spinning wheels with multi-color trails.",
                "price": 3.25,
                "category": "Ground Spinners",
                "image": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?q=80&w=800&auto=format&fit=crop",
                "in_stock": True,
                "rating": 4.4,
            },
            {
                "name": "Sky Rockets (3)",
                "description": "High-flying rockets with beautiful bursts.",
                "price": 7.99,
                "category": "Rockets",
                "image": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=800&auto=format&fit=crop",
                "in_stock": True,
                "rating": 4.7,
            },
        ]
        for s in samples:
            create_document("crackerproduct", s)


# -----------------------------
# Core
# -----------------------------

@app.get("/")
def read_root():
    return {"message": "Crackers Shop API is running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os

    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# -----------------------------
# Schemas endpoint for viewer
# -----------------------------
class SchemaResponse(BaseModel):
    name: str
    schema: dict


@app.get("/schema", response_model=List[SchemaResponse])
def get_schema():
    models = [CrackerProduct, Order]
    result = []
    for m in models:
        result.append({
            "name": m.__name__,
            "schema": m.model_json_schema(),
        })
    return result


# -----------------------------
# Catalog Endpoints
# -----------------------------

@app.get("/api/crackers")
def list_crackers(category: Optional[str] = None):
    seed_crackers_if_empty()
    flt = {"category": category} if category else {}
    items = get_documents("crackerproduct", flt)
    return [serialize_doc(x) for x in items]


@app.post("/api/crackers")
def create_cracker(product: CrackerProduct):
    pid = create_document("crackerproduct", product)
    return {"id": pid}


@app.get("/api/crackers/{product_id}")
def get_cracker(product_id: str):
    from bson import ObjectId

    try:
        obj = db["crackerproduct"].find_one({"_id": ObjectId(product_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product id")

    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return serialize_doc(obj)


# -----------------------------
# Orders Endpoints
# -----------------------------

@app.post("/api/orders")
def create_order(order: Order):
    order_id = create_document("order", order)
    return {"order_id": order_id, "status": "received"}


@app.get("/api/orders")
def list_orders(limit: int = 50):
    docs = get_documents("order", {}, limit=limit)
    return [serialize_doc(d) for d in docs]


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
