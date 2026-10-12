
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="SecureApp API",
    description="A learning project for secure software development.",
    version="0.1.0",
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )

    return response

class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    price: float = Field(gt=0, le=1_000_000)


items: dict[int, dict] = {}
next_item_id = 1


@app.get("/")
def root():
    return {
        "application": "SecureApp",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/items", status_code=201)
def create_item(item: ItemCreate):
    global next_item_id

    item_id = next_item_id
    next_item_id += 1

    item_data = item.model_dump()
    items[item_id] = {"id": item_id, **item_data}

    return items[item_id]


@app.get("/items/{item_id}")
def get_item(item_id: int):
    item = items.get(item_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    return item
