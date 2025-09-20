from functools import lru_cache
from helpers.data_compilers import compile_engines_list, compile_backgrounds_list
from locales.locale import Locale
from helpers.owoify import handle_uwu


def api_level_to_level(
    request,
    asset_base_url: str,
    i: dict,
    bgtype: str,
    include_description: bool = False,
) -> dict | tuple:
    loc = Locale.get_messages(request.state.localization)

    @lru_cache(maxsize=None)
    def get_cached_background(base_url, localization):
        return compile_backgrounds_list(base_url, localization)[0].copy()

    @lru_cache(maxsize=None)
    def get_cached_engine(base_url, localization):
        return compile_engines_list(base_url, localization)[0]

    author = i["author"]
    level_id = i["id"]

    def make_url(file_hash: str) -> str:
        return "/".join([asset_base_url, author, level_id, file_hash])

    default = bgtype.startswith("default_or_")
    if default:
        bgtype = bgtype.removeprefix("default_or_")
        background_hash = i.get("background_file_hash")
    else:
        background_hash = None

    if not background_hash:
        default = False
        background_hash = i[f"background_{bgtype}_file_hash"]

    bg_item = get_cached_background(request.app.base_url, request.state.localization)
    bg_item["image"] = {"hash": background_hash, "url": make_url(background_hash)}
    bg_item["thumbnail"] = {
        "hash": i["jacket_file_hash"],
        "url": make_url(i["jacket_file_hash"]),
    }
    bg_item["name"] = "configured"
    if not default and bgtype == "v3":
        title = loc.background.V3
    elif not default and bgtype == "v1":
        title = loc.background.V1
    else:
        title = loc.background.UPLOADED
    bg_item["title"] = handle_uwu(title, request.state.uwu)

    leveldata = {
        "name": f"UnCh-{level_id}",
        "source": request.app.base_url,
        "version": 1,
        "rating": i["rating"],
        "artists": handle_uwu(i["artists"], request.state.uwu),
        "author": i["author_full"],
        "title": handle_uwu(i["title"], request.state.uwu),
        "tags": (
            [
                {
                    "title": str(i["like_count"]),
                    "icon": "heart" if i.get("liked") else "heartHollow",
                }
            ]
            + [
                {"title": handle_uwu(tag, request.state.uwu), "icon": "tag"}
                for tag in i["tags"]
            ]
        ),
        "engine": get_cached_engine(request.app.base_url, request.state.localization),
        "useSkin": {"useDefault": True},
        "useEffect": {"useDefault": True},
        "useParticle": {"useDefault": True},
        "useBackground": {"useDefault": False, "item": bg_item},
        "cover": {
            "hash": i["jacket_file_hash"],
            "url": make_url(i["jacket_file_hash"]),
        },
        "data": {"hash": i["chart_file_hash"], "url": make_url(i["chart_file_hash"])},
        "bgm": {"hash": i["music_file_hash"], "url": make_url(i["music_file_hash"])},
    }

    if i.get("preview_file_hash"):
        leveldata["preview"] = {
            "hash": i["preview_file_hash"],
            "url": make_url(i["preview_file_hash"]),
        }

    if not include_description:
        return leveldata
    else:
        desc = i.get("description")
        if desc:
            desc = handle_uwu(desc, request.state.uwu)
        return leveldata, desc
