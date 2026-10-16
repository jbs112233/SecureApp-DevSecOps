import logging
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from auth_routes import get_current_user, router as auth_router
from config import ITEM_RATE_LIMIT
from database import get_db
from logging_config import configure_logging
from models import Item, User
from rate_limiter import limiter


configure_logging()
logger = logging.getLogger("secureapp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    alembic_config = Config("alembic.ini")
    command.upgrade(alembic_config, "head")
    logger.info("SecureApp API started")
    yield
    logger.info("SecureApp API stopped")


app = FastAPI(
    title="SecureApp API",
    description="A project where I dive into secure software development.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth_router)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
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
@limiter.limit(
    ITEM_RATE_LIMIT,
    key_func=lambda request: f"items:{request.client.host}",
)
def create_item(
    request: Request,
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_item = Item(
        **item.model_dump(),
        owner_id=current_user.id,
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    logger.info(
        "Item created: item_id=%s owner_id=%s",
        db_item.id,
        current_user.id,
    )

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
    current_user: User = Depends(get_current_user),
):
    item = db.get(Item, item_id)

    if item is None or item.owner_id != current_user.id:
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
