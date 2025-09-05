import json, os
from zipfile import ZipFile
from io import BytesIO

from typing import Optional, List
from helpers.datastructs import (
    EngineItem,
    SRL,
    SkinItem,
    BackgroundItem,
    EffectItem,
    ParticleItem,
    PostItem,
    LevelItem,
)

from helpers.repository_map import repo
from helpers.thumbnail import create_square_thumbnail

import pjsk_background_gen_PIL as pjsk_bg
from PIL import Image

cached = {
    "engines": None,
    "skins": None,
    "effects": None,
    "particles": None,
    "backgrounds": None,
    "banner": None,
    "static_posts": None,
    "static_levels": None,
}


def clear_compile_cache(specific: str = None):
    global cached
    if specific:
        cached[specific] = None
    else:
        new_cached = {}
        for k in cached.keys():
            new_cached[k] = None
        cached = new_cached.copy()


def compile_banner() -> Optional[SRL]:
    if cached["banner"]:
        return cached["banner"]
    path = "files/banner/banner.png"
    if os.path.exists(path):
        hash = repo.add_file(path)
        return repo.get_srl(hash)
    return None


def compile_static_posts_list(source: str = None) -> List[PostItem]:
    if cached["static_posts"]:
        return cached["static_posts"]
    with open("files/posts/posts.json", "r", encoding="utf8") as f:
        posts = json.load(f)
    compiled_data_list = []
    for post in posts:
        compiled_data: PostItem = {"tags": []}
        compiled_data["name"] = post
        if source:
            compiled_data["source"] = source
        with open(f"files/posts/{post}/post.json", "r", encoding="utf8") as f:
            post_data: dict = json.load(f)
        item_keys = ["version", "title", "time", "author", "description"]
        for key in item_keys:
            compiled_data[key] = post_data[key]
        data_files = {"thumbnail": "thumbnail.png"}
        for key, file in data_files.items():
            hash = repo.add_file(
                f"files/posts/{post}/{file}", error_on_file_nonexistent=False
            )
            if hash:
                compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    cached["static_posts"] = compiled_data_list
    return compiled_data_list


def sort_posts_by_newest(posts: List[PostItem]) -> List[PostItem]:
    return sorted(posts, key=lambda post: post["time"], reverse=True)


def compile_static_levels_list(source: str = None) -> List[LevelItem]:
    if cached["static_levels"]:
        return cached["static_levels"]
    compiled_data_list = []

    levels_root = "levels"
    engines = compile_engines_list(source)
    for engine_name in os.listdir(levels_root):
        engine_path = os.path.join(levels_root, engine_name)
        if not os.path.isdir(engine_path):
            continue
        engine_data: Optional[EngineItem] = next(
            (engine for engine in engines if engine["name"] == engine_name), None
        )
        if not engine_data:
            continue
        for level_file in os.listdir(engine_path):
            try:
                invalid_chart_flag = False
                if not level_file.endswith(".zip"):
                    continue
                level_path = os.path.join(engine_path, level_file)
                levelname = os.path.splitext(level_file)[0]
                # iterate all files, {levelname}.zip
                compiled_data: LevelItem = {
                    "name": levelname,
                    "tags": [{"title": f"Engine: {engine_name}", "icon": engine_name}],
                    "useSkin": {"useDefault": True},
                    "useEffect": {"useDefault": True},
                    "useParticle": {"useDefault": True},
                    "useBackground": {"useDefault": True},
                }
                if source:
                    compiled_data["source"] = source
                with ZipFile(level_path, "r") as zip_file:
                    with zip_file.open("level.json") as f:
                        level_data = json.load(f)
                    item_keys = [
                        "version",
                        "title",
                        "rating",
                        "author",
                        "artists",
                        "description",
                    ]
                    for key in item_keys:
                        compiled_data[key] = level_data[key]
                    data_files = {
                        "jacket": "jacket.png",
                        "data": "level.data",
                        "bgm": "music.mp3",
                        "preview": "music_pre.mp3",
                    }
                    for key, filename in data_files.items():
                        if filename in zip_file.namelist():
                            hash = repo.add_file(f"{level_path}|{filename}")
                            if hash:
                                compiled_data[key] = repo.get_srl(hash)
                        else:
                            if key == "preview":
                                pass
                            else:
                                invalid_chart_flag = True
                                break
                    if invalid_chart_flag:
                        continue
                    if "stage.png" in zip_file.namelist():
                        hash = repo.add_file(f"{level_path}|stage.png")
                        image = repo.get_srl(hash)
                        if "stage_thumbnail.png" not in zip_file.namelist():
                            bg = Image.open(zip_file.read("stage.png"))
                            tn = create_square_thumbnail(bg)
                            buf = BytesIO()
                            tn.save(buf, format="PNG")
                            tn_bytes = buf.getvalue()
                            zip_file.writestr("stage_thumbnail.png", tn_bytes)
                        hash2 = repo.add_file(f"{level_path}|stage_thumbnail.png")
                        thumbnail = repo.get_srl(hash2)
                        compiled_data["useBackground"]["useDefault"] = False
                        stage_item: BackgroundItem = {
                            "name": f"bg-{levelname}-v3",
                            "version": 2,
                            "tags": [],
                            "title": level_data["title"],
                            "subtitle": "UntitledCharts Background",
                            "author": "YumYummity",
                            "thumbnail": thumbnail,
                            "data": engine_data["background"]["data"],
                            "image": image,
                            "configuration": engine_data["background"]["configuration"],
                        }
                        compiled_data["useBackground"]["item"] = stage_item
            except Exception as e:
                raise e
                continue
            compiled_data_list.append(compiled_data)
    cached["static_levels"] = compiled_data_list
    return compiled_data_list


def compile_effects_list(source: str = None) -> List[EffectItem]:
    if cached["effects"]:
        return cached["effects"]
    with open("files/effects/effects.json", "r", encoding="utf8") as f:
        effects = json.load(f)
    compiled_data_list = []
    for effect in effects:
        compiled_data: EffectItem = {"tags": []}
        compiled_data["name"] = effect
        if source:
            compiled_data["source"] = source
        with open(f"files/effects/{effect}/effect.json", "r", encoding="utf8") as f:
            effect_data: dict = json.load(f)
        item_keys = ["version", "title", "subtitle", "author"]
        for key in item_keys:
            compiled_data[key] = effect_data[key]
        data_files = {"thumbnail": "thumbnail.png", "data": "data", "audio": "audio"}
        for key, file in data_files.items():
            hash = repo.add_file(f"files/effects/{effect}/{file}")
            compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    cached["effects"] = compiled_data_list
    return compiled_data_list


def compile_backgrounds_list(source: str = None) -> List[BackgroundItem]:
    if cached["backgrounds"]:
        return cached["backgrounds"]
    with open("files/backgrounds/backgrounds.json", "r", encoding="utf8") as f:
        backgrounds = json.load(f)
    compiled_data_list = []
    for background in backgrounds:
        compiled_data: BackgroundItem = {"tags": []}
        compiled_data["name"] = background
        if source:
            compiled_data["source"] = source
        with open(
            f"files/backgrounds/{background}/background.json", "r", encoding="utf8"
        ) as f:
            background_data: dict = json.load(f)
        item_keys = ["version", "title", "subtitle", "author"]
        for key in item_keys:
            compiled_data[key] = background_data[key]
        data_files = {
            "thumbnail": "thumbnail.png",
            "data": "data",
            "image": "image.png",
            "configuration": "configuration.json.gz",
        }
        for key, file in data_files.items():
            hash = repo.add_file(f"files/backgrounds/{background}/{file}")
            compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    cached["backgrounds"] = compiled_data_list
    return compiled_data_list


def compile_particles_list(source: str = None) -> List[ParticleItem]:
    if cached["particles"]:
        return cached["particles"]
    with open("files/particles/particles.json", "r", encoding="utf8") as f:
        particles = json.load(f)
    compiled_data_list = []
    for particle in particles:
        compiled_data: ParticleItem = {"tags": []}
        compiled_data["name"] = particle
        if source:
            compiled_data["source"] = source
        with open(
            f"files/particles/{particle}/particle.json", "r", encoding="utf8"
        ) as f:
            particle_data: dict = json.load(f)
        item_keys = ["version", "title", "subtitle", "author"]
        for key in item_keys:
            compiled_data[key] = particle_data[key]
        data_files = {
            "thumbnail": "thumbnail.png",
            "data": "data",
            "texture": "texture",
        }
        for key, file in data_files.items():
            hash = repo.add_file(f"files/particles/{particle}/{file}")
            compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    cached["particles"] = compiled_data_list
    return compiled_data_list


def compile_skins_list(source: str = None) -> List[SkinItem]:
    if cached["skins"]:
        return cached["skins"]
    with open("files/skins/skins.json", "r", encoding="utf8") as f:
        skins = json.load(f)
    compiled_data_list = []
    for skin in skins:
        compiled_data: SkinItem = {"tags": []}
        compiled_data["name"] = skin
        if source:
            compiled_data["source"] = source
        with open(f"files/skins/{skin}/skin.json", "r", encoding="utf8") as f:
            skin_data: dict = json.load(f)
        item_keys = ["version", "title", "subtitle", "author"]
        for key in item_keys:
            compiled_data[key] = skin_data[key]
        data_files = {
            "thumbnail": "thumbnail.png",
            "data": "data",
            "texture": "texture",
        }
        for key, file in data_files.items():
            hash = repo.add_file(f"files/skins/{skin}/{file}")
            compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    cached["skins"] = compiled_data_list
    return compiled_data_list


def compile_engines_list(source: str = None) -> List[EngineItem]:
    if cached["engines"]:
        return cached["engines"]
    with open("files/engines/engines.json", "r", encoding="utf8") as f:
        engines = json.load(f)
    compiled_data_list = []
    for engine in engines:
        compiled_data: EngineItem = {
            "tags": [],
            "actions": [],
            "hasCommunity": False,
            "leaderboards": [],
            "sections": [],
        }
        with open(f"files/engines/{engine}/engine.json", "r", encoding="utf8") as f:
            engine_data: dict = json.load(f)
        if engine_data.get("description"):
            compiled_data["description"] = engine_data["description"]
        compiled_data["name"] = engine
        if source:
            compiled_data["source"] = source
        item_keys = ["version", "title", "subtitle", "author"]
        for key in item_keys:
            compiled_data[key] = engine_data[key]
        data_files = {
            "thumbnail": "thumbnail.png",
            "configuration": "configuration.json.gz",
            "playData": "playData",
            "watchData": "watchData",
            "previewData": "previewData",
            "tutorialData": "tutorialData",
        }
        for key, file in data_files.items():
            hash = repo.add_file(f"files/engines/{engine}/{file}")
            compiled_data[key] = repo.get_srl(hash)
        skins = compile_skins_list(source)
        skin_data = next(
            skin for skin in skins if skin["name"] == engine_data["skin_name"]
        )
        compiled_data["skin"] = skin_data
        effects = compile_effects_list(source)
        effect_data = next(
            effect for effect in effects if effect["name"] == engine_data["effect_name"]
        )
        compiled_data["effect"] = effect_data
        particles = compile_particles_list(source)
        particle_data = next(
            particle
            for particle in particles
            if particle["name"] == engine_data["particle_name"]
        )
        compiled_data["particle"] = particle_data
        backgrounds = compile_backgrounds_list(source)
        background_data = next(
            background
            for background in backgrounds
            if background["name"] == engine_data["background_name"]
        )
        compiled_data["background"] = background_data
        compiled_data_list.append(compiled_data)
    cached["engines"] = compiled_data_list
    return compiled_data_list
