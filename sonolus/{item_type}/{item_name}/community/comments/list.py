donotload = False

from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from helpers.sonolus_typings import ItemType
from helpers.data_helpers import create_server_form

router = APIRouter()

from locales.locale import Locale
from helpers.owoify import handle_uwu

import aiohttp


def setup():
    @router.get("/")
    async def main(request: Request, item_type: ItemType, item_name: str):
        try:
            locale = Locale.get_messages(request.state.localization)
        except AssertionError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
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
            formatted_comments = []
            commentDeleteAction = create_server_form(
                type="delete",
                title="#DELETE",
                require_confirmation=True,
                options=[],
                icon="delete",
            )
            for comment in comments:
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
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=locale.item_not_found(item_type, item_name),
            )
        return {"pageCount": page_count, "comments": formatted_comments}
