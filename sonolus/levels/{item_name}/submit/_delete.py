from helpers.models.sonolus.response import ServerSubmitItemActionResponse
from helpers.models.api.notifications import NotificationRequest
from helpers.models.api.levels import DeleteChartResponse
from fastapi import HTTPException
from locales.locale import Loc
import aiohttp

async def delete(headers: dict, request, item_name: str, locale: Loc) -> ServerSubmitItemActionResponse:
    async with aiohttp.ClientSession(headers=headers) as cs:
        async with cs.delete(
            request.app.api_config["url"]
            + f"/api/charts/{item_name.removeprefix('UnCh-')}/delete/"
        ) as req:
            if req.status != 200:
                raise HTTPException(
                    status_code=req.status, detail=locale.not_admin_or_owner
                )
            data = DeleteChartResponse.model_validate(await req.json())
        if data.admin and not data.owner:
            async with cs.post(
                request.app.api_config["url"] + f"/api/accounts/notifications/",
                json=NotificationRequest(
                    user_id=data.author,
                    title="Chart Deleted",
                    content=f"#CHART_DELETED\n{data.title}",
                ).model_dump(),
            ) as req:
                if req.status != 200:
                    raise HTTPException(
                        status_code=req.status, detail=locale.not_mod
                    )
                
    return ServerSubmitItemActionResponse(
        key="",
        hashes=[],
        shouldRemoveItem=True
    )