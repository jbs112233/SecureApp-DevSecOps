
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


app = FastAPI(
    title="SecureApp API",
    description="A learning project for secure software development.",
    version="0.1.0",
)
limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
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
@limiter.limit("5/minute")
def create_item(request: Request, item: ItemCreate):
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
