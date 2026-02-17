# FinTrack API

![CI](https://github.com/CarlosAlbertoFurtado/fintrack-api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)

API de finanças pessoais. Categoriza transações automaticamente via GPT, gera relatórios e controla orçamento por categoria.

**🔗 [Demo rodando no Render](https://fintrack-api-vk5b.onrender.com/docs)**

---

Cansou de planilha que não categoriza direito. Comecei fazendo um script pra logar gastos num CSV, foi crescendo e virou uma API completa com banco, cache e IA.

Não tem frontend — é só API. Uso com Insomnia/Postman ou o Swagger que já vem embutido.

## O que faz

- CRUD de transações com filtros (data, tipo, categoria, busca por texto)
- **Categorização automática via GPT** — se não informar a categoria, o modelo chuta
- 12 categorias padrão criadas no cadastro do usuário
- Relatórios: resumo mensal, gasto por categoria com %, tendência mensal
- Orçamento por categoria — alerta quando bate 80% do limite
- Insights via IA — GPT analisa as últimas transações e dá dicas
- Auth JWT (access + refresh token)
- Cache Redis nos relatórios (TTL 5min)

## Stack

Python 3.12, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, Redis, Alembic, OpenAI, Pydantic v2, structlog, pytest + httpx, Docker, GitHub Actions.

## Estrutura

```
app/
├── domain/          # entidades e interfaces (sem deps externas)
├── application/     # use cases e DTOs
├── infrastructure/  # SQLAlchemy, Redis, OpenAI
├── presentation/    # rotas FastAPI, auth middleware, DI
└── shared/          # config, erros, segurança, logging
```

## Rodando

```bash
git clone https://github.com/CarlosAlbertoFurtado/fintrack-api.git && cd fintrack-api
cp .env.example .env

# docker
docker-compose up -d
docker-compose exec app alembic upgrade head

# ou local
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head && uvicorn app.main:app --reload
```

Docs: http://localhost:8000/docs

## API

```
POST   /api/auth/register        POST   /api/transactions
POST   /api/auth/login           GET    /api/transactions
GET    /api/auth/me              GET    /api/transactions/:id
                                 PUT    /api/transactions/:id
POST   /api/categories           DELETE /api/transactions/:id
GET    /api/categories
DELETE /api/categories/:id       POST   /api/budgets
                                 GET    /api/budgets?month=3&year=2026
GET    /api/reports/summary      DELETE /api/budgets/:id
GET    /api/reports/by-category
GET    /api/reports/monthly-trend
GET    /api/reports/insights
```

## Testes

```bash
pytest -v                  # tudo
pytest --cov=app           # com cobertura
```

53 testes. Cobertura tá em ~73% — domínio e use cases acima de 85%, infra e rotas mais baixo.

## TODO

- [x] Deploy no Render
- [ ] Dashboard simples pra ver relatórios

MIT
