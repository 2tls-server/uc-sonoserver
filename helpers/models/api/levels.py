from datetime import datetime
from decimal import Decimal
from functools import lru_cache
from typing import Literal, TypeVar
from pydantic import BaseModel, Field

from helpers.data_compilers import *
from helpers.models.sonolus.item import LevelItem


M = TypeVar("M", bound=BaseModel)

class Chart(BaseModel):
    id: str
    rating: int | Decimal
    author: str  # author sonolus id
    title: str
    staff_pick: bool
    artists: str | None = None
    jacket_file_hash: str
    music_file_hash: str
    chart_file_hash: str
    background_v1_file_hash: str
    background_v3_file_hash: str
    tags: list[str] | None = Field(default_factory=list)
    description: str | None = None
    preview_file_hash: str | None = None
    background_file_hash: str | None = None
    status: Literal["UNLISTED", "PRIVATE", "PUBLIC"]
    like_count: int
    comment_count: int
    created_at: datetime
    published_at: datetime | None = None
    updated_at: datetime
    author_full: str | None = None
    chart_design: str
    is_first_publish: bool | None = None  # only returned on update_status
    liked: bool | None = None

    @lru_cache
    @staticmethod
    def _get_cached_particle(self, base_url: str, particle_name: str):
        particles = compile_particles_list(base_url)
        particle_data = next(
            (particle, engine_specific) for (particle, engine_specific) in particles if particle.name == particle_name
        )
        return particle_data
    
    def _get_cached_skin(
        base_url: str, skin_name: str, engine_name: str, localization: str
    ) -> tuple[SkinItem, list[str], str, str | None]:
        skins = compile_skins_list(base_url)

        candidates = [
            (skin, engines, theme, locale)
            for (skin, engines, theme, locale) in skins
            if theme == skin_name and engine_name in engines
        ]

        if not candidates:
            raise KeyError("no matching theme/engine for skin found")

        #  try to match locale
        for (skin, engines, theme, locale) in candidates:
            if locale == localization:
                return skin, engines, theme, locale

        # fallback: find skin where no locale is set (some global skin)
        for (skin, engines, theme, locale) in candidates:
            if locale is None:
                return skin, engines, theme, locale

        # fallback 2: just return first item
        return candidates[0]

    def _get_cached_background(base_url: str, localization: str):
        return compile_backgrounds_list(base_url, localization)[0].model_copy()

    def _get_cached_engine(base_url: str, engine_name: str, locale: str):
        engines = compile_engines_list(base_url, locale)
        engine_data = next(
            engine for engine in engines if engine.name == engine_name
        )
        return engine_data

    def to_level(
        self, 
        request, 
        asset_base_url: str, 
        bgtype: str, 
        include_description=False, 
        disable_replace_missing_preview=False,
        context: Literal["list", "level"] = "list"
    ) -> tuple[LevelItem, str | None]:
        default = bgtype.startswith("default_or_")
        if default:
            bgtype = bgtype.removeprefix("default_or_")
            background_hash = self.background_file_hash
        else:
            background_hash = None

        if not background_hash:
            default = False
            background_hash: str = getattr(self, f"background_{bgtype}_file_hash")

        bg_item = self._get_cached_background(request.app.base_url, request.state.localization)

class GetChartResponse(BaseModel):
    data: Chart
    asset_base_url: str
    mod: bool | None = None
    admin: bool | None = None # TODO: Make optional fields non-optional (backend)
    owner: bool

class DeleteChartResponse(Chart):
    admin: bool | None = None
    owner: bool | None = None

class VisibilityChangeResponse(Chart):
    mod: bool | None = None
    owner: bool | None = None

class LevelList(BaseModel):
    pageCount: int | None = None # TODO: split level lists into different routes (backend)
    data: list[Chart]
    asset_base_url: str