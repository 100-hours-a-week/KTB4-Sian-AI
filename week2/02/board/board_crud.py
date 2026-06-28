# board/board_crud.py

from datetime import datetime
from models import Boardtable
from sqlalchemy.orm import Session

from board.board_schema import BoardCreate, BoardUpdate

# get all posts from Boardtable
def get_all_posts(db:Session):
    all_posts = db.query(Boardtable)\
    .order_by(Boardtable.create_date.desc())\
    .all()

    return all_posts

# get one post (board_id에 해당하는 게시글을 조회하여 리턴)
def get_one_post(db: Session, board_id:int):
    post = db.query(Boardtable).get(board_id)
    return post

# create one post
def create_post(db: Session, board_create: BoardCreate):
    db_board = Boardtable(subject= board_create.subject,
                          content = board_create.content,
                          create_date =datetime.now())
    db.add(db_board)
    db.commit()

# update one post
def update_post(db: Session, db_board: Boardtable,
                board_update: BoardUpdate):
    db_board.subject = board_update.subject
    db_board.content = board_update.content
    db_board.modify_date = datetime.now()
    db.add(db_board)
    db.commit()

# delete one post
def delete_post(db: Session, db_board: Boardtable):
    db.delete(db_board)
    db.commit()