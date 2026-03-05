# Contributing

Thanks for considering contributing! Here's how to get started.

## Setup

```bash
git clone https://github.com/CarlosAlbertoFurtado/fintrack-api.git
cd fintrack-api
cp .env.example .env
python -m venv venv && source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head
```

## Running tests

```bash
pytest                    # all tests
pytest --cov=app          # with coverage
pytest tests/unit/ -v     # unit tests only
```

## Code style

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting. Run before committing:

```bash
ruff check app/ tests/
ruff format app/ tests/
```

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `test:` adding tests
- `refactor:` code change that neither fixes a bug nor adds a feature

## Pull requests

1. Fork the repo and create a branch from `main`
2. Add tests for any new functionality
3. Ensure all tests pass and linting is clean
4. Open a PR with a clear description of the change
