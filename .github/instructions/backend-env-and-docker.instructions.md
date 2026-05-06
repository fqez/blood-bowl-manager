---
description: "Use when modifying or testing the blood-bowl-manager backend, Python/FastAPI code, requirements, or Docker backend files. Enforces the bbman virtual environment and API container rebuild workflow."
applyTo: "**/*.py,requirements.txt,railway.toml,Procfile,docker/**"
---
# Backend environment and Docker workflow

- For backend validation/tests, use the existing virtual environment at `C:\Users\Franchoped\Software\bbman`.
- Run Python commands with `C:\Users\Franchoped\Software\bbman\Scripts\python.exe` from the backend workspace (`C:\Users\Franchoped\Software\blood-bowl-manager`).
- Do not create a new backend virtual environment unless the user explicitly asks.
- After any backend code/config/dependency change, rebuild and restart the backend API container so changes are persisted and testable:
  - From the backend workspace, run Docker Compose with `docker/docker-compose.yml`.
  - Rebuild at least the `api` service.
- After rebuilding, check that `docker-api-1` is running and inspect recent API logs for startup errors.
