donotload = False

from fastapi import APIRouter, Request

from helpers.data_compilers import compile_banner
from helpers.datastructs import ServerInfoButton
from helpers.data_helpers import (
    ServerFormOptionsFactory,
)

from typing import List

router = APIRouter()


def setup():
    @router.get("/")
    async def main(request: Request):
        # Assume logged in
        # We only need to validate the session
        # If it's a request that updates something, or access something private
        logged_in = False
        if request.headers.get("Sonolus-Session"):
            logged_in = True
        extended_description = ""

        # XXX https://wiki.sonolus.com/custom-server-specs/endpoints/get-sonolus-info
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
        buttons: List[ServerInfoButton] = [{"type": button} for button in button_list]
        data = {
            "title": request.app.config["name"],
            "description": f"{request.app.config['description']}\n{extended_description}",
            "buttons": buttons,
            "configuration": {
                "options": [
                    ServerFormOptionsFactory.server_select_option(
                        query="uwu",
                        name="UwU >.<",
                        required=False,
                        default="off",
                        values=[
                            {"name": "off", "title": "OFF"},
                            {"name": "uwu", "title": "ON"},
                        ],
                        description="Uwuify your menu (EN ONLY).",
                    )
                ]
            },
        }
        if banner_srl:
            data["banner"] = banner_srl
        return data
