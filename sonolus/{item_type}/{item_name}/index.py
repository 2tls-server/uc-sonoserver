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
from helpers.models import ServerItemDetails, ServerItem
from helpers.data_helpers import create_server_form, ServerFormOptionsFactory
from helpers.api_helpers import api_level_to_level, api_notif_to_post

router = APIRouter()

from locales.locale import Loc
from helpers.owoify import handle_item_uwu, handle_uwu

import aiohttp


@router.get("/")
async def main(request: Request, item_type: ItemType, item_name: str):
    locale: Loc = request.state.loc
    item_data: ServerItem = None

    match item_type:
        case "engines":
            data = await request.app.run_blocking(
                compile_engines_list, request.app.base_url, request.state.localization
            )
        case "skins":
            data = await request.app.run_blocking(compile_skins_list, request.app.base_url)
        case "backgrounds":
            item_data = (
                await request.app.run_blocking(
                    compile_backgrounds_list,
                    request.app.base_url,
                    request.state.localization,
                )
            )[0]
        case "effects":
            data = await request.app.run_blocking(
                compile_effects_list, request.app.base_url
            )     
        case "particles":
            data = await request.app.run_blocking(
                compile_particles_list, request.app.base_url
            )
        # case "replays":
        #     data = await request.app.run_blocking(compile_replays_list, request.app.base_url)
        # case "rooms":
        #     data = await request.app.run_blocking(compile_rooms_list, request.app.base_url)
        case _:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=locale.item_not_found(item_type, item_name),
            )
        
    if not item_data:
        item_data = next((i for i in data if i.name == item_name), None)
        if not item_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=locale.item_not_found(
                    item_type.capitalize().removesuffix("s"), item_name
                ),
            )

    return ServerItemDetails(
        item=item_data,
        description=item_data.description if hasattr(item_data, "description") and item_data.description else None,
        actions=[],
        hasCommunity=False,
        leaderboards=[],
        sections=[]
    )
