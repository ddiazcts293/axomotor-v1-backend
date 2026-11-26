from typing import Optional, Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from botocore.exceptions import ClientError

from api.v1.common import get_or_404
from api.v1.dependencies import get_web_or_bot_user
from db.database import get_session
from core.storage import validate_and_upload_file, delete_file
from models import User, IncidentMediaFile, Incident, UserRole, MediaType
from schemas.incident_media import IncidentMediaResponse


router = APIRouter()

CONFLICT_DETAIL = "The incident media could not be saved due to a conflicting or invalid reference"

@router.post(
    "/",
    response_model=IncidentMediaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_media_file(
    incident_id: Annotated[UUID, Form()],
    type: Annotated[MediaType, Form()],
    file: UploadFile = File(...),
    file_metadata: Annotated[Optional[dict], Form()] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_web_or_bot_user),
) -> IncidentMediaFile:
    get_or_404(session, Incident, incident_id, "Incident")

    try:
        result = await validate_and_upload_file(file)
    except ClientError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='The file could not been uploaded due to an internal error'
        )

    media = IncidentMediaFile(
        incident_id=incident_id,
        object_key=result.key,
        type=type,
        file_metadata=file_metadata,
        uploaded_by_id=current_user.user_id
    )

    session.add(media)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        delete_file(result.key)

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=CONFLICT_DETAIL
        )

    session.refresh(media)
    return media


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media_file(
    file_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_web_or_bot_user)
) -> None:
    media = get_or_404(session, IncidentMediaFile, file_id, "Incident Media")

    if media.uploaded_by_id != current_user.user_id and \
        current_user.role == UserRole.driver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Cannot delete files that are not uploaded by the user'
        )

    try:
        delete_file(media.object_key)
    except ClientError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='The file could not been deleted due to an internal error'
        )

    session.delete(media)
    session.commit()
