# SecureApp Threat Model

## 1. Purpose

SecureApp is a learning project that provides a FastAPI REST API
for creating and retrieving items. The project demonstrates
secure software development and automated security testing.

## 2. Assets to Protect

- Application availability and integrity
- Item data stored by the application
- Integrity of source code and dependencies
- GitHub repository and CI/CD workflow integrity
- Secrets and credentials used during development or deployment

## 3. System Components

- FastAPI application (`app.py`)
- Pydantic request validation
- In-memory item storage
- Python dependencies
- Docker container running as a non-root user
- GitHub Actions CI workflow
- Bandit, pip-audit, Trivy, and Gitleaks

## 4. Trust Boundaries

- External clients send HTTP requests to the API.
- Request data crosses into the application through API endpoints.
- The application depends on third-party Python packages.
- GitHub Actions executes workflow steps using repository code.
- The container image includes the operating system and Python packages.

## 5. Threats and Mitigations

| Threat                          | Potential impact                                                 | Planned mitigation                                  |
| ------------------------------- | ---------------------------------------------------------------- | --------------------------------------------------- |
| Malformed input                 | Invalid or unexpected application behavior                       | Pydantic validation and negative tests              |
| Excessive requests              | Resource exhaustion or service disruption                        | Rate limiting                                       |
| Browser-based attacks           | Unsafe browser interactions if the API is used by a web frontend | Appropriate security headers and CORS configuration |
| Vulnerable dependencies         | Exploitation of known software flaws                             | pip-audit and dependency updates                    |
| Vulnerable container packages   | Compromise of the runtime environment                            | Trivy scanning and base-image updates               |
| Accidental secret exposure      | Unauthorized access to services or accounts                      | Gitleaks and secret-management practices            |
| Unauthorized repository changes | Malicious code entering the build                                | Branch protection and required CI checks            |
| Container compromise            | Increased impact if an attacker gains execution                  | Non-root user and least privilege                   |

## 6. Current Limitations

- The API does not currently implement authentication or authorization.
- Item data is stored in memory and is not persistent.
- The API is not intended for sensitive or production data.
- Rate limiting and security response headers still need to be implemented and tested.
- Security scanners cannot detect every vulnerability.

## 7. Security Testing Plan

- Verify request validation for invalid inputs.
- Test appropriate HTTP security headers.
- Test rate limiting behavior.
- Run automated tests in GitHub Actions.
- Scan Python dependencies and the container image.
- Review and document new findings before release.

## 8. Scope

This threat model describes the current learning application.
It must be updated when authentication, persistent storage,
external integrations, or production deployment are introduced. 
