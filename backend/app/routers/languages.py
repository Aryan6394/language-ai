from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.language import get_languages
from app.db.session import get_db
from app.schemas.language import LanguageResponse

router = APIRouter(
    prefix="/languages",
    tags=["Languages"],
)


@router.get(
    "",
    response_model=list[LanguageResponse],
    summary="List supported languages",
)
def list_languages(
    db: Session = Depends(get_db),
):
    """
    Return every active language supported by the platform.
    """

    return get_languages(db)