# comment/comment_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from comment import comment_schema, comment_crud
from board import board_crud

from database import get_db
import httpx

router = APIRouter(
    prefix="/comment"
)

# 댓글 작성
@router.post("/create/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def create_comments(board_id: int,
                   _comment_create: comment_schema.CommentCreate,
                   db: Session=Depends(get_db)):
    # if no board found, exception
    db_board = board_crud.get_one_post(db, board_id=board_id)
    if not db_board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    # create comment
    comment_crud.create_comment(db, db_board=db_board, comment_create=_comment_create)


# 모든 댓글 조회 (useless)
@router.get("/comments", response_model=list[comment_schema.Comment])
def view_all_comments(db: Session = Depends(get_db)):
    return comment_crud.get_all_comments(db)

# 해당 게시글에 대한 댓글 조회

# 해당 댓글 조회
@router.get("/detail/{comment_id}", response_model=comment_schema.Comment)
def view_comment(comment_id: int, db: Session=Depends(get_db)):
    db_comment = comment_crud.get_comment(db, comment_id=comment_id)
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="해당 댓글을 찾을 수 없습니다.")

    return db_comment

# 해당 댓글 수정
@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
def update_comment(_comment_update: comment_schema.CommentUpdate,
                   db:Session = Depends(get_db)):
    db_comment = comment_crud.get_comment(db, comment_id=_comment_update.comment_id)
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="댓글을 찾을 수 없습니다.")
    
    comment_crud.update_comment(db=db, db_comment=db_comment, comment_update=_comment_update)


# 댓글 삭제
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(_comment_delete: comment_schema.CommentDelete,
                   db: Session = Depends(get_db)):
    db_comment = comment_crud.get_comment(db, comment_id=_comment_delete.comment_id)
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="댓글을 찾을 수 없습니다.")
    
    comment_crud.delete_comment(db=db, db_comment=db_comment)







#해당 댓글 요약

@router.post("/summary/{comment_id}")
def summarize_comment(comment_id: int, db:Session=Depends(get_db)) -> dict:
    comment = comment_crud.get_comment(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="해당 댓글을 찾을 수 없습니다.")

    payload = {
        "model": "gemma4:e2b",
        "messages": [
            {"role": "system", "content": "You are a kind AI Assistant."},
            {"role": "user", "content": f"Summarize the content briefly:\n\n{comment.content}"},
        ],
    }
    response = httpx.post(
        "http://localhost:11434/v1/chat/completions",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=60.0,
    )
    result = response.json()
    return {"summary": result["choices"][0]["message"]["content"]}
