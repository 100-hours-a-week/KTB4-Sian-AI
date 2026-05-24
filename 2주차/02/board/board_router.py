# board/board_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from board import board_schema, board_crud
from comment import comment_crud

from database import get_db
import httpx

# prefix 속성은 요청 URL에 항상 포함되어야 하는 값
router = APIRouter(
    prefix="/board"
)

# 게시글 생성
@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def create_board(_board_create: board_schema.BoardCreate,
                db: Session= Depends(get_db)):
    # create post
    board_crud.create_post(db=db, board_create=_board_create)

# 모든 게시물 조회
@router.get("/posts", response_model=list[board_schema.Board])
def view_all_boards(db: Session = Depends(get_db)):
    return board_crud.get_all_posts(db)

# 특정 게시글 조회
# url을 통해 얻은 board_id 값으로 게시글 상세 내역을 조회하여 Board 스키마로 리턴하는 함수
@router.get("/detail/{board_id}", response_model=board_schema.Board)
def view_board(board_id: int, db: Session = Depends(get_db)):
    db_board = board_crud.get_one_post(db, board_id=board_id)
    if not db_board:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="게시글을 찾을 수 없습니다.")
    
    return db_board

# 특정 게시글 수정
@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
def update_board(_board_update: board_schema.BoardUpdate,
                 db: Session = Depends(get_db)):
    db_board = board_crud.get_one_post(db, board_id = _board_update.board_id)
    if not db_board:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="게시글을 찾을 수 없습니다.")

    board_crud.update_post(db=db, db_board=db_board, board_update=_board_update)


# 특정 게시글 삭제
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(_board_delete: board_schema.BoardDelete,
                 db: Session = Depends(get_db)):
    db_board = board_crud.get_one_post(db, board_id=_board_delete.board_id)
    if not db_board:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="게시글을 찾을 수 없습니다.")
    
    # 게시글에 달린 댓글 먼저 삭제
    for comment in db_board.comments:
        del_comment = comment_crud.get_comment(db, comment_id=comment.id)
        if not del_comment:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="해당 댓글을 찾을 수 없습니다.")
        else:
            comment_crud.delete_comment(db=db, db_comment=del_comment)


    board_crud.delete_post(db=db, db_board=db_board)


#해당 게시글 요약
@router.post("/summary/{board_id}")
def summarize_board(board_id: int, db:Session=Depends(get_db)) -> dict:
    db_board = board_crud.get_one_post(db, board_id=board_id)
    if not db_board:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="해당 게시물을 찾을 수 없습니다.")

    payload = {
        "model": "gemma4:e2b",
        "messages": [
            {"role": "system", "content": "You are a kind AI Assistant."},
            {"role": "user", "content": f"Summarize the content briefly:\n\n{db_board.content}"},
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