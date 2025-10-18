from fastapi import APIRouter, Request
from fastapi import HTTPException, status
from helpers.sonolus_typings import ItemType

router = APIRouter()

from locales.locale import Loc

@router.get("/")
async def main(request: Request, item_type: ItemType):
    locale: Loc = request.state.loc

    if item_type != "levels":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=locale.item_type_not_found(item_type)
        )
    submit_form = {
        "type": "replay",
        "title": "#REPLAY",
        "requireConfirmation": False,
        "options": [],
    }
    data = {"submits": [submit_form]}
    return data
