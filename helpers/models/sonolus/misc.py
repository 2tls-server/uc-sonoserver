from pydantic import BaseModel
from helpers.sonolus_typings import Icon, ServerInfoButtonType, Text

class Tag(BaseModel):
    title: str
    icon: Icon | str | None = None


class SRL(BaseModel):
    hash: str
    url: str


class SIL(BaseModel):
    address: str
    name: str

class ServerInfoButton(BaseModel):
    type: ServerInfoButtonType

class ServerItemLeaderboard(BaseModel):
    name: str
    title: str | Text
    description: str | None = None

class ServerMessage(BaseModel):
    message: str