donotload = False

import base64, asyncio

from urllib.parse import parse_qs
from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from helpers.data_compilers import (
    compile_engines_list,
    compile_backgrounds_list,
    compile_effects_list,
    compile_particles_list,
    compile_skins_list,
    compile_static_posts_list,
    compile_playlists_list,
    # compile_replays_list,
    # compile_rooms_list
)
from helpers.sonolus_typings import ItemType
from helpers.datastructs import ServerItemDetails, get_item_type
from helpers.data_helpers import create_server_form, ServerFormOptionsFactory
from helpers.api_helpers import api_level_to_level

router = APIRouter()

from locales.locale import Locale
from helpers.owoify import handle_item_uwu

import aiohttp


def setup():
    @router.get("/")
    async def main(request: Request, item_type: ItemType, item_name: str):
        try:
            locale = Locale.get_messages(request.state.localization)
        except AssertionError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported locale"
            )
        uwu_level = request.state.uwu
        uwu_handled = False
        item_data = None
        auth = request.headers.get("Sonolus-Session")
        actions = []

        if item_type == "engines":
            data = await request.app.run_blocking(
                compile_engines_list, request.app.base_url, request.state.localization
            )
        elif item_type == "skins":
            data = await request.app.run_blocking(
                compile_skins_list, request.app.base_url
            )
        elif item_type == "backgrounds":
            item_data = (
                await request.app.run_blocking(
                    compile_backgrounds_list,
                    request.app.base_url,
                    request.state.localization,
                )
            )[0]
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
            # maybe also grab non-static posts lol
        elif item_type == "playlists":
            session = request.headers.get("Sonolus-Session")
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=locale.not_logged_in
                )
            if item_name == "uploaded":
                item_name = "uploaded_cGFnZT0x"  # page=1
            parts = item_name.split("_", 1)
            if parts[0] != "uploaded" or len(parts) != 2 or len(item_name) > 500:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="huh"
                )
            parsed = parse_qs(base64.b64decode(parts[1].encode()).decode())
            flattened_data = {k: v[0] for k, v in parsed.items()}
            headers = {request.app.auth_header: request.app.auth}
            headers["authorization"] = auth
            params = {
                "type": "advanced",
            }
            page = flattened_data.get("page")
            if page is not None:
                if page.isdigit():
                    page = int(page)
                if not isinstance(page, int) or page < 1:
                    raise HTTPException(
                        status_code=400, detail="page must be a non-negative integer."
                    )
                params["page"] = page - 1
            else:
                page = 1
            min_rating = flattened_data.get("min_rating")
            max_rating = flattened_data.get("max_rating")
            if min_rating is not None:
                if min_rating.isdigit():
                    min_rating = int(min_rating)
                if not isinstance(min_rating, int):
                    raise HTTPException(
                        status_code=400, detail="min_rating must be an integer."
                    )
                params["min_rating"] = min_rating
            if max_rating is not None:
                if max_rating.isdigit():
                    max_rating = int(max_rating)
                if not isinstance(max_rating, int):
                    raise HTTPException(
                        status_code=400, detail="max_rating must be an integer."
                    )
                params["max_rating"] = max_rating
            if (
                min_rating is not None
                and max_rating is not None
                and min_rating > max_rating
            ):
                raise HTTPException(
                    status_code=400,
                    detail="min_rating cannot be greater than max_rating.",
                )
            tags = flattened_data.get("tags")
            if tags is not None:
                if not isinstance(tags, list):
                    raise HTTPException(
                        status_code=400, detail="tags must be a list of strings."
                    )
                for tag in tags:
                    if not isinstance(tag, str):
                        raise HTTPException(
                            status_code=400, detail="Each tag must be a string."
                        )
                params["tags"] = tags
            min_likes = flattened_data.get("min_likes")
            max_likes = flattened_data.get("max_likes")
            if min_likes is not None:
                if min_likes.isdigit():
                    min_likes = int(min_likes)
                if not isinstance(min_likes, int):
                    raise HTTPException(
                        status_code=400, detail="min_likes must be an integer."
                    )
                params["min_likes"] = min_likes
            if max_likes is not None:
                if max_likes.isdigit():
                    max_likes = int(max_likes)
                if not isinstance(max_likes, int):
                    raise HTTPException(
                        status_code=400, detail="max_likes must be an integer."
                    )
                params["max_likes"] = max_likes
            if (
                min_likes is not None
                and max_likes is not None
                and min_likes > max_likes
            ):
                raise HTTPException(
                    status_code=400,
                    detail="min_likes cannot be greater than max_likes.",
                )
            liked_by = flattened_data.get("liked_by", False)
            if type(liked_by) == str and liked_by.isdigit():
                liked_by = bool(liked_by)
            if not isinstance(liked_by, bool):
                raise HTTPException(
                    status_code=400, detail="liked_by must be a boolean."
                )
            params["liked_by"] = liked_by
            title_includes = flattened_data.get("title_includes")
            if title_includes is not None:
                if not isinstance(title_includes, str):
                    raise HTTPException(
                        status_code=400, detail="title_includes must be a string."
                    )
                params["title_includes"] = title_includes
            description_includes = flattened_data.get("description_includes")
            if description_includes is not None:
                if not isinstance(description_includes, str):
                    raise HTTPException(
                        status_code=400, detail="description_includes must be a string."
                    )
                params["description_includes"] = description_includes
            artists_includes = flattened_data.get("artists_includes")
            if artists_includes is not None:
                if not isinstance(artists_includes, str):
                    raise HTTPException(
                        status_code=400, detail="artists_includes must be a string."
                    )
                params["artists_includes"] = artists_includes
            sort_by = flattened_data.get("sort_by", "created_at")
            allowed_sort_by = ["created_at", "rating", "likes", "decaying_likes", "abc"]
            if sort_by not in allowed_sort_by:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid value for sort_by. Allowed values are: {', '.join(allowed_sort_by)}.",
                )
            params["sort_by"] = sort_by
            sort_order = flattened_data.get("sort_order", "desc")
            allowed_sort_order = ["desc", "asc"]
            if sort_order not in allowed_sort_order:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid value for sort_order. Allowed values are: {', '.join(allowed_sort_order)}.",
                )
            params["sort_order"] = sort_order
            level_status = flattened_data.get("status", "ALL")
            if level_status not in ["ALL", "PUBLIC_MINE", "UNLISTED", "PRIVATE"]:
                raise HTTPException(status_code=400, detail="Invalid level_status.")
            params["status"] = level_status
            keywords = flattened_data.get("keywords")
            if keywords is not None:
                if not isinstance(keywords, str):
                    raise HTTPException(
                        status_code=400, detail="keywords must be a string."
                    )
                params["meta_includes"] = keywords
            params = {k: v for k, v in params.items() if v is not None}

            async with aiohttp.ClientSession(headers=headers) as cs:
                async with cs.get(
                    request.app.api_config["url"] + f"/api/charts/",
                    params={
                        k: (int(v) if isinstance(v, bool) else v)
                        for k, v in params.items()
                        if v is not None
                    },
                ) as req:
                    response = await req.json()
            asset_base_url = response["asset_base_url"].removesuffix("/")
            levels = await asyncio.gather(
                *[
                    request.app.run_blocking(
                        api_level_to_level,
                        request,
                        asset_base_url,
                        level,
                        request.state.levelbg,
                    )
                    for level in response["data"]
                ]
            )
            pageCount = response["pageCount"]
            if page > pageCount or page < 0:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        locale.invalid_page_plural(page, pageCount)
                        if pageCount != 1
                        else locale.invalid_page_singular(page, pageCount)
                    ),
                )
            elif pageCount == 0:
                raise HTTPException(
                    status_code=400, detail=locale.items_not_found_search("uploaded")
                )
            item_data = (
                await request.app.run_blocking(
                    compile_playlists_list,
                    request.app.base_url,
                    request.state.localization,
                )
            )[0].copy()
            item_data["name"] = (
                f"uploaded_{base64.urlsafe_b64encode(parts[1].encode()).decode()}"
            )
            item_data["levels"] = levels
            options = []
            options.append(
                ServerFormOptionsFactory.server_select_option(
                    query="status",
                    name=locale.search.VISIBILITY,
                    required=False,
                    default=level_status or "ALL",
                    values=[
                        {"name": "ALL", "title": locale.search.VISIBILITY_ALL},
                        {
                            "name": "PUBLIC_MINE",
                            "title": locale.search.VISIBILITY_PUBLIC,
                        },
                        {
                            "name": "UNLISTED",
                            "title": locale.search.VISIBILITY_UNLISTED,
                        },
                        {"name": "PRIVATE", "title": locale.search.VISIBILITY_PRIVATE},
                    ],
                )
            )
            options.append(
                ServerFormOptionsFactory.server_text_option(
                    query="keywords",
                    name="#KEYWORDS",
                    required=False,
                    default=keywords or "",
                    placeholder=locale.search.ENTER_TEXT,
                    limit=100,
                    shortcuts=[],
                )
            )
            options.append(
                ServerFormOptionsFactory.server_slider_option(
                    query="min_rating",
                    name=locale.search.MIN_RATING,
                    required=False,
                    default=min_rating or 0,
                    min_value=0,
                    max_value=99,
                    step=1,
                )
            )
            options.append(
                ServerFormOptionsFactory.server_slider_option(
                    query="max_rating",
                    name=locale.search.MAX_RATING,
                    required=False,
                    default=max_rating or 99,
                    min_value=0,
                    max_value=99,
                    step=1,
                )
            )
            options.append(
                ServerFormOptionsFactory.server_text_option(
                    query="title_includes",
                    name=locale.search.TITLE_CONTAINS,
                    required=False,
                    default=title_includes or "",
                    placeholder=locale.search.ENTER_TEXT,
                    limit=100,
                    shortcuts=[],
                )
            )
            options.append(
                ServerFormOptionsFactory.server_text_option(
                    query="description_includes",
                    name=locale.search.DESCRIPTION_CONTAINS,
                    required=False,
                    default=description_includes or "",
                    placeholder=locale.search.ENTER_TEXT,
                    limit=200,
                    shortcuts=[],
                )
            )
            options.append(
                ServerFormOptionsFactory.server_text_option(
                    query="artists_includes",
                    name=locale.search.ARTISTS_CONTAINS,
                    required=False,
                    default=artists_includes or "",
                    placeholder=locale.search.ENTER_TEXT,
                    limit=100,
                    shortcuts=[],
                )
            )
            if auth:
                options.append(
                    ServerFormOptionsFactory.server_toggle_option(
                        query="liked_by",
                        name=locale.search.ONLY_LEVELS_I_LIKED,
                        required=False,
                        default=liked_by,
                    )
                )
            options.append(
                ServerFormOptionsFactory.server_slider_option(
                    query="min_likes",
                    name=locale.search.MIN_LIKES,
                    required=False,
                    default=min_likes or 0,
                    min_value=0,
                    max_value=9999,
                    step=1,
                )
            )
            options.append(
                ServerFormOptionsFactory.server_slider_option(
                    query="max_likes",
                    name=locale.search.MAX_LIKES,
                    required=False,
                    default=max_likes or 9999,
                    min_value=0,
                    max_value=9999,
                    step=1,
                )
            )
            options.append(
                ServerFormOptionsFactory.server_text_option(
                    query="tags",
                    name=locale.search.TAGS_COMMA_SEPARATED,
                    required=False,
                    default=tags or "",
                    placeholder=locale.search.ENTER_TAGS,
                    limit=200,
                    shortcuts=[],
                )
            )
            options.append(
                ServerFormOptionsFactory.server_select_option(
                    query="sort_by",
                    name=locale.search.SORT_BY,
                    required=False,
                    default=sort_by or "created_at",
                    values=[
                        {"name": "created_at", "title": locale.search.DATE_CREATED},
                        {"name": "rating", "title": locale.search.RATING},
                        {"name": "likes", "title": locale.search.LIKES},
                        {
                            "name": "decaying_likes",
                            "title": locale.search.DECAYING_LIKES,
                        },
                        {"name": "abc", "title": locale.search.TITLE_A_Z},
                    ],
                    description=locale.search.SORT_BY_DESCRIPTION,
                )
            )
            options.append(
                ServerFormOptionsFactory.server_select_option(
                    query="sort_order",
                    name=locale.search.SORT_ORDER,
                    required=False,
                    default=sort_order or "desc",
                    values=[
                        {"name": "desc", "title": locale.search.DESCENDING},
                        {"name": "asc", "title": locale.search.ASCENDING},
                    ],
                )
            )
            actions.append(
                create_server_form(
                    type="filter",
                    title=locale.search.FILTERS(page, pageCount),
                    require_confirmation=False,
                    options=[
                        ServerFormOptionsFactory.server_slider_option(
                            query="page",
                            name="Page",
                            default=page,
                            min_value=1,
                            max_value=pageCount,
                            step=1,
                            required=False,
                        )
                    ]
                    + options,
                )
            )
        elif item_type == "levels":
            headers = {request.app.auth_header: request.app.auth}
            if auth:
                headers["authorization"] = auth
            async with aiohttp.ClientSession(headers=headers) as cs:
                async with cs.get(
                    request.app.api_config["url"]
                    + f"/api/charts/{item_name.removeprefix('UnCh-')}/"
                ) as req:
                    response = await req.json()
            asset_base_url = response["asset_base_url"].removesuffix("/")
            liked = response["data"].get("liked")
            like_count = response["data"]["like_count"]
            item_data, desc = await request.app.run_blocking(
                api_level_to_level,
                request,
                asset_base_url,
                response["data"],
                request.state.levelbg,
                include_description=True,
            )
            if auth:
                if liked:
                    actions.append(
                        create_server_form(
                            type="unlike",
                            title=f"Unlike ({like_count:,})",
                            icon="heart",
                            require_confirmation=False,
                            options=[],
                        )
                    )
                else:
                    actions.append(
                        create_server_form(
                            type="like",
                            title=f"Like ({like_count:,})",
                            icon="heartHollow",
                            require_confirmation=False,
                            options=[],
                        )
                    )
            if response.get("mod") or response.get("owner"):
                actions.append(
                    create_server_form(
                        type="delete",
                        title="#DELETE",
                        icon="delete",
                        require_confirmation=True,
                        options=[],
                    )
                )
                VISIBILITIES = {
                    "PUBLIC": {"title": "#PUBLIC", "icon": "globe"},
                    "PRIVATE": {"title": "#PRIVATE", "icon": "lock"},
                    "UNLISTED": {
                        "title": locale.search.VISIBILITY_UNLISTED,
                        "icon": "envelopeOpen",
                    },
                }
                current = response["data"]["status"]
                vis_values = []
                for status, meta in VISIBILITIES.items():
                    vis_values.append({"name": status, "title": meta["title"]})
                the_option = ServerFormOptionsFactory.server_select_option(
                    query="visibility",
                    name=locale.search.VISIBILITY,
                    required=True,
                    default=current,
                    values=vis_values,
                )
                the_action = create_server_form(
                    type="visibility",
                    title=locale.search.VISIBILITY,
                    icon=VISIBILITIES[current]["icon"],
                    require_confirmation=True,
                    options=[the_option],
                )
                actions.append(the_action)
            if response.get("mod"):
                if desc:
                    desc = locale.is_mod + f"\n{'-'*10}\n" + desc
                else:
                    desc = locale.is_mod + f"\n{'-'*10}\n" + "No description"
            if desc:
                item_data["description"] = desc
            uwu_handled = True
        # elif item_type == "replays":
        #     data = await request.app.run_blocking(compile_replays_list, request.app.base_url)
        # elif item_type == "rooms":
        #     data = await request.app.run_blocking(compile_rooms_list, request.app.base_url)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=locale.item_not_found(item_type, item_name),
            )
        if not item_data:
            item_data = next((i for i in data if i["name"] == item_name), None)
            if not item_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=locale.item_not_found(
                        item_type.capitalize().removesuffix("s"), item_name
                    ),
                )

        T = get_item_type(item_type)
        if uwu_handled:
            data = item_data
        else:
            data = handle_item_uwu([item_data], uwu_level)[0]
        detail: ServerItemDetails[T] = {
            "item": data,
            "actions": actions,
            "hasCommunity": False,
            "leaderboards": [],
            "sections": [],
        }
        if data.get("description"):
            detail["description"] = data["description"]
        return detail
