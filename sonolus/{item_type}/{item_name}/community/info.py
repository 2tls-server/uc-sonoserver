from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from helpers.sonolus_typings import ItemType
from helpers.data_helpers import create_server_form, ServerFormOptionsFactory

router = APIRouter()

from locales.locale import Locale
from helpers.owoify import handle_uwu

import aiohttp


@router.get("/")
async def main(request: Request, item_type: ItemType, item_name: str):
    try:
        locale = request.state.loc
    except AssertionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    uwu_level = request.state.uwu
    auth = request.headers.get("Sonolus-Session")
    actions = []
    if item_type == "levels":
        headers = {request.app.auth_header: request.app.auth}
        if auth:
            headers["authorization"] = auth
        async with aiohttp.ClientSession(headers=headers) as cs:
            async with cs.get(
                request.app.api_config["url"]
                + f"/api/charts/{item_name.removeprefix('UnCh-')}/comment/"
            ) as req:
                response = await req.json()
        comments = response["data"]
        formatted_comments = []
        commentDeleteAction = create_server_form(
            type="delete",
            title="#DELETE",
            require_confirmation=True,
            options=[],
            icon="delete",
        )
        for comment in comments[:3]:
            formatted_comments.append(
                {
                    "name": str(comment["id"]),
                    "author": handle_uwu(comment["username"], uwu_level),
                    "time": comment["created_at"],
                    "content": handle_uwu(comment["content"], uwu_level),
                    "actions": (
                        [commentDeleteAction]
                        if (comment["owner"] or response.get("mod"))
                        and not comment["deleted_at"]
                        else []
                    ),
                }
            )
        if auth:
            actions.append(
                create_server_form(
                    type="comment",
                    title="#COMMENT",
                    icon="comment",
                    require_confirmation=False,
                    options=[
                        ServerFormOptionsFactory.server_text_area_option(
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
                    ],
                )
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=locale.item_not_found(item_type, item_name),
        )
    return {"actions": actions, "topComments": formatted_comments}
