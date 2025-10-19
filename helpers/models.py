from pydantic import BaseModel, Field
from typing import TypeVar, Literal, Annotated
from datetime import datetime
from decimal import Decimal

from helpers.sonolus_typings import Grade, ServerInfoButtonType, Text, Icon, ItemType


class ServiceUserProfile(BaseModel):
    id: str  # ServiceUserId... is just a string.
    handle: str
    name: str
    avatarType: str
    avatarForegroundType: str
    avatarForegroundColor: str
    avatarBackgroundType: str
    avatarBackgroundColor: str
    bannerType: str
    aboutMe: str
    favorites: list[str]


class ServerAuthenticateRequest(BaseModel):
    type: str
    address: str
    time: int
    userProfile: ServiceUserProfile


class ServerAuthenticateExternalRequest(BaseModel):
    type: str
    url: str
    time: int
    userProfile: ServiceUserProfile


class ServiceUserProfileWithType(ServiceUserProfile):
    type: Literal["game", "external"]

T = TypeVar("T")


class Tag(BaseModel):
    title: str
    icon: str | None = None


class SRL(BaseModel):
    hash: str
    url: str


class SIL(BaseModel):
    address: str
    name: str


# region Items


class BackgroundItem(BaseModel):
    name: str
    source: str | None = None
    version: int
    title: str
    subtitle: str
    author: str
    tags: list[Tag]
    thumbnail: SRL
    data: SRL
    image: SRL
    configuration: SRL


class ParticleItem(BaseModel):
    name: str
    source: str | None = None
    version: int
    title: str
    subtitle: str
    author: str
    tags: list[Tag]
    thumbnail: SRL
    data: SRL
    texture: SRL


class EffectItem(BaseModel):
    name: str
    source: str | None = None
    version: int
    title: str
    subtitle: str
    author: str
    tags: list[Tag]
    thumbnail: SRL
    data: SRL
    audio: SRL


class SkinItem(BaseModel):
    name: str
    source: str | None = None
    version: int
    title: str
    subtitle: str
    author: str
    tags: list[Tag]
    thumbnail: SRL
    data: SRL
    texture: SRL


class EngineItem(BaseModel):
    name: str
    version: int
    title: str
    subtitle: str
    source: str | None = None
    author: str
    tags: list[Tag]
    description: str | None = None

    skin: SkinItem
    background: BackgroundItem
    effect: EffectItem
    particle: ParticleItem

    thumbnail: SRL
    playData: SRL
    watchData: SRL
    previewData: SRL
    tutorialData: SRL
    rom: SRL | None = None
    configuration: SRL


class PostItem(BaseModel):
    name: str
    source: str | None = None
    version: int
    title: str
    time: int
    author: str
    tags: list[Tag]
    thumbnail: SRL | None = None


class UseItem(BaseModel):
    useDefault: bool
    item: SkinItem | BackgroundItem | EffectItem | ParticleItem | None = None


class LevelItem(BaseModel):
    name: str
    source: str | None = None
    version: int
    rating: int
    title: str
    artists: str
    author: str
    tags: list[Tag] = None
    engine: EngineItem
    useSkin: UseItem[SkinItem]
    useBackground: UseItem[BackgroundItem]
    useEffect: UseItem[EffectItem]
    useParticle: UseItem[ParticleItem]
    cover: SRL
    bgm: SRL
    preview: SRL | None = None
    data: SRL


class PlaylistItem(BaseModel):
    name: str
    source: str | None = None
    version: int
    title: str
    subtitle: str
    author: str
    tags: list[Tag]
    levels: list[LevelItem]
    thumbnail: SRL | None = None


class RoomItem(BaseModel):
    name: str
    title: str
    subtitle: str
    master: str
    tags: list[Tag]
    cover: SRL | None = None
    bgm: SRL | None = None
    preview: SRL | None = None


class ReplayItem(BaseModel):
    name: str
    source: str | None = None
    version: int
    title: str
    subtitle: str
    author: str
    tags: list[Tag]
    level: LevelItem
    data: SRL
    configuration: SRL


ServerItem = (
    PostItem
    | RoomItem
    | SkinItem
    | BackgroundItem
    | ParticleItem
    | EffectItem
    | RoomItem
    | PlaylistItem
    | ReplayItem
    | LevelItem
    | EngineItem
)


def get_item_type(type: ItemType) -> ServerItem:
    if type == "posts":
        return PostItem()
    elif type == "playlists":
        return PlaylistItem()
    elif type == "levels":
        return LevelItem()
    elif type == "skins":
        return SkinItem()
    elif type == "backgrounds":
        return BackgroundItem()
    elif type == "effects":
        return EffectItem()
    elif type == "particles":
        return ParticleItem()
    elif type == "engines":
        return EngineItem()
    elif type == "replays":
        return ReplayItem()
    elif type == "rooms":
        return RoomItem()
    else:
        raise ValueError(f"Unknown item type: {type}")


# endregion

# region Server


class ServerInfoButton(BaseModel):
    type: ServerInfoButtonType


class ServerCollectionItemOption(BaseModel):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["collectionItem"] = "collectionItem"
    itemType: ItemType

class DumpDefAliasMixin(BaseModel):
    def model_dump(self, **kwargs):
        kwargs.setdefault("by_alias", True)
        return super().model_dump(**kwargs)

class ServerTextOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["text"] = "text"
    default: str = Field(validation_alias="def", serialization_alias="def")
    placeholder: Text | str
    limit: int
    shortcuts: list[str]

class ServerTextAreaOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["textArea"] = "textArea"
    default: str = Field(validation_alias="def", serialization_alias="def")
    placeholder: Text | str
    limit: int
    shortcuts: list[str]

class ServerSliderOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["slider"] = "slider"
    default: int | float = Field(validation_alias="def", serialization_alias="def")
    min: int | float
    max: int | float
    step: int | float
    unit: Text | str | None = None

class ServerToggleOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["toggle"] = "toggle"
    default: bool = Field(validation_alias="def", serialization_alias="def")

class ServerOption_Value(BaseModel):
    name: str
    title: Text | str

class ServerSelectOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["select"] = "select"
    default: str = Field(validation_alias="def", serialization_alias="def")
    values: list[ServerOption_Value]

class ServerMultiOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["multi"] = "multi"
    default: list[bool] = Field(validation_alias="def", serialization_alias="def")
    values: list[ServerOption_Value]

class ServerServerItemOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["serverItem"] = "serverItem"
    itemType: ItemType
    default: SIL | None = Field(None, validation_alias="def", serialization_alias="def")
    allowOtherServers: bool

class ServerServerItemsOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["serverItems"] = "serverItems"
    itemType: ItemType
    default: list[SIL] = Field(validation_alias="def", serialization_alias="def")
    allowOtherServers: bool
    limit: int

class ServerCollectionItemOption(BaseModel):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["collectionItem"] = "collectionItem"
    itemType: ItemType

class ServerFileOption(DumpDefAliasMixin):
    query: str
    name: Text | str
    description: str | None = None
    required: bool
    type: Literal["file"] = "file"
    default: str = Field(validation_alias="def", serialization_alias="def")

ServerOption = (
    ServerTextOption
    | ServerTextAreaOption
    | ServerSliderOption
    | ServerToggleOption
    | ServerSelectOption
    | ServerMultiOption
    | ServerServerItemOption
    | ServerServerItemsOption
    | ServerCollectionItemOption
    | ServerFileOption
)


class ServerForm(BaseModel):
    type: str
    title: Text | str
    icon: Icon | str | None = None
    description: str | None = None
    help: str | None = None
    requireConfirmation: bool
    options: list[Annotated[ServerOption, Field(discriminator="type")]]


class ServerMessage(BaseModel):
    message: str


class ServerItemSectionTyped(BaseModel):
    title: str | Text
    icon: Icon | str | None = None
    description: str | None = None
    help: str | None = None
    itemType: ItemType
    search: ServerForm | None = None
    searchValues: str | None = None

class GenericItemSection(ServerItemSectionTyped):
    itemType: str
    items: list[ServerItem]

class PostItemSection(ServerItemSectionTyped):
    itemType: Literal["post"] = "post"
    items: list[PostItem]


class PlaylistItemSection(ServerItemSectionTyped):
    itemType: Literal["playlist"] = "playlist"
    items: list[PlaylistItem]


class LevelItemSection(ServerItemSectionTyped):
    itemType: Literal["level"] = "level"
    items: list[LevelItem]


class SkinItemSection(ServerItemSectionTyped):
    itemType: Literal["skin"] = "skin"
    items: list[SkinItem]


class BackgroundItemSection(ServerItemSectionTyped):
    itemType: Literal["background"] = "background"
    items: list[BackgroundItem]


class EffectItemSection(ServerItemSectionTyped):
    itemType: Literal["effect"] = "effect"
    items: list[EffectItem]


class ParticleItemSection(ServerItemSectionTyped):
    itemType: Literal["particle"] = "particle"
    items: list[ParticleItem]


class EngineItemSection(ServerItemSectionTyped):
    itemType: Literal["engine"] = "engine"
    items: list[EngineItem]


class ReplayItemSection(ServerItemSectionTyped):
    itemType: Literal["replay"] = "replay"
    items: list[ReplayItem]


class RoomItemSection(ServerItemSectionTyped):
    itemType: Literal["room"] = "room"
    items: list[RoomItem]


ServerItemSection = (
    PostItemSection
    | PlaylistItemSection
    | LevelItemSection
    | SkinItemSection
    | BackgroundItemSection
    | EffectItemSection
    | ParticleItemSection
    | EngineItemSection
    | ReplayItemSection
    | RoomItemSection
)


class ServerItemLeaderboard(BaseModel):
    name: str
    title: str | Text
    description: str | None = None


class ServerItemDetails(BaseModel):
    item: ServerItem
    description: str | None = None
    actions: list[ServerForm]
    hasCommunity: bool
    leaderboards: list[ServerItemLeaderboard]
    sections: list[Annotated[ServerItemSection, Field(discriminator="itemType")]]


class ServerItemInfo(BaseModel):
    creates: list[ServerForm] | None = None
    searches: list[ServerForm] | None = None
    sections: list[Annotated[ServerItemSection, Field(discriminator="itemType")]]
    banner: SRL | None = None


class ServerItemCommunityComment(BaseModel):
    name: str
    author: str
    time: int  # ms epoch
    content: str
    actions: list[ServerForm]


# endregion


class GameplayResult(BaseModel):
    grade: Grade
    arcadeScore: int
    accuracyScore: int
    combo: int
    perfect: int
    great: int
    good: int
    miss: int
    totalCount: int

class ServerSubmitItemActionRequest(BaseModel):
    values: str

class ServerSubmitItemCommunityCommentActionResponse(BaseModel):
    key: str
    hashes: list[str]
    shouldUpdateCommunity: bool | None = None
    shouldUpdateComments: bool | None = None
    shouldNavigateCommentsToPage: int | None = None

class ServerItemCommunityCommentList(BaseModel):
    pageCount: int
    cursor: str | None = None
    comments: list[ServerItemCommunityComment]

class Comment(BaseModel):
    id: int
    commenter: str
    username: str | None = None
    content: str
    created_at: datetime | int # idk probably TODO figure it out
    deleted_at: datetime | int | None = None
    chart_id: str
    owner: bool | None = None

class APIServerDeleteCommentResponse(Comment):
    mod: bool | None = None

class NotificationRequest(BaseModel):
    user_id: str | None = None
    chart_id: str | None = None
    title: str
    content: str | None = None

class APIServerListCommentsResponse(BaseModel):
    data: list[Comment]
    pageCount: int
    mod: bool | None = None
    admin: bool | None = None

class ServerItemCommunityInfo(BaseModel):
    actions: list[ServerForm]
    topComments: list[ServerItemCommunityComment]

class ServerSubmitItemCommunityActionRequest(BaseModel):
    values: str



class CommentRequest(BaseModel):
    content: str

class ParsedServerSubmitCommentActionRequest(BaseModel):
    type: str
    content: str

class ParsedServerSubmitCommentIDActionRequest(BaseModel):
    type: str

class ServerItemList(BaseModel):
    pageCount: int
    cursor: str | None = None
    items: list[ServerItem]
    searches: list[ServerForm] | None = None

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

class APIServerGetChartResponse(BaseModel):
    data: Chart
    asset_base_url: str
    mod: bool | None = None
    owner: bool