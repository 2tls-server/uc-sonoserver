import asyncio

from typing import List

from fastapi import APIRouter, Request
from fastapi import HTTPException, status
from helpers.sonolus_typings import ItemType
from helpers.models import (
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
    uwu_level = request.state.uwu
    banner_srl = await request.app.run_blocking(compile_banner)
    searches = []
    creates = []
    auth = request.headers.get("Sonolus-Session")

    if item_type == "posts":
        data = await request.app.run_blocking(
            compile_static_posts_list, request.app.base_url
        )
        data = sort_posts_by_newest(data)
        sections: List[PostItemSection] = [
            create_section(
                "#NEWEST",
                item_type,
                handle_item_uwu(data[:5], request.state.localization, uwu_level),
                icon="post",
            )
        ]
        if auth:
            headers = {request.app.auth_header: request.app.auth}
            headers["authorization"] = auth
            async with aiohttp.ClientSession(headers=headers) as cs:
                async with cs.get(
                    request.app.api_config["url"] + f"/api/accounts/notifications/",
                    params={"only_unread": 1},
                ) as req:
                    response = await req.json()
            raw_notifs = response.get("notifications", [])
            notifs = [api_notif_to_post(request, i) for i in raw_notifs]
            if notifs:
                sections.insert(
                    0,
                    create_section(
                        locale.notification.UNREAD,
                        item_type,
                        # don't uwuify. these are important
                        notifs,
                        icon="bell",
                        description=locale.notification.NOTIFICATION_DESC_UNREAD,
                    ),
                )
            else:
                sections.insert(
                    0,
                    create_section(
                        locale.notification.NOTIFICATION,
                        item_type,
                        [],
                        icon="bell",
                        description=locale.notification.NOTIFICATION_DESC,
                    ),
                )
    
    data: ServerItemInfo = {
        "sections": sections,
    }
    if banner_srl:
        data["banner"] = banner_srl
    if searches:
        data["searches"] = searches
    if creates:
        data["creates"] = creates
    return data
