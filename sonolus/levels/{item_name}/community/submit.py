from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from helpers.sonolus_typings import ItemType
from helpers.models import ServerSubmitItemCommunityActionRequest, ParsedServerSubmitCommentActionRequest, CommentRequest, ServerSubmitItemCommunityCommentActionResponse

from pydantic import BaseModel

from urllib.parse import parse_qs

router = APIRouter()

from locales.locale import Locale

import aiohttp


@router.post("/", response_model=ServerSubmitItemCommunityCommentActionResponse)
async def main(
    request: Request,
    item_name: str,
    data: ServerSubmitItemCommunityActionRequest,
):
    try:
        locale = request.state.loc
    except AssertionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    auth = request.headers.get("Sonolus-Session")

    parsed_data = ParsedServerSubmitCommentActionRequest.model_validate({k: v[0] for k, v in parse_qs(data.values).items()})

    headers = {request.app.auth_header: request.app.auth}
    if auth:
        headers["authorization"] = auth
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=locale.not_logged_in,
        )

    type = parsed_data.type
    if type not in ["comment"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=locale.not_found
        )
    
    async with aiohttp.ClientSession(headers=headers) as cs:
        async with cs.post(
            request.app.api_config["url"]
            + f"/api/charts/{item_name.removeprefix('UnCh-')}/comment/",
            json=CommentRequest(content=parsed_data.content).model_dump(),
        ) as req:
            if req.status != 200:
                raise HTTPException(
                    status_code=req.status, detail=locale.unknown_error
                )

    return ServerSubmitItemCommunityCommentActionResponse(
        key="",
        hashes=[],
        shouldUpdateComments=True
    )
