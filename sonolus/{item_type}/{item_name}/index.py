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

router = APIRouter()

from locales.locale import Locale
from helpers.owoify import handle_item_uwu


def setup():
    @router.get("/")
    async def main(request: Request, item_type: ItemType, item_name: str):
        query_params = dict(request.query_params)
        for item in request.app.remove_config_queries:
            query_params.pop(item, None)
        locale = Locale.get_messages(request.state.localization)
        uwu_level = request.state.uwu if request.state.localization == "en" else "off"
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
                level_data = None  # get from api
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
            data = []
        elif item_type == "levels":
            data = []
        # elif item_type == "replays":
        #     data = await request.app.run_blocking(compile_replays_list, request.app.base_url)
        # elif item_type == "rooms":
        #     data = await request.app.run_blocking(compile_rooms_list, request.app.base_url)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=locale.item_not_found(item_type),
            )
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
            "actions": [],
            "hasCommunity": False,
            "leaderboards": [],
            "sections": [],
        }
        if data.get("description"):
            detail["description"] = data["description"]
        return detail
