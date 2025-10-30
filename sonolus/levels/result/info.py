from fastapi import APIRouter, Request
from fastapi import HTTPException, status
from helpers.sonolus_typings import ItemType

router = APIRouter()

from locales.locale import Loc

@router.get("/")
async def main(): # TODO
    submit_form = {
        "type": "replay",
        "title": "#REPLAY",
        "requireConfirmation": False,
        "options": [],
    }
    data = {"submits": [submit_form]}
    return data
