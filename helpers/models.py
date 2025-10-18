from pydantic import BaseModel, Field
from typing import TypeVar, Optional, Union, Literal, Annotated, Generic
from datetime import datetime

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
    icon: Optional[str] = None


class SRL(BaseModel):
    hash: str
    url: str


class SIL(BaseModel):
    address: str
    name: str


# region Items


class BackgroundItem(BaseModel):
    name: str
    source: Optional[str] = None
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
    source: Optional[str] = None
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
    source: Optional[str] = None
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
    source: Optional[str] = None
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
    source: Optional[str] = None
    author: str
    tags: list[Tag]
    description: Optional[str] = None

    skin: SkinItem
    background: BackgroundItem
    effect: EffectItem
    particle: ParticleItem

    thumbnail: SRL
    playData: SRL
    watchData: SRL
    previewData: SRL
    tutorialData: SRL
    rom: Optional[SRL] = None
    configuration: SRL


class PostItem(BaseModel):
    name: str
    source: Optional[str] = None
    version: int
    title: str
    time: int
    author: str
    tags: list[Tag]
    thumbnail: Optional[SRL] = None


class UseItem(BaseModel):
    useDefault: bool
    item: Union[SkinItem, BackgroundItem, EffectItem, ParticleItem, None] = None


class LevelItem(BaseModel):
    name: str
    source: Optional[str] = None
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
    preview: Optional[SRL] = None
    data: SRL


class PlaylistItem(BaseModel):
    name: str
    source: Optional[str] = None
    version: int
    title: str
    subtitle: str
    author: str
    tags: list[Tag]
    levels: list[LevelItem]
    thumbnail: Optional[SRL] = None


class RoomItem(BaseModel):
    name: str
    title: str
    subtitle: str
    master: str
    tags: list[Tag]
    cover: Optional[SRL] = None
    bgm: Optional[SRL] = None
    preview: Optional[SRL] = None


class ReplayItem(BaseModel):
    name: str
    source: Optional[str] = None
    version: int
    title: str
    subtitle: str
    author: str
    tags: list[Tag]
    level: LevelItem
    data: SRL
    configuration: SRL


ServerItem = Union[
    PostItem,
    RoomItem,
    SkinItem,
    BackgroundItem,
    ParticleItem,
    EffectItem,
    RoomItem,
    PlaylistItem,
    ReplayItem,
    LevelItem,
    EngineItem,
]


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
    name: Union[Text, str]
    description: Optional[str] = None
    required: bool
    type: Literal["collectionItem"] = "collectionItem"
    itemType: ItemType

class DumpDefAliasMixin(BaseModel):
    def model_dump(self, **kwargs):
        kwargs.setdefault("by_alias", True)
        return super().model_dump(**kwargs)

class ServerTextOption(DumpDefAliasMixin):
    query: str
    name: Union[Text, str]
    description: Optional[str] = None
    required: bool
    type: Literal["text"] = "text"
    default: str = Field(validation_alias="def", serialization_alias="def")
    placeholder: Union[Text, str]
    limit: int
    shortcuts: list[str]

class ServerTextAreaOption(DumpDefAliasMixin):
    query: str
    name: Union[Text, str]
    description: Optional[str] = None
    required: bool
    type: Literal["textArea"] = "textArea"
    default: str = Field(validation_alias="def", serialization_alias="def")
    placeholder: Union[Text, str]
    limit: int
    shortcuts: list[str]

class ServerSliderOption(DumpDefAliasMixin):
    query: str
    name: Union[Text, str]
    description: Optional[str] = None
    required: bool
    type: Literal["slider"] = "slider"
    default: Union[int, float] = Field(validation_alias="def", serialization_alias="def")
    min: Union[int, float]
    max: Union[int, float]
    step: Union[int, float]
    unit: Union[Text, str, None] = None

class ServerToggleOption(DumpDefAliasMixin):
    query: str
    name: Union[Text, str]
    description: Optional[str] = None
    required: bool
    type: Literal["toggle"] = "toggle"
    default: bool = Field(validation_alias="def", serialization_alias="def")

class ServerOption_Value(BaseModel):
    name: str
    title: Union[Text, str]

class ServerSelectOption(DumpDefAliasMixin):
    query: str
    name: Union[Text, str]
    description: Optional[str] = None
    required: bool
    type: Literal["select"] = "select"
    default: str = Field(validation_alias="def", serialization_alias="def")
    values: list[ServerOption_Value]

class ServerMultiOption(DumpDefAliasMixin):
    query: str
    name: Union[Text, str]
    description: Optional[str] = None
    required: bool
    type: Literal["multi"] = "multi"
    default: list[bool] = Field(validation_alias="def", serialization_alias="def")
    values: list[ServerOption_Value]

class ServerServerItemOption(DumpDefAliasMixin):
    query: str
    name: Union[Text, str]
    description: Optional[str] = None
    required: bool
    type: Literal["serverItem"] = "serverItem"
    itemType: ItemType
    default: Optional[SIL] = Field(None, validation_alias="def", serialization_alias="def")
    allowOtherServers: bool

class ServerServerItemsOption(DumpDefAliasMixin):
    query: str
    name: Union[Text, str]
    description: Optional[str] = None
    required: bool
    type: Literal["serverItems"] = "serverItems"
    itemType: ItemType
    default: list[SIL] = Field(validation_alias="def", serialization_alias="def")
    allowOtherServers: bool
    limit: int

class ServerCollectionItemOption(BaseModel):
    query: str
    name: Union[Text, str]
    description: Optional[str] = None
    required: bool
    type: Literal["collectionItem"] = "collectionItem"
    itemType: ItemType

class ServerFileOption(DumpDefAliasMixin):
    query: str
    name: Union[Text, str]
    description: Optional[str] = None
    required: bool
    type: Literal["file"] = "file"
    default: str = Field(validation_alias="def", serialization_alias="def")

ServerOption = Union[
    ServerTextOption,
    ServerTextAreaOption,
    ServerSliderOption,
    ServerToggleOption,
    ServerSelectOption,
    ServerMultiOption,
    ServerServerItemOption,
    ServerServerItemsOption,
    ServerCollectionItemOption,
    ServerFileOption,
]


class ServerForm(BaseModel):
    type: str
    title: Union[Text, str]
    icon: Union[Icon, str, None] = None
    description: Optional[str] = None
    help: Optional[str] = None
    requireConfirmation: bool
    options: list[Annotated[ServerOption, Field(discriminator="type")]]


class ServerMessage(BaseModel):
    message: str


class ServerItemSectionTyped(BaseModel):
    title: Union[str, Text]
    icon: Optional[Union[Icon, str]] = None
    description: Optional[str] = None
    help: Optional[str] = None
    itemType: ItemType
    search: Optional[ServerForm] = None
    searchValues: Optional[str] = None

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


ServerItemSection = Union[
    PostItemSection,
    PlaylistItemSection,
    LevelItemSection,
    SkinItemSection,
    BackgroundItemSection,
    EffectItemSection,
    ParticleItemSection,
    EngineItemSection,
    ReplayItemSection,
    RoomItemSection,
]


class ServerItemLeaderboard(BaseModel):
    name: str
    title: Union[str, Text]
    description: Optional[str] = None


class ServerItemDetails(BaseModel, Generic[T]):
    item: T
    description: Optional[str] = None
    actions: list[ServerForm]
    hasCommunity: bool
    leaderboards: list[ServerItemLeaderboard]
    sections: list[Annotated[ServerItemSection, Field(discriminator="itemType")]]


class ServerItemInfo(BaseModel):
    creates: Optional[list[ServerForm]] = None
    searches: Optional[list[ServerForm]] = None
    sections: list[Annotated[ServerItemSection, Field(discriminator="itemType")]]
    banner: Optional[SRL] = None


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
    shouldUpdateCommunity: Optional[bool] = None
    shouldUpdateComments: Optional[bool] = None
    shouldNavigateCommentsToPage: Optional[int] = None

class ServerItemCommunityCommentList(BaseModel):
    pageCount: int
    cursor: Optional[str] = None
    comments: list[ServerItemCommunityComment]

class Comment(BaseModel):
    id: int
    commenter: str
    username: Optional[str] = None
    content: str
    created_at: Union[datetime, int]
    deleted_at: Union[datetime, int, None] = None
    chart_id: str
    owner: Optional[bool] = None

class APIServerDeleteCommentResponse(Comment):
    mod: Optional[bool] = None

class NotificationRequest(BaseModel):
    user_id: Optional[str] = None
    chart_id: Optional[str] = None
    title: str
    content: Optional[str] = None

class APIServerListCommentsResponse(BaseModel):
    data: list[Comment]
    pageCount: int
    mod: Optional[bool] = None
    admin: Optional[bool] = None

class ServerItemCommunityInfo(BaseModel):
    actions: list[ServerForm]
    topComments: list[ServerItemCommunityComment]

class ServerSubmitItemActionRequest(BaseModel):
    values: str

class CommentRequest(BaseModel):
    content: str

class ParsedServerSubmitCommentActionRequest(BaseModel):
    type: str
    content: str

class ParsedServerSubmitCommentIDActionRequest(BaseModel):
    type: str