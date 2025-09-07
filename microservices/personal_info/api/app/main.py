from fastapi import FastAPI

from .routers import routers

app = FastAPI(
    title="Personal Info API",
    version="1.0.1",
)

for router in routers:
    app.include_router(router)


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}