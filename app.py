
import logging

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from database import Base, engine, get_db
from models import Item
from logging_config import configure_logging


configure_logging()
logger = logging.getLogger("secureapp")


from alembic import command
from alembic.config import Config


@asynccontextmanager
async def lifespan(app: FastAPI):
    alembic_config = Config("alembic.ini")
    command.upgrade(alembic_config, "head")

    logger.info("SecureApp API started")
    yield
    logger.info("SecureApp API stopped")


app = FastAPI(
    title="SecureApp API",
    description="A learning project for secure software development.",
    version="0.1.0",
    lifespan=lifespan,
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
def create_item(
    request: Request,
    item: ItemCreate,
    db: Session = Depends(get_db),
):
    db_item = Item(**item.model_dump())

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    logger.info("Item created: item_id=%s", db_item.id)

    return {
        "id": db_item.id,
        "name": db_item.name,
        "description": db_item.description,
        "price": db_item.price,
    }


@app.get("/items/{item_id}")
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    item = db.get(Item, item_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
    }
