# Deployment Process

## Purpose

This will show you how to build, migrate, run, verify, and stop the SecureApp Docker container locally.

## Prerequisites

- Make sure docker is running.
- Open PowerShell terminal.
- Find the Dockerfile, requirements.txt, and Alembic migration files.
- Generate a valid `SECUREAPP_SECRET_KEY`.
- Make sure a consistent docker volume is available for the SQLite database.


## COMMANDS

## 1. Build the image

docker build -t secureapp:local .

## 2. Create a persistent database volume

docker volume create secureapp-data

## 3. Configure the signing key

python -c "import secrets; print(secrets.token_urlsafe(48))"

$env:SECUREAPP_SECRET_KEY = "REPLACE_WITH_YOUR_GENERATED_SECRET"


## 4. Apply database migrations


docker run --rm `
  --mount source=secureapp-data,target=/data `
  -e SECUREAPP_SECRET_KEY `
  secureapp:local `
  python -m alembic upgrade head


## 5. Start the API


docker run -d `
  --name secureapp `
  --mount source=secureapp-data,target=/data `
  -p 8000:8000 `
  -e SECUREAPP_SECRET_KEY `
  secureapp:local

## 6. Verify startup and health

docker ps --filter "name=secureapp"


Invoke-RestMethod http://localhost:8000/health


docker logs secureapp

docker exec secureapp id


## 7. Stop the API


docker stop secureapp
docker rm secureapp


## Security notes

- Keep secrets out of source control and Docker images.
- Use a new, strong signing key for each environment.
- Keep the database volume mounted at /data for migrations and normal API operation.
- Run migrations explicitly before starting the API.
- Treat local development settings as a baseline, not a production deployment configuration.
