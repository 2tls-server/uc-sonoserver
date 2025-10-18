import base64, decimal
from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from helpers.sonolus_typings import ItemType

from pydantic import BaseModel

from urllib.parse import parse_qs, urlencode

router = APIRouter()

from locales.locale import Loc

import aiohttp


class ServerSubmitItemActionRequest(BaseModel):
    values: str


@router.post("/")
async def main(
    request: Request,
    item_type: ItemType,
    item_name: str,
    data: ServerSubmitItemActionRequest,
):
    locale: Loc = request.state.loc
    uwu_level = request.state.uwu
    auth = request.headers.get("Sonolus-Session")

    parsed = parse_qs(data.values)
    flattened_data = {k: v[0] for k, v in parsed.items()}

    headers = {request.app.auth_header: request.app.auth}
    if auth:
        headers["authorization"] = auth
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=locale.not_logged_in,
        )
    # parse data.values, www-form
    type = flattened_data.get("type")
    if type not in [
        "like",
        "unlike",
        "delete",
        "visibility",
        "staff_pick_add",
        "staff_pick_delete",
        "rerate",
    ]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=locale.not_found
        )
    if type in ["like", "unlike"]:
        async with aiohttp.ClientSession(headers=headers) as cs:
            async with cs.post(
                request.app.api_config["url"]
                + f"/api/charts/{item_name.removeprefix('UnCh-')}/like/",
                json={"type": type},
            ) as req:
                if req.status != 200:
                    raise HTTPException(
                        status_code=req.status, detail=locale.unknown_error
                    )
        resp = {"key": "", "hashes": [], "shouldUpdateItem": True}
    elif type in ["delete"]:
        async with aiohttp.ClientSession(headers=headers) as cs:
            async with cs.delete(
                request.app.api_config["url"]
                + f"/api/charts/{item_name.removeprefix('UnCh-')}/delete/"
            ) as req:
                if req.status != 200:
                    raise HTTPException(
                        status_code=req.status, detail=locale.not_admin_or_owner
                    )
                data = await req.json()
            if data.get("admin") and not data.get("owner"):
                async with cs.post(
                    request.app.api_config["url"] + f"/api/accounts/notifications/",
                    json={
                        "user_id": data["author"],
                        "title": "Chart Deleted",
                        "content": f"#CHART_DELETED\n{data['title']}",
                    },
                ) as req:
                    if req.status != 200:
                        raise HTTPException(
                            status_code=req.status, detail=locale.not_mod
                        )
        resp = {"key": "", "hashes": [], "shouldRemoveItem": True}
    elif type in ["visibility"]:
        async with aiohttp.ClientSession(headers=headers) as cs:
            async with cs.patch(
                request.app.api_config["url"]
                + f"/api/charts/{item_name.removeprefix('UnCh-')}/visibility/",
                json={"status": flattened_data.get("visibility")},
            ) as req:
                if req.status != 200:
                    raise HTTPException(
                        status_code=req.status, detail=locale.not_mod_or_owner
                    )
                data = await req.json()
            if (
                flattened_data["visibility"] != "PUBLIC"
                and data.get("mod")
                and not data.get("owner")
            ):
                async with cs.post(
                    request.app.api_config["url"] + f"/api/accounts/notifications/",
                    json={
                        "user_id": data["author"],
                        "title": "Chart Visibility Update",
                        "content": f"#CHART_VISIBILITY_CHANGED\n{flattened_data['visibility']}\n{data['title']}",
                    },
                ) as req:
                    if req.status != 200:
                        raise HTTPException(
                            status_code=req.status, detail=locale.not_mod
                        )
        resp = {"key": "", "hashes": [], "shouldUpdateItem": True}
    elif type in ["rerate"]:
        constant = flattened_data.get("constant")

        def is_valid_constant(c: str):
            try:
                if not isinstance(c, str):
                    return False
                d = decimal.Decimal(c)
                if not (-1000 < d < 1000):
                    return False
                # precision check: less than 4 digits after decimal (excluding trailing zeros)
                if "." in c:
                    dec_part = c.split(".")[1].rstrip("0")
                    if len(dec_part) >= 4:
                        return False
                return True
            except (decimal.InvalidOperation, ValueError):
                return False

        if not is_valid_constant(constant):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=locale.invalid_constant,
            )
        async with aiohttp.ClientSession(headers=headers) as cs:
            async with cs.patch(
                request.app.api_config["url"]
                + f"/api/charts/{item_name.removeprefix('UnCh-')}/constant_rate/",
                json={
                    "constant": float(
                        decimal.Decimal(constant).quantize(
                            decimal.Decimal("0.0001"),
                            rounding=decimal.ROUND_HALF_UP,
                        )
                    )
                },
            ) as req:
                if req.status != 200:
                    raise HTTPException(
                        status_code=req.status, detail=locale.not_mod_or_owner
                    )
                data = await req.json()
        resp = {"key": "", "hashes": [], "shouldUpdateItem": True}
    elif type in ["staff_pick_add", "staff_pick_delete"]:
        async with aiohttp.ClientSession(headers=headers) as cs:
            async with cs.patch(
                request.app.api_config["url"]
                + f"/api/charts/{item_name.removeprefix('UnCh-')}/stpick/",
                json={"value": True if type == "staff_pick_add" else False},
            ) as req:
                if req.status != 200:
                    raise HTTPException(
                        status_code=req.status, detail=locale.not_mod
                    )
        resp = {"key": "", "hashes": [], "shouldUpdateItem": True}

    return resp
