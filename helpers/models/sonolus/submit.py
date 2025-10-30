from typing import Literal
from urllib.parse import parse_qs
from pydantic import BaseModel

class ServerSubmitItemActionRequest(BaseModel):
    values: str


class _ParsedServerSubmitCommentActionRequest(BaseModel):
    type: str
    content: str

class ServerSubmitCommentActionRequest(ServerSubmitItemActionRequest):
    def parse(self) -> _ParsedServerSubmitCommentActionRequest:
        return _ParsedServerSubmitCommentActionRequest.model_validate({k: v[0] for k, v in parse_qs(self.values).items()})
    


class _ParsedServerSubmitCommentIDActionRequest(BaseModel):
    type: str

class ServerSubmitCommentIDActionRequest(ServerSubmitItemActionRequest):
    def parse(self) -> _ParsedServerSubmitCommentIDActionRequest:
        return _ParsedServerSubmitCommentIDActionRequest.model_validate({k: v[0] for k, v in parse_qs(self.values).items()})
    
    
class _ParsedServerSubmitLevelActionRequest(BaseModel):
    type: str
    visibility: Literal["UNLISTED", "PRIVATE", "PUBLIC", None] = None
    constant: str | None = None

class ServerSubmitLevelActionRequest(ServerSubmitItemActionRequest):
    def parse(self) -> _ParsedServerSubmitLevelActionRequest:
        return _ParsedServerSubmitLevelActionRequest.model_validate({k: v[0] for k, v in parse_qs(self.values).items()})