# comment/comment_crud.py

from datetime import datetime

from sqlalchemy.orm import Session

from comment.comment_schema import CommentCreate, CommentUpdate
from models import Boardtable, Commenttable

# create comment
def create_comment(db:Session, db_board:Boardtable, comment_create: CommentCreate):
    db_comment = Commenttable(board=db_board,
                              content=comment_create.content,
                              create_date=datetime.now())
    db.add(db_comment)
    db.commit()

# get all comments from Commenttable (Useless)
def get_all_comments(db:Session):
    all_comments = db.query(Commenttable)\
    .order_by(Commenttable.create_date.desc())\
    .all()

    return all_comments

# get one comment
def get_comment(db: Session, comment_id: int):
    # comment의 고유번호인 comment_id 와 일치하는 답변 조회하여 리턴
    return db.query(Commenttable).get(comment_id)


# update comment
def update_comment(db: Session, db_comment:Commenttable,
                   comment_update: CommentUpdate):
    db_comment.content = comment_update.content
    db_comment.modify_date = datetime.now()
    db.add(db_comment)
    db.commit()

# delete comment
def delete_comment(db:Session, db_comment: Commenttable):
    db.delete(db_comment)
    db.commit()