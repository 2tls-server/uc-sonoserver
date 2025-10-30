import json, os

from helpers.models.sonolus.item import (
    EngineItem, 
    SkinItem, 
    BackgroundItem, 
    EffectItem, 
    ParticleItem, 
    PostItem, 
    PlaylistItem
)
from helpers.models.sonolus.misc import SRL

from helpers.repository_map import repo

from locales.locale import Loc, Locale

cached = {
    "skins": None,
    "effects": None,
    "particles": None,
    "banner": None,
    "static_posts": None,
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


def compile_banner() -> SRL | None:
    if cached["banner"]:
        return cached["banner"]
    path = "files/banner/banner.png"
    if os.path.exists(path):
        hash = repo.add_file(path)
        return repo.get_srl(hash)
    return None

def compile_playlists_list(
    source: str | None = None, locale: str = "en"
) -> list[PlaylistItem]:
    def replace_values(k_value):
        return (
            k_value.replace("#YOU", loc.you)
                .replace("#UPLOADEDSUB", loc.playlist.UPLOADEDSUB)
                .replace("#UPLOADED", loc.playlist.UPLOADED)
        )
    
    loc, locale = Locale.get_messages(locale)
    if cached.get(f"playlists_{locale}"):
        return cached[f"playlists_{locale}"]
    compiled_data_list = []
    for playlist in os.listdir("files/playlists"):
        if not os.path.isdir(os.path.join("files", "playlists", playlist)):
            continue

        with open(
            f"files/playlists/{playlist}/playlist.json", "r", encoding="utf8"
        ) as f:
            post_data: dict = json.load(f)
        if not post_data.get("enabled", True):
            continue

        compiled_data = PlaylistItem(
            name=playlist,
            source=source,
            version=post_data["version"],
            title=replace_values(post_data["title"]),
            subtitle=replace_values(post_data["subtitle"]),
            author=replace_values(post_data["author"])
        )

        data_files = {"thumbnail": "thumbnail.png"}
        for key, file in data_files.items():
            hash = repo.add_file(
                f"files/playlists/{playlist}/{file}", error_on_file_nonexistent=False
            )
            if hash:
                compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    cached[f"playlists_{locale}"] = compiled_data_list
    return compiled_data_list


def compile_static_posts_list(source: str = None) -> list[PostItem]:
    if cached["static_posts"]:
        return cached["static_posts"]
    
    compiled_data_list = []
    for post in os.listdir("files/posts"):
        if not os.path.isdir(os.path.join("files", "posts", post)):
            continue

        with open(f"files/posts/{post}/post.json", "r", encoding="utf8") as f:
            post_data: dict = json.load(f)
        if not post_data.get("enabled", True):
            continue

        thumbnail: SRL | None = None
        hash = repo.add_file(
            f"files/posts/{post}/thumbnail.png", error_on_file_nonexistent=False
        )
        if hash:
            thumbnail = repo.get_srl(hash)

        compiled_data = PostItem(
            name=post,
            source=source,
            version=post_data["version"],
            title=post_data["title"],
            time=post_data["time"],
            author=post_data["author"],
            tags=[],
            thumbnail=thumbnail
        )
        compiled_data_list.append(compiled_data)

    cached["static_posts"] = compiled_data_list
    return compiled_data_list


def sort_posts_by_newest(posts: list[PostItem]) -> list[PostItem]:
    return sorted(posts, key=lambda post: post.time, reverse=True)


def compile_effects_list(source: str = None) -> list[EffectItem]:
    if cached["effects"]:
        return cached["effects"]
    compiled_data_list = []
    for effect in os.listdir("files/effects"):
        if not os.path.isdir(os.path.join("files", "effects", effect)):
            continue

        with open(f"files/effects/{effect}/effect.json", "r", encoding="utf8") as f:
            effect_data: dict = json.load(f)
        if not effect_data.get("enabled", True):
            continue

        compiled_data = EffectItem(
            name=effect,
            source=source,
            version=effect_data["version"],
            title=effect_data["title"],
            subtitle=effect_data["subtitle"],
            author=effect_data["author"],
            tags=[],
            thumbnail=repo.get_srl(repo.add_file(f"files/effects/{effect}/thumbnail.png")),
            data=repo.get_srl(repo.add_file(f"files/effects/{effect}/data")),
            audio=repo.get_srl(repo.add_file(f"files/effects/{effect}/audio"))
        )
        compiled_data_list.append(compiled_data)
    cached["effects"] = compiled_data_list
    return compiled_data_list


def compile_backgrounds_list(
    source: str = None,
    locale: str = "en",
) -> list[BackgroundItem]:
    def replace_values(d_value: str):
        return (
            d_value.replace("#BACKGROUNDSELECTSUB", loc.background.BACKGROUNDSELECTSUB)
            .replace("#BACKGROUNDSELECT", loc.background.BACKGROUNDSELECT)
        )

    loc, locale = Locale.get_messages(locale)
    if cached.get(f"backgrounds_{locale}"):
        return cached[f"backgrounds_{locale}"]
    compiled_data_list = []
    for background in os.listdir("files/backgrounds"):
        if not os.path.isdir(os.path.join("files", "backgrounds", background)):
            continue
        compiled_data: BackgroundItem = {"tags": []}
        compiled_data["name"] = background
        if source:
            compiled_data["source"] = source
        with open(
            f"files/backgrounds/{background}/background.json", "r", encoding="utf8"
        ) as f:
            background_data: dict = json.load(f)
        if not background_data.get("enabled", True):
            continue

        compiled_data = BackgroundItem(
            name=background,
            source=source,
            version=background_data["version"],
            title=replace_values(background_data["title"]),
            subtitle=replace_values(background_data["subtitle"]),
            author=replace_values(background_data["author"]),
            tags=[],
            thumbnail=repo.get_srl(repo.add_file(f"files/backgrounds/{background}/thumbnail.png")), # TODO shorten with subrepos for relative paths and srl_from_file
            data=repo.get_srl(repo.add_file(f"files/backgrounds/{background}/data")),
            image=repo.get_srl(repo.add_file(f"files/backgrounds/{background}/image.png")),
            configuration=repo.get_srl(repo.add_file(f"files/backgrounds/{background}/configuration.json.gz"))
        )

        compiled_data_list.append(compiled_data)
    cached[f"backgrounds_{locale}"] = compiled_data_list
    return compiled_data_list


def compile_particles_list(source: str = None) -> list[tuple[ParticleItem, bool]]:
    if cached["particles"]:
        return cached["particles"]
    compiled_data_list = []
    for particle in os.listdir("files/particles"):
        if not os.path.isdir(os.path.join("files", "particles", particle)):
            continue

        with open(
            f"files/particles/{particle}/particle.json", "r", encoding="utf8"
        ) as f:
            particle_data: dict = json.load(f)
        if not particle_data.get("enabled", True):
            continue

        compiled_data = ParticleItem(
            name=particle,
            source=source,
            version=particle_data["version"],
            title=particle_data["title"],
            subtitle=particle_data["subtitle"],
            author=particle_data["author"],
            tags=[],
            thumbnail=repo.get_srl(repo.add_file(f"files/particles/{particle}/thumbnail.png")),
            data=repo.get_srl(repo.add_file(f"files/particles/{particle}/data")),
            texture=repo.get_srl(repo.add_file(f"files/particles/{particle}/texture"))
        )

        compiled_data_list.append((compiled_data, particle_data["engine_specific"]))
    cached["particles"] = compiled_data_list
    return compiled_data_list


def compile_skins_list(source: str = None) -> list[tuple[SkinItem, list[str], str, str | None]]: # "engines", "theme", "locale"... probably a TODO
    if cached["skins"]:
        return cached["skins"]
    compiled_data_list = []
    for skin in os.listdir("files/skins"):
        if not os.path.isdir(os.path.join("files", "skins", skin)):
            continue

        if source:
            compiled_data["source"] = source
        with open(f"files/skins/{skin}/skin.json", "r", encoding="utf8") as f:
            skin_data: dict = json.load(f)
        if not skin_data.get("enabled", True):
            continue

        compiled_data = SkinItem(
            name=skin,
            source=source,
            version=skin_data["version"],
            title=skin_data["title"],
            subtitle=skin_data["subtitle"],
            author=skin_data["author"],
            tags=[],
            thumbnail=repo.get_srl(repo.add_file(f"files/skins/{skin}/thumbnail.png")),
            data=repo.get_srl(repo.add_file(f"files/skins/{skin}/data")),
            texture=repo.get_srl(repo.add_file(f"files/skins/{skin}/texture"))
        )
        compiled_data_list.append((compiled_data, skin_data["engines"], skin_data["theme"], skin_data.get("locale")))
    cached["skins"] = compiled_data_list
    return compiled_data_list


def compile_engines_list(source: str = None, locale: str = "en") -> list[EngineItem]:
    if cached.get(f"engines_{locale}"):
        return cached[f"engines_{locale}"]
    compiled_data_list: list[tuple[EngineItem, int | float]] = []
    for engine in os.listdir("files/engines"):
        if not os.path.isdir(os.path.join("files", "engines", engine)):
            continue

        with open(f"files/engines/{engine}/engine.json", "r", encoding="utf8") as f:
            engine_data: dict = json.load(f)
        if not engine_data.get("enabled", True):
            continue

        def get_skin_name(engine_data: dict, locale: str) -> str:
            if engine_data.get("skin_name_locale", {}).get(locale):
                return engine_data["skin_name_locale"][locale]
            return engine_data["skin_name"]

        try:
            skins = compile_skins_list(source)
            skin_data = next(
                skin
                for (skin, _, _) in skins
                if skin.name == get_skin_name(engine_data, locale)
            )
            effects = compile_effects_list(source)
            effect_data = next(
                effect
                for effect in effects
                if effect.name == engine_data["effect_name"]
            )
            particles = compile_particles_list(source)
            particle_data = next(
                particle
                for (particle, _) in particles
                if particle.name == engine_data["particle_name"]
            )
            backgrounds = compile_backgrounds_list(source, locale)
            background_data = next(
                background
                for background in backgrounds
                if background.name == engine_data["background_name"]
            )
        except StopIteration:
            raise KeyError(
                "StopIteration raised: incorrect key name! Make sure your engine file names and resource file names match."
            )
        
        compiled_data = (
            EngineItem(
                name=engine,
                version=engine_data.get("key"),
                title=engine_data.get("title"),
                subtitle=engine_data.get("subtitle"),
                source=source,
                author=engine_data.get("author"),
                tags=[],
                description=engine_data.get("description"),
                skin=skin_data,
                background=background_data,
                effect=effect_data,
                particle=particle_data,
                thumbnail=repo.get_srl(repo.add_file(f"files/engines/{engine}/thumbnail.png")),
                playData=repo.get_srl(repo.add_file(f"files/engines/{engine}/EnginePlayData")),
                watchData=repo.get_srl(repo.add_file(f"files/engines/{engine}/EngineWatchData")),
                previewData=repo.get_srl(repo.add_file(f"files/engines/{engine}/EnginePreviewData")),
                tutorialData=repo.get_srl(repo.add_file(f"files/engines/{engine}/EngineTutorialData")),
                rom=repo.get_srl(repo.add_file(f"files/engines/{engine}/EngineRom", error_on_file_nonexistent=False)),
                configuration=repo.get_srl(repo.add_file(f"files/engines/{engine}/EngineConfiguration"))
            ), 
            engine_data.get("engine_sort_order", float("inf")) # last, if no sort order
        )

        compiled_data_list.append(compiled_data)
    compiled_data_list = sorted(
        compiled_data_list,
        key=lambda item: (
            item[1],  # engine_sort_order
            item[0].title.lower(),  # abc
        ),
    )
    cached[f"engines_{locale}"] = compiled_data_list
    return compiled_data_list
