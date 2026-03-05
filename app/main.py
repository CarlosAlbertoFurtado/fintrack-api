from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.shared.errors import AppError
from app.shared.logger import setup_logging, logger
from app.infrastructure.database.connection import connect_database, disconnect_database
from app.presentation.routes import auth, transactions, categories, reports

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting_api", port=settings.app_port, env=settings.app_env)
    await connect_database()
    yield
    logger.info("shutting_down")
    await disconnect_database()


app = FastAPI(
    title="FinTrack API",
    description="Personal finance management API with AI-powered categorization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.message},
    )


@app.exception_handler(Exception)
async def handle_unexpected(request: Request, exc: Exception):
    logger.error("unhandled_error", error=str(exc))
    body = {"status": "error", "message": "Internal server error"}
    if settings.debug:
        body["debug"] = str(exc)
    return JSONResponse(status_code=500, content=body)


@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "1.0.0"}


app.include_router(auth.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
