donotload = False

from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from helpers.data_compilers import (
    compile_engines_list,
    compile_backgrounds_list,
    compile_effects_list,
    compile_particles_list,
    compile_skins_list,
    compile_static_posts_list,
    # compile_replays_list,
    # compile_rooms_list
)
from helpers.sonolus_typings import ItemType
from helpers.datastructs import ServerItemDetails, get_item_type
from helpers.data_helpers import create_server_form, ServerFormOptionsFactory

router = APIRouter()

from locales.locale import Locale
from helpers.owoify import handle_item_uwu

import aiohttp


def setup():
    @router.get("/")
    async def main(request: Request, item_type: ItemType, item_name: str):
        query_params = dict(request.query_params)
        for item in request.app.remove_config_queries:
            query_params.pop(item, None)
        locale = Locale.get_messages(request.state.localization)
        uwu_level = request.state.uwu if request.state.localization == "en" else "off"
        item_data = None
        auth = request.headers.get("Sonolus-Session")
        actions = []

        if item_type == "engines":
            data = await request.app.run_blocking(
                compile_engines_list, request.app.base_url
            )
        elif item_type == "skins":
            data = await request.app.run_blocking(
                compile_skins_list, request.app.base_url
            )
        elif item_type == "backgrounds":
            if item_name.startswith("levelbg-"):
                level_data = None  # XXX: get from api
                data = []
            else:
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
            # maybe also grab non-static posts lol
        elif item_type == "playlists":
            session = request.headers.get("Sonolus-Session")
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Not logged in."
                )
            data = []  # XXX: implement
        elif item_type == "levels":
            headers = {request.app.auth_header: request.app.auth}
            if auth:
                headers["authorization"] = auth
            async with aiohttp.ClientSession(headers=headers) as cs:
                async with cs.get(
                    request.app.api_config["url"] + f"/api/charts/{item_name}/"
                ) as req:
                    response = await req.json()
            liked = response["data"].get("liked")
            item_data = {
                "name": f"UnCh-{response['data']['id']}",
                "source": request.app.base_url,
                "version": 1,
                "rating": response["data"]["rating"],
                "artists": response["data"]["artists"],
                "author": response["data"]["author_full"],
                "title": response["data"]["title"],
                "tags": [
                    {
                        "title": str(response["data"]["like_count"]),
                        "icon": "heart" if liked else "heartHollow",
                    }
                ]
                + [{"title": tag, "icon": "tag"} for tag in response["data"]["tags"]],
                "engine": compile_engines_list(request.app.base_url)[0],
                "useSkin": {"useDefault": True},
                "useEffect": {"useDefault": True},
                "useParticle": {"useDefault": True},
                "useBackground": {"useDefault": True},  # XXX
                "cover": {
                    "hash": response["data"]["jacket_file_hash"],
                    "url": "/".join(
                        [
                            response["asset_base_url"].removesuffix("/"),
                            response["data"]["author"],
                            response["data"]["id"],
                            response["data"]["jacket_file_hash"],
                        ]
                    ),
                },
                "data": {
                    "hash": response["data"]["chart_file_hash"],
                    "url": "/".join(
                        [
                            response["asset_base_url"].removesuffix("/"),
                            response["data"]["author"],
                            response["data"]["id"],
                            response["data"]["chart_file_hash"],
                        ]
                    ),
                },
                "bgm": {
                    "hash": response["data"]["music_file_hash"],
                    "url": "/".join(
                        [
                            response["asset_base_url"].removesuffix("/"),
                            response["data"]["author"],
                            response["data"]["id"],
                            response["data"]["music_file_hash"],
                        ]
                    ),
                },
            }
            if response["data"]["preview_file_hash"]:
                item_data["preview"] = {
                    "hash": response["data"]["preview_file_hash"],
                    "url": "/".join(
                        [
                            response["asset_base_url"].removesuffix("/"),
                            response["data"]["author"],
                            response["data"]["id"],
                            response["data"]["preview_file_hash"],
                        ]
                    ),
                }
            if auth:
                if liked:
                    actions.append(
                        create_server_form(
                            type="unlike",
                            title="Unlike",
                            icon="heart",
                            require_confirmation=False,
                            options=[],
                        )
                    )
                else:
                    actions.append(
                        create_server_form(
                            type="like",
                            title="Like",
                            icon="heartHollow",
                            require_confirmation=False,
                            options=[],
                        )
                    )
        # elif item_type == "replays":
        #     data = await request.app.run_blocking(compile_replays_list, request.app.base_url)
        # elif item_type == "rooms":
        #     data = await request.app.run_blocking(compile_rooms_list, request.app.base_url)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=locale.item_not_found(item_type),
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
