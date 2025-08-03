from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from app.core.events import startup_handler, shutdown_handler
from app.routers import routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_handler(app)
    yield
    await shutdown_handler(app)


app = FastAPI(title="Auth miscroservice", version="1.0.0", lifespan=lifespan)

for router in routers:
    app.include_router(router)


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
