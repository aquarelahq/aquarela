from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field, field_validator

from aquarela.deps import Conn
from aquarela.errors import ApiError
from aquarela.repositories.projects import ProjectRepository

router = APIRouter(prefix="/api/projects")


class Name(BaseModel):
    name: str = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v


class ProjectIn(Name):
    path: str = Field(min_length=1)


def repo(conn: Conn) -> ProjectRepository:
    return ProjectRepository(conn)


Projects = Annotated[ProjectRepository, Depends(repo)]


@router.get("")
def list_projects(projects: Projects) -> list[dict]:
    return projects.list()


@router.post("", status_code=201)
def create_project(data: ProjectIn, projects: Projects) -> dict:
    root = Path(data.path).expanduser()
    if not root.is_dir():
        raise ApiError(422, "invalid_path", "The path is not a folder.")
    return projects.create(data.name, str(root.resolve()))


@router.get("/{pid}")
def project_detail(pid: str, projects: Projects) -> dict:
    return {**projects.get(pid), "image_counts": projects.image_counts(pid)}


@router.patch("/{pid}")
def rename_project(pid: str, data: Name, projects: Projects) -> dict:
    return projects.rename(pid, data.name)


@router.delete("/{pid}", status_code=204)
def delete_project(pid: str, projects: Projects) -> Response:
    projects.delete(pid)
    return Response(status_code=204)
