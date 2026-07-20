from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.dependencies import get_dictionary_service
from app.schemas.dictionary import (
    DictionaryLookupRequest,
    DictionaryResponse,
)
from app.services.dictionary_service import DictionaryService

router = APIRouter(
    prefix="/dictionary",
    tags=["Dictionary"],
)


@router.post(
    "/lookup",
    response_model=DictionaryResponse,
    status_code=status.HTTP_200_OK,
)
async def lookup_word(
    request: DictionaryLookupRequest,
    session: AsyncSession = Depends(get_async_db),
    service: DictionaryService = Depends(get_dictionary_service),
) -> DictionaryResponse:
    """
    Look up a word using the local cache first.
    Falls back to the configured AI provider if the word
    is not already stored.
    """
    try:
        return await service.lookup(
            session,
            word=request.word,
            language=request.language,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc