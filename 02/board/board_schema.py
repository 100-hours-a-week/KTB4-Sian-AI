# board/board_schema.py

import datetime
from pydantic import BaseModel, field_validator

from comment.comment_schema import Comment

# Board Create
class BoardCreate(BaseModel):
    subject: str
    content: str
    
    @field_validator('subject','content')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 내용은 허용되지 않습니다.')
        return v

# Board Update
class BoardUpdate(BoardCreate):
    board_id: int

# Board Delete
class BoardDelete(BaseModel):
    board_id: int

# Board Schema
class Board(BaseModel):
    id: int
    subject: str
    content: str
    create_date: datetime.datetime
    # Comment 스키마로 구성된 comments 리스트 추가 (backref 명과 동일한 comments)
    comments: list[Comment] =[]
    modify_date: datetime.datetime | None = None

