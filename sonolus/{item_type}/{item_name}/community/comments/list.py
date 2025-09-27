import asyncio

from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from helpers.sonolus_typings import ItemType
from helpers.data_helpers import create_server_form

router = APIRouter()

from locales.locale import Loc
from helpers.owoify import handle_uwu

import aiohttp


@router.get("/")
async def main(request: Request, item_type: ItemType, item_name: str):
    locale: Loc = request.state.loc
    page = request.state.query_params.get("page", 0)
    uwu_level = request.state.uwu
    auth = request.headers.get("Sonolus-Session")
    if item_type == "levels":
        headers = {request.app.auth_header: request.app.auth}
        if auth:
            headers["authorization"] = auth
        async with aiohttp.ClientSession(headers=headers) as cs:
            async with cs.get(
                request.app.api_config["url"]
                + f"/api/charts/{item_name.removeprefix('UnCh-')}/comment/",
                params={"page": page},
            ) as req:
                response = await req.json()
        page_count = response["pageCount"]
        if page > page_count or page < 0:
            raise HTTPException(
                status_code=400,
                detail=(
                    locale.invalid_page_plural(page, page_count)
                    if page_count != 1
                    else locale.invalid_page_singular(page, page_count)
                ),
            )
        elif page_count == 0:
            raise HTTPException(status_code=400, detail=locale.not_found)
        comments = response["data"]
        commentDeleteAction = create_server_form(
            type="delete",
            title="#DELETE",
            require_confirmation=True,
            options=[],
            icon="delete",
        )

        async def process_comment(comment: dict) -> dict:
            return {
                "name": str(comment["id"]),
                "author": handle_uwu(
                    comment["username"], request.state.localization, uwu_level
                ),
                "time": comment["created_at"],
                "content": handle_uwu(
                    comment["content"], request.state.localization, uwu_level
                ),
                "actions": (
                    [commentDeleteAction]
                    if (comment["owner"] or response.get("mod"))
                    and not comment["deleted_at"]
                    else []
                ),
            }

        tasks = [process_comment(comment) for comment in comments]
        formatted_comments = await asyncio.gather(*tasks)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=locale.item_not_found(item_type, item_name),
        )
    return {"pageCount": page_count, "comments": formatted_comments}
