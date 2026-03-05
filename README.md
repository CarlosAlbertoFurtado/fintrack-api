# FinTrack API

Personal finance REST API with AI-powered transaction categorization.

Built with **FastAPI**, **PostgreSQL**, **Redis**, and **OpenAI**.

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Why this exists

I built this because most personal finance tools either:
- Don't categorize transactions well (or at all)
- Are bloated desktop apps when all you need is an API
- Don't give you actual insights about your spending patterns

FinTrack solves this by letting you log transactions and having GPT auto-categorize them based on the description. It also generates monthly spending insights in Portuguese.

## What it does

- **Transaction tracking** — full CRUD with filters (date range, type, category, text search)
- **AI categorization** — if you don't pick a category, OpenAI suggests one based on the description
- **12 default categories** — created automatically when you sign up (Alimentação, Transporte, Moradia, etc.)
- **Financial reports** — monthly summary, spending by category with percentages, income vs expense trends
- **Budget alerts** — set monthly limits per category, get warned at 80% (configurable)
- **AI insights** — GPT analyzes your recent transactions and gives actionable tips
- **JWT auth** — access + refresh tokens, role-based access

## Tech stack

| What | Why |
|------|-----|
| Python 3.12 | Async from the ground up |
| FastAPI | Auto-generated OpenAPI docs, dependency injection, async |
| SQLAlchemy 2.0 | Async ORM with proper typing |
| PostgreSQL | Reliable, great for financial data |
| Redis | Cache summaries (5min TTL), avoids hitting the DB on every dashboard load |
| Alembic | DB migrations |
| OpenAI | Transaction categorization + spending insights |
| Pydantic v2 | Request/response validation |
| structlog | JSON logs in prod, colored output in dev |
| pytest | Unit tests for domain entities |
| Docker | Dev environment with docker-compose |
| GitHub Actions | CI: ruff lint → pytest → docker build |

## Architecture

Clean Architecture with 4 layers:

```
app/
├── domain/          # Entities + repository interfaces (no deps)
├── application/     # Use cases + DTOs
├── infrastructure/  # SQLAlchemy repos, Redis cache, OpenAI service
├── presentation/    # FastAPI routes, auth middleware, DI
└── shared/          # Config, errors, security, logging
```

The idea is that you can swap SQLAlchemy for another ORM (or even a different DB) without touching the use cases — they only depend on the interfaces defined in `domain/`.

## Quick start

```bash
# clone
git clone https://github.com/CarlosAlbertoFurtado/fintrack-api.git
cd fintrack-api

# env vars
cp .env.example .env

# run with docker (recommended)
docker-compose up -d
docker-compose exec app alembic upgrade head

# or locally
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

API docs at http://localhost:8000/docs

## API overview

```
POST   /api/auth/register       → create account
POST   /api/auth/login          → get JWT tokens
GET    /api/auth/me             → current user

POST   /api/transactions        → create (AI auto-categorizes if no category)
GET    /api/transactions        → list with filters & pagination
GET    /api/transactions/:id    → get by id
PUT    /api/transactions/:id    → update
DELETE /api/transactions/:id    → delete

POST   /api/categories          → create custom category
GET    /api/categories          → list user's categories
DELETE /api/categories/:id      → delete (can't delete defaults)

GET    /api/reports/summary     → income/expenses/balance for period
GET    /api/reports/by-category → spending breakdown with percentages
GET    /api/reports/monthly-trend → income vs expenses over time
GET    /api/reports/insights    → AI-generated spending advice
```

## Running tests

```bash
pytest                        # all tests
pytest --cov=app              # with coverage
pytest tests/unit/ -v         # verbose
```

## Project structure

```
59 files total

domain/entities/     → User, Transaction, Category, Budget (dataclasses with validation)
domain/interfaces/   → Repository ABCs, cache/AI service contracts
application/         → RegisterUser, LoginUser, CreateTransaction, GetSummary
infrastructure/      → SQLAlchemy repos, Redis cache, OpenAI categorizer
presentation/        → 4 route modules, JWT middleware, DI container
tests/unit/          → entity validation tests (23 test cases)
```

## Known limitations / TODO

- [ ] Budget endpoints not wired up to routes yet (entity + repo ready)
- [ ] No email notifications (SMTP config exists but service not implemented)
- [ ] refresh token rotation endpoint missing
- [ ] Front-end not included (API only)

## License

MIT
