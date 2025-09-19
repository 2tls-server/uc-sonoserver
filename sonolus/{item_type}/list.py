donotload = False

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
    compile_static_posts_list,
    # compile_playlists_list,
    # compile_replays_list,
    # compile_rooms_list
    sort_posts_by_newest,
)
from helpers.paginate import list_to_pages
from helpers.sonolus_typings import ItemType
from helpers.api_helpers import api_level_to_level

router = APIRouter()

from locales.locale import Locale
from helpers.owoify import handle_item_uwu


def setup():
    @router.get("/")
    async def main(
        request: Request,
        item_type: ItemType,
        type: Literal["quick", "advanced"] = Query("quick"),
        page: int = Query(0, ge=0),
        min_rating: Optional[int] = Query(None),
        max_rating: Optional[int] = Query(None),
        tags: Optional[List[str]] = Query(None),
        min_likes: Optional[int] = Query(None),
        max_likes: Optional[int] = Query(None),
        liked_by: Optional[bool] = Query(False),
        title_includes: Optional[str] = Query(None),
        description_includes: Optional[str] = Query(None),
        artists_includes: Optional[str] = Query(None),
        sort_by: Optional[
            Literal["created_at", "rating", "likes", "decaying_likes", "abc"]
        ] = Query("created_at"),
        sort_order: Optional[Literal["desc", "asc"]] = Query("desc"),
        level_status: Optional[Literal["PUBLIC"]] = Query(
            "PUBLIC"
        ),  # will only ever be PUBLIC here. anything else, go to playlists
        keywords: Optional[str] = Query(None),
    ):
        query_params = dict(request.query_params)
        for item in request.app.remove_config_queries:
            query_params.pop(item, None)
        locale = Locale.get_messages(request.state.localization)
        uwu_level = request.state.uwu if request.state.localization == "en" else "off"
        searching = False
        generate_pages = True
        auth = request.headers.get("Sonolus-Session")

        if item_type == "engines":
            data = await request.app.run_blocking(
                compile_engines_list, request.app.base_url
            )
        elif item_type == "skins":
            data = await request.app.run_blocking(
                compile_skins_list, request.app.base_url
            )
        elif item_type == "backgrounds":
            data = await request.app.run_blocking(
                compile_backgrounds_list, request.app.base_url
            )
        elif item_type == "effects":
            data = await request.app.run_blocking(
                compile_effects_list, request.app.base_url
            )
        elif item_type == "particles":
            data = await request.app.run_blocking(
                compile_particles_list, request.app.base_url
            )
        elif item_type == "posts":
            data = await request.app.run_blocking(
                compile_static_posts_list, request.app.base_url
            )
            data = sort_posts_by_newest(data)
        # elif item_type == "playlists":
        #     data = await request.app.run_blocking(compile_playlists_list, request.app.base_url)
        elif item_type == "levels":
            if type == "quick":
                params = {
                    "type": type,
                    "page": page,
                    "meta_includes": keywords,
                }
            else:
                params = {
                    "type": type,
                    "page": page,
                    "min_rating": min_rating,
                    "max_rating": max_rating,
                    "status": level_status,
                    "tags": tags,
                    "min_likes": min_likes,
                    "max_likes": max_likes,
                    "liked_by": liked_by,
                    "title_includes": title_includes,
                    "description_includes": description_includes,
                    "artists_includes": artists_includes,
                    "sort_by": sort_by,
                    "sort_order": sort_order,
                    "meta_includes": keywords,
                }
            headers = {request.app.auth_header: request.app.auth}
            if auth:
                headers["authorization"] = auth
            async with aiohttp.ClientSession(headers=headers) as cs:
                async with cs.get(
                    request.app.api_config["url"] + "/api/charts/",
                    params={
                        k: (int(v) if isinstance(v, bool) else v)
                        for k, v in params.items()
                        if v is not None
                    },
                ) as req:
                    response = await req.json()
            response_data = response["data"]
            data = []
            asset_base_url = response["asset_base_url"].removesuffix("/")
            for item in response_data:
                item_data = api_level_to_level(request, asset_base_url, item)
                data.append(item_data)
            num_pages = response["pageCount"]
            generate_pages = False
        # elif item_type == "replays":
        #     data = await request.app.run_blocking(compile_replays_list, request.app.base_url)
        # elif item_type == "rooms":
        #     data = await request.app.run_blocking(compile_rooms_list, request.app.base_url)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=locale.item_type_not_found(item_type),
            )
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
        page_data = handle_item_uwu(page_data, uwu_level)
        return {
            "pageCount": len(pages) if generate_pages else num_pages,
            "items": page_data,
        }
