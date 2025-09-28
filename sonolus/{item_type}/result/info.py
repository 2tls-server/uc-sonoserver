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
from helpers.api_helpers import api_level_to_level, api_notif_to_post
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

from locales.locale import Loc
from helpers.owoify import handle_uwu, handle_item_uwu

import aiohttp


@router.get("/")
async def main(request: Request, item_type: ItemType):
    locale: Loc = request.state.loc
    auth = request.headers.get("Sonolus-Session")

    if item_type == "levels":
        pass
    else:
        raise HTTPException(
            status_code=404, detail=locale.item_type_not_found(item_type)
        )
    submit_form = {
        "type": "replay",
        "title": "#REPLAY",
        "requireConfirmation": False,
        "options": [],
    }
    data = {"submits": []}  # [submit_form]
    return data
