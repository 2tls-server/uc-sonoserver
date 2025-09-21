import aiohttp

from fastapi import APIRouter, Request, HTTPException, status

from helpers.data_compilers import compile_banner
from helpers.datastructs import ServerInfoButton
from helpers.data_helpers import (
    ServerFormOptionsFactory,
)

from typing import List

from locales.locale import Locale
from helpers.owoify import handle_uwu

router = APIRouter()


@router.get("/")
async def main(request: Request):
    try:
        locale = Locale.get_messages(request.state.localization)
    except AssertionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    uwu_level = request.state.uwu
    # Assume logged in
    # We only need to validate the session
    # If it's a request that updates something, or access something private
    logged_in = False
    if request.headers.get("Sonolus-Session"):
        logged_in = True

    banner_srl = await request.app.run_blocking(compile_banner)
    button_list = [
        "authentication",
        "post",
        "level",
        "configuration",
        # "playlist",
        # "skin",
        # "background",
        # "effect",
        # "particle",
        # "engine",
    ]
    if logged_in:
        button_list.append("playlist")
    options = []
    if request.state.localization == "en":
        option = ServerFormOptionsFactory.server_select_option(
            query="uwu",
            name="UwU >.<",
            required=False,
            default="off",
            values=[
                {"name": "off", "title": "OFF"},
                {"name": "owo", "title": "SLIGHTLY"},
                {"name": "uwu", "title": "A LOT"},
                {"name": "uvu", "title": "EXTREME"},
            ],
            description="Uwuify your menu (EN ONLY).",
        )
        options.append(option)
    options.append(
        ServerFormOptionsFactory.server_select_option(
            query="levelbg",
            name=locale.background.USEBACKGROUND,
            required=False,
            default="default_or_v3",
            values=[
                {"name": "default_or_v3", "title": locale.background.DEF_OR_V3},
                {"name": "v3", "title": locale.background.V3},
                {"name": "default_or_v1", "title": locale.background.DEF_OR_V1},
                {"name": "v1", "title": locale.background.V1},
            ],
            description=locale.background.USEBACKGROUNDDESC,
        )
    )
    options.append(
        ServerFormOptionsFactory.server_select_option(
            query="stpickconfig",
            name=locale.staff_pick,
            required=False,
            default="off",
            values=[
                {"name": "off", "title": locale.search.STAFF_PICK_OFF},
                {"name": "true", "title": locale.search.STAFF_PICK_TRUE},
                {"name": "false", "title": locale.search.STAFF_PICK_FALSE},
            ],
            description=locale.search.STAFF_PICK_CONFIG_DESC
            + "\n"
            + locale.staff_pick_desc,
        )
    )
    desc = locale.server_description or request.app.config["description"]

    auth = request.headers.get("Sonolus-Session")
    login_message = False
    if auth:
        try:
            headers = {request.app.auth_header: request.app.auth}
            headers["authorization"] = auth
            async with aiohttp.ClientSession(headers=headers) as cs:
                async with cs.get(
                    request.app.api_config["url"] + f"/api/accounts/session/account/",
                ) as req:
                    response = await req.json()
            desc += "\n\n" + ("-" * 40) + "\n"
            desc += "\n" + locale.welcome(response["sonolus_username"])
            desc += "\n\n" + ("-" * 40) + "\n"
            if response.get("mod") or response.get("admin"):
                if response.get("admin"):
                    desc += f"\n{locale.is_admin}\n{locale.admin_powers}\n{locale.mod_powers}"
                else:
                    desc += f"\n{locale.is_mod}\n{locale.mod_powers}"
            login_message = True
        except:
            pass
    if not login_message:
        desc = locale.server_description or request.app.config["description"]
        desc += "\n\n" + ("-" * 40) + "\n"
        desc += "\n" + locale.not_logged_in
    buttons: List[ServerInfoButton] = [{"type": button} for button in button_list]
    data = {
        "title": request.app.config["name"],
        "description": handle_uwu(
            desc,
            uwu_level,
        ),
        "buttons": buttons,
        "configuration": {"options": options},
    }
    if banner_srl:
        data["banner"] = banner_srl
    return data
