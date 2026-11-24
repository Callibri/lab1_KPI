from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app.routers import analytics, auth, movies, reports
from app.validators import ValidationFailed


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Box Office Analytics (Lab 1: CRUD)", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(reports.router)
app.include_router(analytics.router)


@app.exception_handler(ValidationFailed)
async def validation_failed_handler(_: Request, exc: ValidationFailed):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def request_validation_handler(_: Request, exc: RequestValidationError):
    errors = [{"loc": list(e["loc"]), "msg": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=400, content={"detail": errors})
