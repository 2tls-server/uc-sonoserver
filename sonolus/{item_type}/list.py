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
    # compile_playlists_list,
    compile_static_levels_list,
    # compile_replays_list,
    # compile_rooms_list
    sort_posts_by_newest,
)
from helpers.paginate import list_to_pages
from helpers.sonolus_typings import ItemType

router = APIRouter()


def setup():
    @router.get("/")
    async def main(request: Request, item_type: ItemType, page: int = 0):
        if item_type == "engines":
            data = compile_engines_list(request.app.base_url)
        elif item_type == "skins":
            data = compile_skins_list(request.app.base_url)
        elif item_type == "backgrounds":
            data = compile_backgrounds_list(request.app.base_url)
        elif item_type == "effects":
            data = compile_effects_list(request.app.base_url)
        elif item_type == "particles":
            data = compile_particles_list(request.app.base_url)
        elif item_type == "posts":
            data = compile_static_posts_list(request.app.base_url)
            data = sort_posts_by_newest(data)
        # elif item_type == "playlists":
        #     data = compile_playlists_list(request.app.base_url)
        elif item_type == "levels":
            data = compile_static_levels_list(request.app.base_url)
        # elif item_type == "replays":
        #     data = compile_replays_list(request.app.base_url)
        # elif item_type == "rooms":
        #     data = compile_rooms_list(request.app.base_url)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Item "{item_type}" not found.',
            )
        pages = list_to_pages(data, request.app.get_items_per_page(item_type))
        page_data = pages[page]

        return {"pageCount": len(pages), "items": page_data}
