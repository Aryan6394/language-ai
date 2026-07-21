from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.schemas.language import LanguageResponse
from app.services.language_service import LanguageService

router = APIRouter(
    prefix="/languages",
    tags=["Languages"],
)


@router.get(
    "",
    response_model=list[LanguageResponse],
    summary="List supported languages",
)
async def list_languages(
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> list[LanguageResponse]:
    """
    Return every active language supported by the platform.
    """

    return await LanguageService.get_languages(db)