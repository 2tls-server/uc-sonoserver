donotload = False

from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from helpers.sonolus_typings import ItemType
from helpers.datastructs import ServerItemDetails

from pydantic import BaseModel

from urllib.parse import parse_qs

router = APIRouter()

from locales.locale import Locale

import aiohttp


class ServerSubmitItemActionRequest(BaseModel):
    values: str


def setup():
    @router.post("/")
    async def main(
        request: Request,
        item_type: ItemType,
        item_name: str,
        data: ServerSubmitItemActionRequest,
    ):
        query_params = dict(request.query_params)
        for item in request.app.remove_config_queries:
            query_params.pop(item, None)
        locale = Locale.get_messages(request.state.localization)
        uwu_level = request.state.uwu if request.state.localization == "en" else "off"
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
            if type not in ["like", "unlike"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=locale.not_found
                )
            async with aiohttp.ClientSession(headers=headers) as cs:
                async with cs.post(
                    request.app.api_config["url"] + f"/api/charts/{item_name}/like/",
                    data={"type": type},
                ) as req:
                    if req.status != 200:
                        raise HTTPException(
                            status_code=req.status, detail=locale.unknown_error
                        )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=locale.item_not_found(item_type),
            )

        resp = {"key": "", "hashes": [], "shouldUpdateItem": True}
        return resp
