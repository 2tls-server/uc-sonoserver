from helpers.data_compilers import compile_engines_list


def api_level_to_level(request, asset_base_url: str, i: dict) -> dict:
    leveldata = {
        "name": f"UnCh-{i['id']}",
        "source": request.app.base_url,
        "version": 1,
        "rating": i["rating"],
        "artists": i["artists"],
        "author": i["author_full"],
        "title": i["title"],
        "tags": [
            {
                "title": str(i["like_count"]),
                "icon": "heart" if i.get("liked") else "heartHollow",
            }
        ]
        + [{"title": tag, "icon": "tag"} for tag in i["tags"]],
        "engine": compile_engines_list(request.app.base_url)[0],
        "useSkin": {"useDefault": True},
        "useEffect": {"useDefault": True},
        "useParticle": {"useDefault": True},
        "useBackground": {"useDefault": True},  # XXX
        "cover": {
            "hash": i["jacket_file_hash"],
            "url": "/".join(
                [
                    asset_base_url,
                    i["author"],
                    i["id"],
                    i["jacket_file_hash"],
                ]
            ),
        },
        "data": {
            "hash": i["chart_file_hash"],
            "url": "/".join(
                [
                    asset_base_url,
                    i["author"],
                    i["id"],
                    i["chart_file_hash"],
                ]
            ),
        },
        "bgm": {
            "hash": i["music_file_hash"],
            "url": "/".join(
                [
                    asset_base_url,
                    i["author"],
                    i["id"],
                    i["music_file_hash"],
                ]
            ),
        },
    }
    if i["preview_file_hash"]:
        leveldata["preview"] = {
            "hash": i["preview_file_hash"],
            "url": "/".join(
                [
                    asset_base_url,
                    i["author"],
                    i["id"],
                    i["preview_file_hash"],
                ]
            ),
        }
    return leveldata
