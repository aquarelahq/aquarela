from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import Connection


def _get_conn(request: Request) -> Iterator[Connection]:
    """One transaction per request: commits on success, rolls back on error."""
    with request.app.state.engine.begin() as conn:
        yield conn


Conn = Annotated[Connection, Depends(_get_conn)]
