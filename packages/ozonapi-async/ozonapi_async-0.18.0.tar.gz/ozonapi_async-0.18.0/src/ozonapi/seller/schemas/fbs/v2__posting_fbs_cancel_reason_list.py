"""https://docs.ozon.ru/api/seller/?#operation/PostingAPI_GetPostingFbsCancelReasonList"""
from pydantic import BaseModel, Field

from ..entities.postings.cancel_reason import PostingCancelReasonListItem


class PostingFBSCancelReasonListResponse(BaseModel):
    """Возвращает список возможных причин отправлений.

    Attributes:
        result: список возможных причин отправлений
    """
    model_config = {'frozen': True}

    result: list[PostingCancelReasonListItem] = Field(
        ..., description="Cписок возможных причин отправлений."
    )