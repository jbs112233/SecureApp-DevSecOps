# SecureApp DevSecOps

This is learning and portfolio project where I took time to demonstrate secure API development, automated testing, dependency auditing, static security analysis, containerization, and CI/CD practices.

## My Goals

- Build an API with FastAPI.
- Include user registration and JWT-based authentication.
- Store the application data with SQLAlchemy and SQLite.
- Manage database changes with Alembic migrations.
- Apply security controls and automated tests.
- Integrate security checks into GitHub Actions.
- Run the application in a Docker container using a non-root user.

## Technology Stack

- Language: Python
- API: FastAPI
- Database: SQLite and SQLAlchemy
- Migrations: Alembic
- Authentication: JWT and password hashing
- Testing: pytest
- Security scanning: Bandit, pip-audit, Gitleaks, and Trivy
- Containerization: Docker
- CI/CD: GitHub Actions

## Security Controls

The project includes:

- Password hashing and token-based authentication.
- Authentication and access controls for application endpoints.
- Request rate limiting.
- HTTP security headers.
- Environment-based configuration for the JWT signing key.
- Automated tests for application behavior and security controls.
- Dependency and source-code security scanning.
- Docker execution as a non-root user.

## Local Development

Use Windows PowerShell to run these commands and get your project set up yourself!

Create and activate a virtual environment:

python -m venv .venv
.\.venv\Scripts\Activate.ps1

Install the project dependencies:


python -m pip install -r requirements.txt


Configure a strong signing key in your current PowerShell session:


python -c "import secrets; print(secrets.token_urlsafe(48))"
$env:SECUREAPP_SECRET_KEY = "REPLACE_WITH_YOUR_GENERATED_SECRET"


Replace the placeholder with the generated value. Do not commit secrets or paste them into project documentation!!!!

Run the automated tests:


python -m pytest -q





## Docker Deployment

For image building, database migrations, health checks, and container shutdown instructions, go into the repository and find the deployment rulebook!

The container is configured to run as a non-root user. The SQLite database uses a persistent Docker volume mounted at /data.



## CI/CD and Security Checks

The GitHub Actions workflow is located in .github/workflows/ci.yml. It runs automated tests and configured security checks as part of the project's continuous integration process.


Local verification during the project included:

-pytest: 47 tests passed.
-Bandit: zero issues identified in a targeted scan of 548 lines of application and migration code.
-pip-audit: no known dependency vulnerabilities reported.

These results describe checks run during development; they are not a guarantee that the application is free of all vulnerabilities.


## Documentation

- [Deployment Runbook](docs/deployment.md)
- [Threat Model](THREAT_MODEL.md)


## Project Status and Limitations

To reiterate, this is a learning and portfolio project, not a production-ready security certification. Production deployment would require additional review of secrets management, database operations, monitoring, infrastructure configuration, and operational controls. 

The test suite has reported a SlowAPI deprecation warning related to asyncio.iscoroutinefunction; it did not cause the tests to fail.

As well as 3 warnings related to configuration errors, which also did not lead to failed test.
