from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from sqlalchemy import create_engine, event

from aquarela import classes, errors, projects
from aquarela.db import database_url, migrate


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    url = database_url()
    migrate(url)
    engine = create_engine(url)

    @event.listens_for(engine, "connect")
    def _foreign_keys(dbapi_connection, _):
        if engine.dialect.name == "sqlite":
            dbapi_connection.execute("PRAGMA foreign_keys = ON")

    app.state.engine = engine
    yield
    engine.dispose()


app = FastAPI(title="Aquarela", lifespan=lifespan)
errors.install(app)
app.include_router(projects.router)
app.include_router(classes.router)


@app.get("/api/health", response_class=PlainTextResponse)
def health() -> str:
    return "ok"


def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8080)
