import re
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field, field_validator

from aquarela.deps import Conn
from aquarela.errors import ApiError
from aquarela.repositories.classes import ClassRepository
from aquarela.repositories.projects import ProjectRepository

router = APIRouter(prefix="/api/projects/{pid}/classes")

COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
KEY = re.compile(r"^[1-9]$")


def _check(pattern: re.Pattern, v: str | None, what: str) -> str | None:
    if v is not None and not pattern.match(v):
        raise ValueError(what)
    return v


class ClassIn(BaseModel):
    name: str = Field(min_length=1)
    color: str
    key: str | None = None

    @field_validator("name")
    @classmethod
    def _name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v

    @field_validator("color")
    @classmethod
    def _color(cls, v: str) -> str:
        return _check(COLOR, v, "must look like #e86a92")

    @field_validator("key")
    @classmethod
    def _key(cls, v: str | None) -> str | None:
        return _check(KEY, v, "must be a digit from 1 to 9")


class ClassPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    color: str | None = None
    key: str | None = None
    position: int | None = Field(default=None, ge=0)

    _color = field_validator("color")(
        lambda cls, v: _check(COLOR, v, "must look like #e86a92")
    )
    _key = field_validator("key")(
        lambda cls, v: _check(KEY, v, "must be a digit from 1 to 9")
    )


def repo(pid: str, conn: Conn) -> ClassRepository:
    ProjectRepository(conn).get(pid)  # 404 when the project does not exist
    return ClassRepository(conn, pid)


Classes = Annotated[ClassRepository, Depends(repo)]


@router.get("")
def list_classes(classes: Classes) -> list[dict]:
    return classes.list()


@router.post("", status_code=201)
def create_class(data: ClassIn, classes: Classes) -> dict:
    return classes.create(data.name, data.color, data.key)


@router.patch("/{cid}")
def update_class(cid: str, data: ClassPatch, classes: Classes) -> dict:
    sent = data.model_fields_set
    if ("name" in sent and data.name is None) or (
        "color" in sent and data.color is None
    ):
        raise ApiError(422, "invalid_request", "name and color cannot be null.")
    changes = {f: getattr(data, f) for f in ("name", "color", "key") if f in sent}
    if "name" in changes:
        changes["name"] = changes["name"].strip()
        if not changes["name"]:
            raise ApiError(422, "invalid_request", "name: must not be blank")
    return classes.update(cid, changes, data.position)


@router.delete("/{cid}", status_code=204)
def delete_class(cid: str, classes: Classes) -> Response:
    classes.delete(cid)
    return Response(status_code=204)
