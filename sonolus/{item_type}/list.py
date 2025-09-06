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
            raw_data = compile_static_levels_list(request.app.base_url)
            # XXX: do japanese/romaji searching via CUTLET python lib
            # XXX: fuzzy matching...
            filtered_data = []
            type_ = query_params.get("type")
            print(type_)
            if type_ == "quick":
                keywords = query_params.get("keywords")
                if keywords:
                    excluded_keys = ["description"]
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
