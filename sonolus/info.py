donotload = False

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


def setup():
    @router.get("/")
    async def main(request: Request):
        try:
            locale = Locale.get_messages(request.state.localization)
        except AssertionError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported locale"
            )
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
        buttons: List[ServerInfoButton] = [{"type": button} for button in button_list]
        data = {
            "title": request.app.config["name"],
            "description": handle_uwu(
                locale.server_description or request.app.config["description"],
                uwu_level,
            ),
            "buttons": buttons,
            "configuration": {"options": options},
        }
        if banner_srl:
            data["banner"] = banner_srl
        return data
