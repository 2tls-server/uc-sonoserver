donotload = False

import asyncio

from typing import List

from fastapi import APIRouter, Request
from fastapi import HTTPException, status
from helpers.sonolus_typings import ItemType
from helpers.datastructs import (
    EngineItemSection,
    SkinItemSection,
    BackgroundItemSection,
    EffectItemSection,
    ParticleItemSection,
    PostItemSection,
    PlaylistItemSection,
    LevelItemSection,
    ReplayItemSection,
    RoomItemSection,
    ServerItemInfo,
    ServerForm,
)
from helpers.api_helpers import api_level_to_level
from helpers.data_helpers import (
    create_section,
    create_server_form,
    ServerFormOptionsFactory,
)
from helpers.data_compilers import (
    compile_banner,
    compile_backgrounds_list,
    compile_effects_list,
    compile_engines_list,
    compile_particles_list,
    compile_skins_list,
    compile_static_posts_list,
    sort_posts_by_newest,
    compile_playlists_list,
)

router = APIRouter()

from locales.locale import Locale
from helpers.owoify import handle_uwu, handle_item_uwu

import aiohttp


def setup():
    @router.get("/")
    async def main(request: Request, item_type: ItemType):
        query_params = request.state.query_params
        try:
            locale = Locale.get_messages(request.state.localization)
        except AssertionError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        uwu_level = request.state.uwu
        banner_srl = await request.app.run_blocking(compile_banner)
        searches = []
        auth = request.headers.get("Sonolus-Session")

        if item_type == "engines":
            data = await request.app.run_blocking(
                compile_engines_list, request.app.base_url, request.state.localization
            )
            sections: List[EngineItemSection] = [
                create_section(
                    "#ENGINE",
                    item_type,
                    handle_item_uwu(data[:5], uwu_level),
                    description=handle_uwu(
                        locale.server_description or request.app.config["description"],
                        uwu_level,
                    ),
                    icon="engine",
                )
            ]
        elif item_type == "skins":
            data = await request.app.run_blocking(
                compile_skins_list, request.app.base_url
            )
            sections: List[SkinItemSection] = [
                create_section(
                    "#SKIN",
                    item_type,
                    handle_item_uwu(data[:5], uwu_level),
                    description=handle_uwu(
                        locale.server_description or request.app.config["description"],
                        uwu_level,
                    ),
                    icon="skin",
                )
            ]
        elif item_type == "backgrounds":
            data = await request.app.run_blocking(
                compile_backgrounds_list,
                request.app.base_url,
                request.state.localization,
            )
            sections: List[BackgroundItemSection] = [
                create_section(
                    "#BACKGROUND",
                    item_type,
                    handle_item_uwu(data[:5], uwu_level),
                    description=handle_uwu(
                        locale.server_description or request.app.config["description"],
                        uwu_level,
                    ),
                    icon="background",
                )
            ]
        elif item_type == "effects":
            data = await request.app.run_blocking(
                compile_effects_list, request.app.base_url
            )
            sections: List[EffectItemSection] = [
                create_section(
                    "#EFFECT",
                    item_type,
                    handle_item_uwu(data[:5], uwu_level),
                    description=handle_uwu(
                        locale.server_description or request.app.config["description"],
                        uwu_level,
                    ),
                    icon="effect",
                )
            ]
        elif item_type == "particles":
            data = await request.app.run_blocking(
                compile_particles_list, request.app.base_url
            )
            sections: List[ParticleItemSection] = [
                create_section(
                    "#PARTICLE",
                    item_type,
                    handle_item_uwu(data[:5], uwu_level),
                    description=handle_uwu(
                        locale.server_description or request.app.config["description"],
                        uwu_level,
                    ),
                    icon="particle",
                )
            ]
        elif item_type == "posts":
            data = await request.app.run_blocking(
                compile_static_posts_list, request.app.base_url
            )
            # grab non-static posts too
            # sort em
            data = sort_posts_by_newest(data)
            sections: List[PostItemSection] = [
                create_section(
                    "#NEWEST",
                    item_type,
                    handle_item_uwu(data[:5], uwu_level),
                    icon="post",
                )
            ]
        elif item_type == "playlists":
            data = await request.app.run_blocking(
                compile_playlists_list, request.app.base_url, request.state.localization
            )
            sections: List[PlaylistItemSection] = [
                create_section(
                    "#PLAYLIST",
                    item_type,
                    data[:1],
                    description=handle_uwu(
                        locale.server_description or request.app.config["description"],
                        uwu_level,
                    ),
                    icon="playlist",
                )
            ]
        elif item_type == "levels":
            headers = {request.app.auth_header: request.app.auth}
            if auth:
                headers["authorization"] = auth
            async with aiohttp.ClientSession(headers=headers) as cs:
                async with cs.get(
                    request.app.api_config["url"] + "/api/charts/",
                    params={"type": "random"},
                ) as req:
                    random_response = await req.json()
                async with cs.get(
                    request.app.api_config["url"] + "/api/charts/",
                    params={"type": "advanced", "sort_by": "created_at"},
                ) as req:
                    newest_response = await req.json()
            asset_base_url = random_response["asset_base_url"].removesuffix("/")
            random = await asyncio.gather(
                *[
                    request.app.run_blocking(
                        api_level_to_level,
                        request,
                        asset_base_url,
                        i,
                        request.state.levelbg,
                    )
                    for i in random_response["data"][:4]
                ]
            )
            newest = await asyncio.gather(
                *[
                    request.app.run_blocking(
                        api_level_to_level,
                        request,
                        asset_base_url,
                        i,
                        request.state.levelbg,
                    )
                    for i in newest_response["data"][:4]
                ]
            )
            sections: List[LevelItemSection] = [
                # create_section(
                #     locale.staff_pick,
                #     item_type,
                #     handle_item_uwu(newest, uwu_level),
                #     icon="trophy",
                # ),
                create_section(
                    "#NEWEST",
                    item_type,
                    handle_item_uwu(newest, uwu_level),
                    icon="level",
                ),
                create_section(
                    "#RANDOM",
                    item_type,
                    handle_item_uwu(random, uwu_level),
                    icon="level",
                ),
            ]
            options = []
            options.append(
                ServerFormOptionsFactory.server_text_option(
                    query="keywords",
                    name="#KEYWORDS",
                    required=False,
                    default="",
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
                    default=0,
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
                    default=99,
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
                    default="",
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
                    default="",
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
                    default="",
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
                        default=False,
                    )
                )

            options.append(
                ServerFormOptionsFactory.server_slider_option(
                    query="min_likes",
                    name=locale.search.MIN_LIKES,
                    required=False,
                    default=0,
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
                    default=9999,
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
                    default="",
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
                    default="created_at",
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
                    default="desc",
                    values=[
                        {"name": "desc", "title": locale.search.DESCENDING},
                        {"name": "asc", "title": locale.search.ASCENDING},
                    ],
                )
            )
            search_form = create_server_form(
                type="advanced",
                title=locale.search.ADVANCED_SEARCH,
                require_confirmation=False,
                options=options,
            )
            searches.append(search_form)
        # elif item_type == "replays":
        #     data = await request.app.run_blocking(compile_replays_list, request.app.base_url)
        #     sections: List[ReplayItemSection] = [
        #         create_section(
        #             "Replays", item_type, data[:5], description=handle_uwu(
        #     locale.server_description or request.app.config["description"],
        #     uwu_level,
        # ), icon="replay"
        #         )
        #     ]
        # elif item_type == "rooms":
        #     data = await request.app.run_blocking(compile_rooms_list, request.app.base_url)
        #     sections: List[RoomItemSection] = [
        #         create_section(
        #             "Rooms", item_type, data[:5], description=handle_uwu(
        #     locale.server_description or request.app.config["description"],
        #     uwu_level,
        # ), icon="room"
        #         )
        #     ]
        else:
            raise HTTPException(
                status_code=404, detail=locale.item_type_not_found(item_type)
            )
        data: ServerItemInfo = {
            "sections": sections,
        }
        if banner_srl:
            data["banner"] = banner_srl
        if searches:
            data["searches"] = searches
        return data
