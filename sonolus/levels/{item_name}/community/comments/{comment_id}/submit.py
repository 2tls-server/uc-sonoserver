from fastapi import APIRouter, Request
from fastapi import HTTPException, status
from typing import TypedDict, Optional

from helpers.sonolus_typings import ItemType
from helpers.models import ServerSubmitItemActionRequest, ServerSubmitItemCommunityCommentActionResponse, APIServerDeleteCommentResponse, NotificationRequest, ParsedServerSubmitCommentIDActionRequest
from urllib.parse import parse_qs

router = APIRouter()

from locales.locale import Loc

import aiohttp

@router.post("/", response_model=ServerSubmitItemCommunityCommentActionResponse)
async def main(
    request: Request,
    item_name: str,
    comment_id: int,
    data: ServerSubmitItemActionRequest,
):
    locale: Loc = request.state.loc
    auth = request.headers.get("Sonolus-Session")

    parsed_data = ParsedServerSubmitCommentIDActionRequest.model_validate({k: v[0] for k, v in parse_qs(data.values).items()})

    headers = {request.app.auth_header: request.app.auth}
    if auth:
        headers["authorization"] = auth
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=locale.not_logged_in,
        )
    
    # parse data.values, www-form
    type = parsed_data.type
    if type not in ["delete"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=locale.not_found
        )
    
    async with aiohttp.ClientSession(headers=headers) as cs:
        async with cs.delete(
            request.app.api_config["url"]
            + f"/api/charts/{item_name.removeprefix('UnCh-')}/comment/{comment_id}/"
        ) as req:
            if req.status != 200:
                raise HTTPException(
                    status_code=req.status, detail=locale.unknown_error
                )
            del_data = APIServerDeleteCommentResponse.model_validate_json(await req.json())
            if del_data.mod and not del_data.owner:
                async with cs.post(
                    request.app.api_config["url"]
                    + f"/api/accounts/notifications/",
                    json=NotificationRequest(
                        user_id=del_data.commenter,
                        title="Comment Deleted",
                        content=f"#COMMENT_DELETED\n{data['content']}"
                    ).model_dump(),
                ) as req:
                    if req.status != 200:
                        raise HTTPException(
                            status_code=req.status, detail=locale.not_mod
                        )

    return ServerSubmitItemCommunityCommentActionResponse(
        key="",
        hashes=[],
        shouldUpdateComments=True
    )
