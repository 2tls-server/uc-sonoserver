from fastapi import HTTPException
from helpers.models.api.notifications import NotificationRequest
from helpers.models.api.levels import VisibilityChangeResponse
from helpers.models.sonolus.response import ServerSubmitItemActionResponse
from locales.locale import Loc
from typing import Literal
import aiohttp

async def visibility(headers: dict, request, item_name: str, visibility: Literal["UNLISTED", "PRIVATE", "PUBLIC"], locale: Loc) -> ServerSubmitItemActionResponse:
    async with aiohttp.ClientSession(headers=headers) as cs:
        async with cs.patch(
            request.app.api_config["url"]
            + f"/api/charts/{item_name.removeprefix('UnCh-')}/visibility/",
            json={"status": visibility},
        ) as req:
            if req.status != 200:
                raise HTTPException(
                    status_code=req.status, detail=locale.not_mod_or_owner
                )
            data = VisibilityChangeResponse.model_validate(await req.json())
        if (
            visibility != "PUBLIC"
            and data.mod
            and not data.owner
        ):
            async with cs.post(
                request.app.api_config["url"] + f"/api/accounts/notifications/",
                json=NotificationRequest(
                    user_id=data.author,
                    title="Chart Visibility Update",
                    content=f"#CHART_VISIBILITY_CHANGED\n{visibility}\n{data.title}"
                )
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