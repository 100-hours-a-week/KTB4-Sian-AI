# comment/comment_schema.py

import datetime
from pydantic import BaseModel, field_validator

# content 입력항목을 처리하는데 사용할 스키마
class CommentCreate(BaseModel):
    content: str

    # 빈 문자열 허용 금지
    @field_validator('content')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('댓글 내용이 빈 값입니다.')
        return v
    
class CommentUpdate(CommentCreate):
    comment_id: int

class CommentDelete(BaseModel):
    comment_id: int

# 게시글 상세 조회에 사용할 Comment 스키마 = 출력으로 사용할 답변 1건 
class Comment(BaseModel):
    id:int
    content:str
    create_date: datetime.datetime
    # 게시글로 돌아가기 위해 해당 댓글이 작성된 게시글의 번호 필요
    board_id: int

    modify_date: datetime.datetime | None = None
