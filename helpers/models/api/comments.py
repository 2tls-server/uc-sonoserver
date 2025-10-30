from datetime import datetime
from pydantic import BaseModel

class Comment(BaseModel):
    id: int
    commenter: str
    username: str | None = None
    content: str
    created_at: datetime | int # idk probably TODO figure it out
    deleted_at: datetime | int | None = None
    chart_id: str
    owner: bool | None = None

class DeleteCommentResponse(Comment):
    mod: bool | None = None

class CommentList(BaseModel):
    data: list[Comment]
    pageCount: int
    mod: bool | None = None
    admin: bool | None = None

class CommentRequest(BaseModel):
    content: str