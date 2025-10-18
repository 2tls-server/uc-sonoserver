import asyncio

from fastapi import APIRouter, Request, Query
from fastapi import HTTPException, status

from typing import Literal, Optional, List

import aiohttp

from helpers.data_compilers import (
    compile_engines_list,
    compile_backgrounds_list,
    compile_effects_list,
    compile_particles_list,
    compile_skins_list,
    # compile_replays_list,
    # compile_rooms_list
)
from helpers.paginate import list_to_pages
from helpers.sonolus_typings import ItemType
from helpers.api_helpers import api_level_to_level, api_notif_to_post

router = APIRouter()

from locales.locale import Loc
from helpers.owoify import handle_item_uwu

type_func = type


@router.get("/")
async def main(
    request: Request,
    item_type: ItemType,
    type: Literal["quick", "advanced"] = Query("quick"),
    page: int = Query(0, ge=0),
    staff_pick: Optional[Literal["default", "off", "true", "false"]] = Query("default"),
    min_rating: Optional[int] = Query(None),
    max_rating: Optional[int] = Query(None),
    tags: Optional[List[str]] = Query(None),
    min_likes: Optional[int] = Query(None),
    max_likes: Optional[int] = Query(None),
    min_comments: Optional[int] = Query(None),
    max_comments: Optional[int] = Query(None),
    liked_by: Optional[bool] = Query(False),
    commented_on: Optional[bool] = Query(False),
    title_includes: Optional[str] = Query(None),
    description_includes: Optional[str] = Query(None),
    author_includes: Optional[str] = Query(None),
    artists_includes: Optional[str] = Query(None),
    sort_by: Optional[
        Literal[
            "created_at",
            "published_at",
            "rating",
            "likes",
            "comments",
            "decaying_likes",
            "abc",
            "random",
        ]
    ] = Query("published_at"),
    sort_order: Optional[Literal["desc", "asc"]] = Query("desc"),
    level_status: Optional[Literal["PUBLIC"]] = Query(
        "PUBLIC"
    ),  # will only ever be PUBLIC here. anything else, go to playlists
    keywords: Optional[str] = Query(None),
):
    locale: Loc = request.state.loc
    uwu_level = request.state.uwu
    searching = False
    generate_pages = True
    auth = request.headers.get("Sonolus-Session")

    if item_type == "posts":
        notifs = []
        if auth:
            headers = {request.app.auth_header: request.app.auth}
            headers["authorization"] = auth
            async with aiohttp.ClientSession(headers=headers) as cs:
                async with cs.get(
                    request.app.api_config["url"] + f"/api/accounts/notifications/",
                    params={"only_unread": 0},
                ) as req:
                    response = await req.json()
            raw_notifs = response.get("notifications", [])
            notifs = [api_notif_to_post(request, i) for i in raw_notifs]
        if not notifs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=locale.notification.none_past,
            )
        data = notifs

    if generate_pages:
        pages = list_to_pages(data, request.app.get_items_per_page(item_type))
        if len(pages) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    locale.items_not_found(item_type)
                    if not searching
                    else locale.items_not_found_search(item_type)
                ),
            )
        try:
            page_data = pages[page]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="hi stop hitting our api thanks",
            )
    else:
        if len(data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    locale.items_not_found(item_type)
                    if not searching
                    else locale.items_not_found_search(item_type)
                ),
            )
        page_data = data
    page_data = handle_item_uwu(page_data, request.state.localization, uwu_level)
    return {
        "pageCount": len(pages),
        "items": page_data,
    }
