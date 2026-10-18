


FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SECUREAPP_DATABASE_URL=sqlite:////data/secureapp.db

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app.py auth.py auth_routes.py config.py logging_config.py database.py models.py rate_limiter.py ./
COPY alembic.ini ./
COPY migrations/ ./migrations/

RUN adduser -D -u 10001 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data

USER 10001

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]


