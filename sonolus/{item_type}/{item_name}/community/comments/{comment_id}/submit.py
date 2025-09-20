donotload = False

import base64
from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from helpers.sonolus_typings import ItemType
from helpers.datastructs import ServerItemDetails

from pydantic import BaseModel

from urllib.parse import parse_qs, urlencode

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
        comment_id: int,
        data: ServerSubmitItemActionRequest,
    ):
        query_params = request.state.query_params
        try:
            locale = Locale.get_messages(request.state.localization)
        except AssertionError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
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
                        + f"/api/charts/{item_name.removeprefix('UnCh-')}/comment/{comment_id}/",
                        json={"content": flattened_data.get("content")},
                    ) as req:
                        if req.status != 200:
                            raise HTTPException(
                                status_code=req.status, detail=locale.unknown_error
                            )
                resp = {"key": "", "hashes": [], "shouldUpdateComments": True}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=locale.item_not_found(item_type, item_name),
            )

        return resp
