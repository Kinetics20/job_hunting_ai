from fastapi import FastAPI, Depends


app = FastAPI(title="Job Hunting AI", version="1.0.0")


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
