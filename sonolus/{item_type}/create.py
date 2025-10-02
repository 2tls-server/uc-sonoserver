import asyncio

from typing import List

from fastapi import APIRouter, Request
from fastapi import HTTPException, status
from helpers.sonolus_typings import ItemType

router = APIRouter()

from locales.locale import Loc


@router.post("/")
async def main(request: Request, item_type: ItemType):
    locale: Loc = request.state.loc
    if item_type == "levels":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=locale.use_website_to_upload("https://untitledcharts.com"),
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=locale.item_type_not_found(item_type),
    )
