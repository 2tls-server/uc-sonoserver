from helpers.models.sonolus.response import ServerSubmitItemActionResponse
from fastapi import HTTPException
from locales.locale import Loc
from typing import Literal
import aiohttp

async def staff_pick(headers: dict, request, item_name: str, type: Literal["staff_pick_add", "staff_pick_delete"], locale: Loc) -> ServerSubmitItemActionResponse:
    async with aiohttp.ClientSession(headers=headers) as cs:
        async with cs.patch(
            request.app.api_config["url"]
            + f"/api/charts/{item_name.removeprefix('UnCh-')}/stpick/",
            json={"value": True if type == "staff_pick_add" else False},
        ) as req:
            if req.status != 200:
                raise HTTPException(
                    status_code=req.status, detail=locale.not_mod
                )
            
    return ServerSubmitItemActionResponse(
        key="",
        hashes=[],
        shouldUpdateItem=True
    )