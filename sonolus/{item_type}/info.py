donotload = False

from typing import List
import random

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


def setup():
    @router.get("/")
    async def main(request: Request, item_type: ItemType):
        extended_description = ""
        banner_srl = await request.app.run_blocking(compile_banner)
        searches = []
        if item_type == "engines":
            data = await request.app.run_blocking(
                compile_engines_list, request.app.base_url
            )
            sections: List[EngineItemSection] = [
                create_section(
                    "Engines",
                    item_type,
                    data[:5],
                    description=f"{request.app.config['description']}\n{extended_description}",
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
                    data[:5],
                    description=f"{request.app.config['description']}\n{extended_description}",
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
                    data[:5],
                    description=f"{request.app.config['description']}\n{extended_description}",
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
                    data[:5],
                    description=f"{request.app.config['description']}\n{extended_description}",
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
                    data[:5],
                    description=f"{request.app.config['description']}\n{extended_description}",
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
                create_section("Newest Posts", item_type, data[:5], icon="post")
            ]
        # elif item_type == "playlists":
        #     data = await request.app.run_blocking(compile_playlists_list, request.app.base_url)
        #     sections: List[PlaylistItemSection] = [
        #         create_section(
        #             "Playlists", item_type, data[:5], description=f"{request.app.config['description']}\n{extended_description}", icon="playlist"
        #         )
        #     ]
        elif item_type == "levels":
            data = []
        # elif item_type == "replays":
        #     data = await request.app.run_blocking(compile_replays_list, request.app.base_url)
        #     sections: List[ReplayItemSection] = [
        #         create_section(
        #             "Replays", item_type, data[:5], description=f"{request.app.config['description']}\n{extended_description}", icon="replay"
        #         )
        #     ]
        # elif item_type == "rooms":
        #     data = await request.app.run_blocking(compile_rooms_list, request.app.base_url)
        #     sections: List[RoomItemSection] = [
        #         create_section(
        #             "Rooms", item_type, data[:5], description=f"{request.app.config['description']}\n{extended_description}", icon="room"
        #         )
        #     ]
        else:
            raise HTTPException(
                status_code=404, detail=f'Item "{item_type}" not found.'
            )
        data: ServerItemInfo = {
            "sections": sections,
        }
        if banner_srl:
            data["banner"] = banner_srl
        if searches:
            data["searches"] = searches
        return data
