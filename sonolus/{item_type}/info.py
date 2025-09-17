donotload = False

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
)

router = APIRouter()

from locales.locale import Locale
from helpers.owoify import handle_uwu, handle_item_uwu

import aiohttp


def setup():
    @router.get("/")
    async def main(request: Request, item_type: ItemType):
        query_params = dict(request.query_params)
        for item in request.app.remove_config_queries:
            query_params.pop(item, None)
        locale = Locale.get_messages(request.state.localization)
        uwu_level = request.state.uwu if request.state.localization == "en" else "off"
        banner_srl = await request.app.run_blocking(compile_banner)
        searches = []
        auth = request.headers.get("Sonolus-Session")

        if item_type == "engines":
            data = await request.app.run_blocking(
                compile_engines_list, request.app.base_url
            )
            sections: List[EngineItemSection] = [
                create_section(
                    "Engines",
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
                    "Skins",
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
                compile_backgrounds_list, request.app.base_url
            )
            sections: List[BackgroundItemSection] = [
                create_section(
                    "Backgrounds",
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
                    "Effects",
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
                    "Particles",
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
                    "Newest Posts",
                    item_type,
                    handle_item_uwu(data[:5], uwu_level),
                    icon="post",
                )
            ]
        # elif item_type == "playlists":
        #     data = await request.app.run_blocking(compile_playlists_list, request.app.base_url)
        #     sections: List[PlaylistItemSection] = [
        #         create_section(
        #             "Playlists", item_type, data[:5], description=handle_uwu(
        #     locale.server_description or request.app.config["description"],
        #     uwu_level,
        # ), icon="playlist"
        #         )
        #     ]
        elif item_type == "levels":
            headers = {request.app.auth_header: request.app.auth}
            if auth:
                headers["authorization"] = auth
            async with aiohttp.ClientSession(headers=headers) as cs:
                async with cs.get(
                    request.app.api_config["url"] + "/api/charts/",
                    params={"type": "random"},
                ) as req:
                    response = await req.json()
            data = []
            for i in response["data"]:
                leveldata = {
                    "name": f"UnCh-{i['id']}",
                    "source": request.app.base_url,
                    "version": 1,
                    "rating": i["rating"],
                    "artists": i["artists"],
                    "author": i["author_full"],
                    "title": i["title"],
                    "tags": [
                        {
                            "title": str(i["like_count"]),
                            "icon": "heart" if i.get("liked") else "heartHollow",
                        }
                    ]
                    + [{"title": tag, "icon": "tag"} for tag in i["tags"]],
                    "engine": compile_engines_list(request.app.base_url)[0],
                    "useSkin": {"useDefault": True},
                    "useEffect": {"useDefault": True},
                    "useParticle": {"useDefault": True},
                    "useBackground": {"useDefault": True},  # XXX
                    "cover": {
                        "hash": i["jacket_file_hash"],
                        "url": "/".join(
                            [
                                response["asset_base_url"].removesuffix("/"),
                                i["author"],
                                i["id"],
                                i["jacket_file_hash"],
                            ]
                        ),
                    },
                    "data": {
                        "hash": i["chart_file_hash"],
                        "url": "/".join(
                            [
                                response["asset_base_url"].removesuffix("/"),
                                i["author"],
                                i["id"],
                                i["chart_file_hash"],
                            ]
                        ),
                    },
                    "bgm": {
                        "hash": i["music_file_hash"],
                        "url": "/".join(
                            [
                                response["asset_base_url"].removesuffix("/"),
                                i["author"],
                                i["id"],
                                i["music_file_hash"],
                            ]
                        ),
                    },
                }
                if i["preview_file_hash"]:
                    leveldata["preview"] = {
                        "hash": i["preview_file_hash"],
                        "url": "/".join(
                            [
                                response["asset_base_url"].removesuffix("/"),
                                i["author"],
                                i["id"],
                                i["preview_file_hash"],
                            ]
                        ),
                    }
                data.append(leveldata)
            sections: List[LevelItemSection] = [
                create_section(
                    "Random",
                    item_type,
                    handle_item_uwu(data, uwu_level),
                    icon="level",
                )
            ]
            options = []

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
                        default=True,
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
