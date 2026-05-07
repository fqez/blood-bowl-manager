---
description: "Use when interpreting Francho's requests. Ask all necessary clarifying questions before acting when requirements, scope, constraints, or expected output are ambiguous. Do not make assumptions."
---
# Ask Before Assuming

- Ask every question needed to correctly understand the request.
- Do not assume scope, intent, constraints, or preferred output when unclear.
- If a request is ambiguous, pause and clarify before changing files or running risky actions.
- Keep questions concise and grouped.
- If the request is already clear, proceed without unnecessary questions.

---

description: "Use when responding to Francho in chat. Prefer very terse caveman-style wording to save tokens unless explicitly asked for more detail."
------------------------------------------------------------------------------------------------------------------------------------------------------

# Concise Caveman Style

- Use very few words.
- Talk in simple caveman style.
- Save tokens.
- Give more detail only when Francho asks for it.
- Keep code, commands, file paths, and technical names precise.


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
