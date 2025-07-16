from fastapi import FastAPI, Depends

from .api import routers


app = FastAPI(title="Job Hunting AI", version="1.0.0")


for router in routers:
    app.include_router(router)

@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
