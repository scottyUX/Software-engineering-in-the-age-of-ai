# System Intent & Architectural Boundaries

## Purpose
The **Link Shortener** is a lightweight, agent-friendly microservice designed to convert long URLs into deterministic or custom short tokens, redirect visitors, and provide inspectable metadata.

---

## Architectural Principles & Guarantees

1. **Lightweight Simplicity:**
   - The application relies on an in-memory dictionary store for zero-dependency development and sub-millisecond local test execution.
   - External databases (Redis, PostgreSQL, SQLite) should not be introduced without formal task requirements.

2. **Strict Validation & Determinism:**
   - All inbound payloads must be validated using Pydantic schemas.
   - Long URLs must be valid HTTP/HTTPS URLs.
   - Short code generation uses a secure random or custom alphanumeric token policy.

3. **HTTP Status Code Precision:**
   - Successful link generation: `200 OK`
   - Redirection to target URL: `307 Temporary Redirect`
   - Custom alias conflict: `409 Conflict` (when custom alias already exists)
   - Missing link: `404 Not Found`
   - Expired link: `410 Gone` (if expiry is enabled)

4. **Agent-Facing Expectations:**
   - Any agent operating in this repository must keep changes small, modular, and backed by regression tests.
   - No code change is accepted without passing the pre-commit lint and test gate.
