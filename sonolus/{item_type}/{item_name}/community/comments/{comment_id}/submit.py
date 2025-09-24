from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from helpers.sonolus_typings import ItemType

from pydantic import BaseModel

from urllib.parse import parse_qs

router = APIRouter()

from locales.locale import Loc

import aiohttp


class ServerSubmitItemActionRequest(BaseModel):
    values: str


@router.post("/")
async def main(
    request: Request,
    item_type: ItemType,
    item_name: str,
    comment_id: int,
    data: ServerSubmitItemActionRequest,
):
    locale: Loc = request.state.loc
    uwu_level = request.state.uwu
    item_data = None
    auth = request.headers.get("Sonolus-Session")
    actions = []

    parsed = parse_qs(data.values)
    flattened_data = {k: v[0] for k, v in parsed.items()}

    if item_type == "levels":
        headers = {request.app.auth_header: request.app.auth}
        if auth:
            headers["authorization"] = auth
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=locale.not_logged_in,
            )
        # parse data.values, www-form
        type = flattened_data.get("type")
        if type not in ["delete"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=locale.not_found
            )
        if type in ["delete"]:
            async with aiohttp.ClientSession(headers=headers) as cs:
                async with cs.delete(
                    request.app.api_config["url"]
                    + f"/api/charts/{item_name.removeprefix('UnCh-')}/comment/{comment_id}/"
                ) as req:
                    if req.status != 200:
                        raise HTTPException(
                            status_code=req.status, detail=locale.unknown_error
                        )
                    data = await req.json()
                    if data.get("mod") and not data.get("owner"):
                        async with cs.post(
                            request.app.api_config["url"]
                            + f"/api/accounts/notifications/",
                            json={
                                "user_id": data["commenter"],
                                "title": "Comment Deleted",
                                "content": f"#COMMENT_DELETED\n{data['content']}",
                            },
                        ) as req:
                            if req.status != 200:
                                raise HTTPException(
                                    status_code=req.status, detail=locale.not_mod
                                )
            resp = {"key": "", "hashes": [], "shouldUpdateComments": True}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=locale.item_not_found(item_type, item_name),
        )

    return resp
