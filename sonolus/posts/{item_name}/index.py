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
from helpers.models import ServerItemDetails, get_item_type
from helpers.data_helpers import create_server_form, ServerFormOptionsFactory
from helpers.api_helpers import api_level_to_level, api_notif_to_post

router = APIRouter()

from locales.locale import Loc
from helpers.owoify import handle_item_uwu, handle_uwu

import aiohttp


@router.get("/")
async def main(request: Request, item_type: ItemType, item_name: str):
    locale: Loc = request.state.loc
    uwu_level = request.state.uwu
    community = False
    uwu_handled = False
    item_data = None
    auth = request.headers.get("Sonolus-Session")
    actions = []

    if item_type == "posts":
        if item_name.startswith("notification-"):
            if not auth:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=locale.not_found
                )
            headers = {"authorization": auth}
            async with aiohttp.ClientSession(headers=headers) as cs:
                async with cs.get(
                    request.app.api_config["url"]
                    + f"/api/accounts/notifications/{item_name.removeprefix('notification-')}/"
                ) as req:
                    if req.status != 200:
                        raise HTTPException(
                            status_code=req.status, detail=locale.not_found
                        )
                    data = await req.json()
            item_data, desc = api_notif_to_post(request, data, include_description=True)
            item_data["description"] = desc
            uwu_handled = True  # don't uwu important info
        else:
            data = await request.app.run_blocking(
                compile_static_posts_list, request.app.base_url
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
        data = handle_item_uwu([item_data], request.state.localization, uwu_level)[0]
    detail: ServerItemDetails[T] = {
        "item": data,
        "actions": actions,
        "hasCommunity": community,
        "leaderboards": [],
        "sections": [],
    }
    if data.get("description"):
        detail["description"] = data["description"]
    return detail
