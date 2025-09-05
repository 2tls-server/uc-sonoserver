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
)
from helpers.section_helper import create_section
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
        banner_srl = compile_banner()
        if item_type == "engines":
            data = compile_engines_list(request.app.base_url)
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
            data = compile_skins_list(request.app.base_url)
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
            data = compile_backgrounds_list(request.app.base_url)
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
            data = compile_effects_list(request.app.base_url)
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
            data = compile_particles_list(request.app.base_url)
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
            data = compile_static_posts_list(request.app.base_url)
            # grab non-static posts too
            # sort em
            data = sort_posts_by_newest(data)
            sections: List[PostItemSection] = [
                create_section("Newest Posts", item_type, data[:5], icon="post")
            ]
        # elif item_type == "playlists":
        #     data = compile_playlists_list(request.app.base_url)
        #     sections: List[PlaylistItemSection] = [
        #         create_section(
        #             "Playlists", item_type, data[:5], description=f"{request.app.config['description']}\n{extended_description}", icon="playlist"
        #         )
        #     ]
        # elif item_type == "levels":
        #     data = compile_levels_list(request.app.base_url)
        #     sections: List[LevelItemSection] = [
        #         create_section(
        #             "Levels", item_type, data[:5], description=f"{request.app.config['description']}\n{extended_description}", icon="level"
        #         )
        #     ]
        # elif item_type == "replays":
        #     data = compile_replays_list(request.app.base_url)
        #     sections: List[ReplayItemSection] = [
        #         create_section(
        #             "Replays", item_type, data[:5], description=f"{request.app.config['description']}\n{extended_description}", icon="replay"
        #         )
        #     ]
        # elif item_type == "rooms":
        #     data = compile_rooms_list(request.app.base_url)
        #     sections: List[RoomItemSection] = [
        #         create_section(
        #             "Rooms", item_type, data[:5], description=f"{request.app.config['description']}\n{extended_description}", icon="room"
        #         )
        #     ]
        else:
            raise HTTPException(
                status_code=404, detail=f'Item "{item_type}" not found.'
            )
        data = {
            "sections": sections,
        }
        if banner_srl:
            data["banner"] = banner_srl
        return data
