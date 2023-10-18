from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.logging import get_logger
from app.models.tags import TagOut, TagsOut
from app.db.repositories.tags import TagsRepository
from app.api.dependencies.database import get_repository


router = APIRouter()

tags_logger = get_logger(__name__)


@router.get(
    "/",
    response_model=TagsOut,
    name="get-all-tags"
)
async def get_all_tags(
    tag_repo: Annotated[
        TagsRepository, Depends(get_repository(TagsRepository))
    ]
) -> TagsOut:
    try:
        db_tags = await tag_repo.get_all_tags()
        return TagsOut(tags=[TagOut(**tag.model_dump()) for tag in db_tags])
    except Exception as exc:
        tags_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, 
            "Failed to fetch tags."
        )
