from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlmodel import Session, col, select

from api.v1.common import (
    PaginationDep,
    apply_update,
    commit_or_409,
    get_or_404,
    paginate,
)
from api.v1.dependencies import get_current_user
from db.database import get_session
from models import User, Vehicle, VehicleDevice
from models.enums import VehicleDeviceType
from schemas.vehicle_device import (
    VehicleDeviceCreate,
    VehicleDeviceResponse,
    VehicleDeviceUpdate,
)

router = APIRouter()

DUPLICATE_DETAIL = "There is already another device registered with the same serial number"


@router.post(
    "/",
    response_model=VehicleDeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar dispositivo",
    description="Asocia un dispositivo HUB o NODE a un vehículo existente; el número de serie debe ser único.",
)
def register_device(
    device_data: VehicleDeviceCreate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> VehicleDevice:
    get_or_404(session, Vehicle, device_data.vehicle_id, "Vehicle")

    device = VehicleDevice(**device_data.model_dump(), is_active=False)
    session.add(device)
    commit_or_409(session, DUPLICATE_DETAIL)
    session.refresh(device)
    return device


@router.get(
    "/",
    response_model=list[VehicleDeviceResponse],
    summary="Listar dispositivos",
    description="Devuelve dispositivos paginados y admite filtros por vehículo, tipo y estados.",
)
def get_devices(
    response: Response,
    page: PaginationDep,
    vehicle_id: Optional[UUID] = Query(default=None, description="Filtra por UUID del vehículo asociado."),
    device_type: Optional[VehicleDeviceType] = Query(default=None, alias="type", description="Filtra por tipo HUB o NODE."),
    is_active: Optional[bool] = Query(default=None, description="Filtra por estado activo del dispositivo."),
    is_enabled: Optional[bool] = Query(default=None, description="Filtra por habilitación del dispositivo."),
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> list[VehicleDevice]:
    statement = select(VehicleDevice)

    if vehicle_id is not None:
        statement = statement.where(VehicleDevice.vehicle_id == vehicle_id)
    if device_type is not None:
        statement = statement.where(VehicleDevice.type == device_type)
    if is_active is not None:
        statement = statement.where(VehicleDevice.is_active == is_active)
    if is_enabled is not None:
        statement = statement.where(VehicleDevice.is_enabled == is_enabled)

    statement = statement.order_by(col(VehicleDevice.registered_at).desc())
    return paginate(session, statement, page, response)


@router.get(
    "/{device_id}",
    response_model=VehicleDeviceResponse,
    summary="Consultar dispositivo",
    description="Obtiene un dispositivo por UUID.",
)
def get_device(
    device_id: Annotated[UUID, Path(description="UUID del dispositivo.")],
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> VehicleDevice:
    return get_or_404(session, VehicleDevice, device_id, "Device")


@router.put(
    "/{device_id}",
    response_model=VehicleDeviceResponse,
    summary="Actualizar dispositivo",
    description="Actualiza el vehículo asociado, número de serie, etiqueta, tipo o habilitación.",
)
def update_device(
    device_id: Annotated[UUID, Path(description="UUID del dispositivo que se desea actualizar.")],
    device_data: VehicleDeviceUpdate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> VehicleDevice:
    device = get_or_404(session, VehicleDevice, device_id, "Device")

    if device_data.vehicle_id is not None and device_data.vehicle_id != device.vehicle_id:
        get_or_404(session, Vehicle, device_data.vehicle_id, "Vehicle")

    apply_update(device, device_data)
    session.add(device)
    commit_or_409(session, DUPLICATE_DETAIL)
    session.refresh(device)
    return device