from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from aquarela.db import migrate


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    migrate()
    yield


app = FastAPI(title="Aquarela", lifespan=lifespan)


@app.get("/api/health", response_class=PlainTextResponse)
def health() -> str:
    return "ok"


def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8080)
