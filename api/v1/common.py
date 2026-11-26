from typing import Annotated

from fastapi import Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, func, select


class Pagination:
    def __init__(
        self,
        limit: int = Query(20, ge=1, le=100, description="Cantidad máxima de resultados por página (1–100)."),
        offset: int = Query(0, ge=0, description="Cantidad de resultados que se omiten antes de iniciar la página."),
    ):
        self.limit = limit
        self.offset = offset


PaginationDep = Annotated[Pagination, Depends()]


def paginate(session: Session, stmt, page: Pagination, response: Response) -> list:
    total = session.exec(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    ).one()
    response.headers["X-Total-Count"] = str(total)
    return list(session.exec(stmt.offset(page.offset).limit(page.limit)).all())


def get_or_404(session: Session, model, pk, name: str):
    obj = session.get(model, pk)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"{name} not found")
    return obj


def apply_update(obj, data: SQLModel) -> None:
    update_data = data.model_dump(exclude_unset=True)
    if any(value is None for value in update_data.values()):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "All fields cannot be null or empty",
        )
    for field, value in update_data.items():
        setattr(obj, field, value)


def commit_or_409(session: Session, detail: str) -> None:
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail) from None