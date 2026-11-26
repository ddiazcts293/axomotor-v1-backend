from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from geoalchemy2.elements import WKTElement

from api.v1.dependencies import get_current_user
from db.database import get_session
from models import KnownLocation, User
from schemas.known_location import (
    KnownLocationCreate,
    KnownLocationUpdate,
    KnownLocationResponse
)
from utils.helpers import convert_vertices_to_string

router = APIRouter()

@router.post(
    "/",
    response_model=KnownLocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar ubicación conocida",
    description="Crea una ubicación con un polígono geográfico válido, cerrado y sin autointersecciones.",
)
def register_location(
    location_data: KnownLocationCreate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> KnownLocation:
    existing_location = session.exec(
        select(KnownLocation).where(KnownLocation.name == location_data.name)
    ).first()

    if existing_location:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already another location registered with the same name",
        )

    polygon_wkt = convert_vertices_to_string(location_data.location_area)
    location = KnownLocation(
        name = location_data.name,
        type = location_data.type,
        address = location_data.address,
        location_area=WKTElement(polygon_wkt, srid=4326)
    )

    session.add(location)

    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to save the location",
        ) from None

    session.refresh(location)
    return location

@router.get(
    "/",
    response_model=list[KnownLocationResponse],
    summary="Listar ubicaciones",
    description="Devuelve todas las ubicaciones conocidas registradas.",
)
def get_locations(
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> list[KnownLocation]:
    return list(session.exec(select(KnownLocation)).all())

@router.get(
    "/{location_id}",
    response_model=KnownLocationResponse,
    summary="Consultar ubicación",
    description="Obtiene una ubicación conocida por UUID.",
)
def get_location(
    location_id: Annotated[UUID, Path(description="UUID de la ubicación conocida.")],
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    location = session.get(KnownLocation, location_id)

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )
    return location

@router.put(
    "/{location_id}",
    response_model=KnownLocationResponse,
    summary="Actualizar ubicación",
    description="Actualiza los datos enviados; si se modifica el polígono, se valida su geometría.",
)
def update_location(
    location_id: Annotated[UUID, Path(description="UUID de la ubicación que se desea actualizar.")],
    location_data: KnownLocationUpdate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    location = session.get(KnownLocation, location_id)
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    update_data = location_data.model_dump(exclude_unset=True)
    if any(value is None for value in update_data.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="All fields cannot be null or empty",
        )

    if 'name' in update_data:
        duplicate = session.exec(
            select(KnownLocation).where(
                KnownLocation.location_id != location_id,
                KnownLocation.name == update_data.get('name', location.name)
            )
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="There is already another location registered with the same name"
            )

    if 'location_area' in update_data:
        vertices = update_data.pop('location_area')
        polygon_wkt = convert_vertices_to_string(vertices)
        location.location_area=WKTElement(polygon_wkt, srid=4326)

    for field, value in update_data.items():
        setattr(location, field, value)

    session.add(location)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to save the location",
        ) from None

    session.refresh(location)
    return location
