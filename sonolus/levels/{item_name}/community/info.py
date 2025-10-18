from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from typing import Optional

from helpers.sonolus_typings import ItemType
from helpers.models import APIServerListCommentsResponse, Comment, ServerForm, ServerItemCommunityComment, ServerTextAreaOption, ServerItemCommunityInfo

router = APIRouter()

from locales.locale import Locale
from helpers.owoify import handle_uwu

import aiohttp

def process_comment(comment: Comment, is_mod: Optional[bool], localization, uwu_level, comment_delete_action: ServerForm) -> ServerItemCommunityComment:
    return ServerItemCommunityComment(
        name=str(comment.id),
        author=handle_uwu(
            comment.username,
            localization,
            uwu_level,
            symbols=False
        ),
        time=comment.created_at,
        content=handle_uwu(
            comment.content, localization, uwu_level
        ),
        actions=(
            [comment_delete_action]
            if (comment.owner or is_mod)
            and not comment.deleted_at
            else []
        )
    )

@router.get("/", response_model=ServerItemCommunityInfo)
async def main(request: Request, item_name: str):
    try:
        locale = request.state.loc
    except AssertionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    uwu_level = request.state.uwu
    auth = request.headers.get("Sonolus-Session")
    actions = []

    headers = {request.app.auth_header: request.app.auth}
    if auth:
        headers["authorization"] = auth
    async with aiohttp.ClientSession(headers=headers) as cs:
        async with cs.get(
            request.app.api_config["url"]
            + f"/api/charts/{item_name.removeprefix('UnCh-')}/comment/"
        ) as req:
            response = APIServerListCommentsResponse.model_validate_json(await req.json())

    comments = response.data
    formatted_comments = []
    comment_delete_action = ServerForm(
        type="delete",
        title="#DELETE",
        icon="delete",
        requireConfirmation=True,
        options=[]
    )

    formatted_comments = [process_comment(comment, response.mod, request.state.localization, uwu_level, comment_delete_action) for comment in comments]

    return ServerItemCommunityInfo(
        actions=(
            [
                ServerForm(
                    type="comment",
                    title="#COMMENT",
                    icon="comment",
                    requireConfirmation=False,
                    options=[
                        ServerTextAreaOption(
                            query="content",
                            name="#COMMENT",
                            required=True,
                            default="",
                            placeholder="#COMMENT_PLACEHOLDER",
                            limit=200,
                            shortcuts=[
                                "Awesome!",
                                "This was fun.",
                                "Great chart!",
                                "UwU :3",
                            ],
                        )
                    ]
                )
            ] if auth else []
        ),
        topComments=formatted_comments
    )