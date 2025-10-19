from fastapi import APIRouter, Request, Query
from fastapi import HTTPException, status

from helpers.data_compilers import (
    compile_engines_list,
    compile_backgrounds_list,
    compile_effects_list,
    compile_particles_list,
    compile_skins_list,
    # compile_replays_list,
    # compile_rooms_list
)
from helpers.paginate import list_to_pages
from helpers.sonolus_typings import ItemType
from helpers.models import ServerItemList

router = APIRouter()

from locales.locale import Loc
from helpers.owoify import handle_item_uwu

type_func = type


@router.get("/", response_model=ServerItemList)
async def main(
    request: Request,
    item_type: ItemType,
    page: int = Query(0, ge=0),
):
    locale: Loc = request.state.loc
    uwu_level = request.state.uwu
    searching = False

    match item_type:
        case "engines":
            data = await request.app.run_blocking(
                compile_engines_list, request.app.base_url, request.state.localization
            )
        case "skins":
            data = await request.app.run_blocking(compile_skins_list, request.app.base_url)
            data = [
                item
                for item in data
                if (item.get("engines") == None)
                or (
                    (type_func(item.get("engines")) in [list, tuple])
                    and (request.state.engine in item.get("engines"))
                )
            ]

        case "backgrounds":
            data = await request.app.run_blocking(
                compile_backgrounds_list,
                request.app.base_url,
                request.state.localization,
            )
        case "effects":
            data = await request.app.run_blocking(
                compile_effects_list, request.app.base_url
            )
        case "particles":
            data = await request.app.run_blocking(
                compile_particles_list, request.app.base_url
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=locale.item_type_not_found(item_type),
            )
        
    pages = list_to_pages(data, request.app.get_items_per_page(item_type))
    if len(pages) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                locale.items_not_found(item_type)
                if not searching
                else locale.items_not_found_search(item_type)
            ),
        )
    
    try:
        page_data = pages[page]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="hi stop hitting our api thanks",
        )
    
    page_data = handle_item_uwu(page_data, request.state.localization, uwu_level)
    return ServerItemList(
        pageCount=len(pages),
        items=page_data
    )
