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
        query_params = dict(request.query_params)
        query_params.pop("localization", None)
        query_params.pop("page", None)
        searching = False
        if item_type == "engines":
            data = await request.app.run_blocking(
                compile_engines_list, request.app.base_url
            )
        elif item_type == "skins":
            data = await request.app.run_blocking(
                compile_skins_list, request.app.base_url
            )
        elif item_type == "backgrounds":
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
            data = sort_posts_by_newest(data)
        # elif item_type == "playlists":
        #     data = await request.app.run_blocking(compile_playlists_list, request.app.base_url)
        elif item_type == "levels":
            raw_data = await request.app.run_blocking(
                compile_static_levels_list, request.app.base_url
            )
            # XXX: do japanese/romaji searching via CUTLET python lib
            # XXX: fuzzy matching...
            filtered_data = []
            type_ = query_params.get("type")
            if type_ == "quick":
                keywords = query_params.get("keywords")
                if keywords:
                    searching = True
                    excluded_keys = ["description", "name"]
                    for item in raw_data:
                        if any(
                            keywords.lower() in str(value).lower()
                            and key not in excluded_keys
                            for key, value in item.items()
                        ):
                            filtered_data.append(item)
                    data = filtered_data
                else:
                    data = raw_data
            elif type_ == "advanced":
                searching = True
                title_search = query_params["title"]
                for item in raw_data:
                    if (
                        "title" in item
                        and title_search.lower() in item["title"].lower()
                    ):
                        filtered_data.append(item)
                data = filtered_data
            else:
                data = raw_data
        # elif item_type == "replays":
        #     data = await request.app.run_blocking(compile_replays_list, request.app.base_url)
        # elif item_type == "rooms":
        #     data = await request.app.run_blocking(compile_rooms_list, request.app.base_url)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Item "{item_type}" not found.',
            )
        pages = list_to_pages(data, request.app.get_items_per_page(item_type))
        if len(pages) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Could not find any {item_type}."
                    if not searching
                    else f"Could not find any {item_type} matching your search."
                ),
            )
        page_data = pages[page]

        return {"pageCount": len(pages), "items": page_data}
