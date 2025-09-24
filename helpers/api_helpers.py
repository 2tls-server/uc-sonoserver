from functools import lru_cache
from helpers.data_compilers import compile_engines_list, compile_backgrounds_list
from locales.locale import Locale
from helpers.owoify import handle_uwu


def api_notif_to_post(
    request,
    i: dict,
    include_description: bool = False,
) -> dict | tuple:
    loc = request.state.loc
    d = {
        "name": f"notification-{i['id']}",
        "source": request.app.base_url,
        "version": 1,
        "title": i["title"],
        "time": i["timestamp"],
        "author": "UntitledCharts",
        "tags": [
            (
                {"title": loc.notification.READ_STATUS, "icon": "envelopeOpen"}
                if i["is_read"]
                else {"title": loc.notification.UNREAD_STATUS, "icon": "envelope"}
            )
        ],
    }
    if include_description:
        content = i["content"]
        content_parts = content.splitlines()
        if content_parts[0].startswith("#"):
            if content_parts[0] == "#CHART_DELETED":
                del content_parts[0]
                content = loc.notification.templates.CHART_DELETED(
                    chart_name="\n".join(content_parts)
                )
            elif content_parts[0] == "#CHART_VISIBILITY_CHANGED":
                del content_parts[0]
                visibility = content_parts.pop(0)
                content = loc.notification.templates.CHART_VISIBILITY_CHANGED(
                    visibility_status=visibility, chart_name="\n".join(content_parts)
                )
            elif content_parts[0] == "#COMMENT_DELETED":
                del content_parts[0]
                content = loc.notification.templates.COMMENT_DELETED(
                    comment_content="\n".join(content_parts)
                )
        return d, content
    return d


def api_level_to_level(
    request,
    asset_base_url: str,
    i: dict,
    bgtype: str,
    include_description: bool = False,
    disable_replace_missing_preview: bool = False,
) -> dict | tuple:
    loc = request.state.loc

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
                },
                {
                    "title": str(i["comment_count"]),
                    "icon": "comment",
                },
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
    elif not disable_replace_missing_preview:
        leveldata["preview"] = {
            "hash": i["music_file_hash"],
            "url": make_url(i["music_file_hash"]),
        }

    if i["staff_pick"]:
        leveldata["tags"].insert(
            0,
            {
                "title": loc.staff_pick,
                "icon": "trophy",
            },
        )

    if not include_description:
        return leveldata
    else:
        desc = i.get("description")
        if desc:
            desc = handle_uwu(desc, request.state.uwu)
        return leveldata, desc
