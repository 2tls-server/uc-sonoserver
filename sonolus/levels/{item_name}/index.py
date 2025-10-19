from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from helpers.models import ServerItemDetails, get_item_type, APIServerGetChartResponse
from helpers.data_helpers import create_server_form, ServerFormOptionsFactory
from helpers.api_helpers import api_level_to_level

router = APIRouter()

from locales.locale import Loc
from helpers.owoify import handle_item_uwu

import aiohttp


@router.get("/")
async def main(request: Request, item_name: str):
    locale: Loc = request.state.loc
    uwu_level = request.state.uwu
    uwu_handled = False
    item_data = None
    auth = request.headers.get("Sonolus-Session")
    actions = []
    
    headers = {request.app.auth_header: request.app.auth}
    if auth:
        headers["authorization"] = auth
    async with aiohttp.ClientSession(headers=headers) as cs:
        async with cs.get(
            request.app.api_config["url"]
            + f"/api/charts/{item_name.removeprefix('UnCh-')}/"
        ) as req:
            data = await req.json()
            if req.status != 200:
                raise HTTPException(
                    status_code=req.status, detail=response["detail"]
                )
            response = APIServerGetChartResponse.model_validate_json(await req.json())

    asset_base_url = response.asset_base_url.removesuffix("/")
    liked = response.data.liked
    like_count = response.data.like_count
    item_data, desc = await request.app.run_blocking(
        api_level_to_level,
        request,
        asset_base_url,
        response.data,
        request.state.levelbg,
        include_description=True,
        context="level",
    )
    if auth:
        if liked:
            actions.append(
                create_server_form(
                    type="unlike",
                    title=f"Unlike ({like_count:,})",
                    icon="heart",
                    require_confirmation=False,
                    options=[],
                )
            )
        else:
            actions.append(
                create_server_form(
                    type="like",
                    title=f"Like ({like_count:,})",
                    icon="heartHollow",
                    require_confirmation=False,
                    options=[],
                )
            )
    if response.get("mod") or response.get("owner"):
        if response.get("owner") or response.get("admin"):
            actions.append(
                create_server_form(
                    type="delete",
                    title="#DELETE",
                    icon="delete",
                    require_confirmation=True,
                    options=[],
                )
            )
        VISIBILITIES = {
            "PUBLIC": {"title": "#PUBLIC", "icon": "globe"},
            "PRIVATE": {"title": "#PRIVATE", "icon": "lock"},
            "UNLISTED": {
                "title": locale.search.VISIBILITY_UNLISTED,
                "icon": "unlock",
            },
        }
        current = response["data"]["status"]
        vis_values = []
        for s, meta in VISIBILITIES.items():
            vis_values.append({"name": s, "title": meta["title"]})
        the_option = ServerFormOptionsFactory.server_select_option(
            query="visibility",
            name=locale.search.VISIBILITY,
            required=True,
            default=current,
            values=vis_values,
        )
        the_action = create_server_form(
            type="visibility",
            title=locale.search.VISIBILITY,
            icon=VISIBILITIES[current]["icon"],
            require_confirmation=True,
            options=[the_option],
        )
        actions.append(the_action)
        if response.get("mod"):
            actions.append(
                create_server_form(
                    type="rerate",
                    title=locale.rerate,
                    icon="plus",
                    require_confirmation=True,
                    options=[
                        ServerFormOptionsFactory.server_text_option(
                            query="constant",
                            name="#RATING",
                            required=True,
                            default="",
                            placeholder=str(response["data"]["rating"]),
                            description=locale.rerate_desc,
                            shortcuts=[str(response["data"]["rating"])],
                            limit=9,  # -999.1234, 9 max possible characters
                        )
                    ],
                )
            )
            if response["data"].get("staff_pick"):
                actions.append(
                    create_server_form(
                        type="staff_pick_delete",
                        title=locale.staff_pick_remove,
                        icon="delete",
                        require_confirmation=True,
                        options=[
                            ServerFormOptionsFactory.server_toggle_option(
                                query="_",
                                name="#CONFIRM",
                                required=True,
                                default=False,
                                description=locale.staff_pick_confirm,  # no uwu
                            )
                        ],
                    )
                )
            else:
                actions.append(
                    create_server_form(
                        type="staff_pick_add",
                        title=locale.staff_pick_add,
                        icon="trophy",
                        require_confirmation=True,
                        options=[
                            ServerFormOptionsFactory.server_toggle_option(
                                query="_",
                                name="#CONFIRM",
                                required=True,
                                default=False,
                                description=locale.staff_pick_confirm,  # no uwu
                            )
                        ],
                    )
                )
        if desc:
            item_data["description"] = desc
        uwu_handled = True

    if uwu_handled:
        data = item_data
    else:
        data = handle_item_uwu([item_data], request.state.localization, uwu_level)[0]
    detail: ServerItemDetails = {
        "item": data,
        "actions": actions,
        "hasCommunity": True,
        "leaderboards": [], # TODO
        "sections": [],
    }
    if data.get("description"):
        detail["description"] = data["description"]
    return detail
