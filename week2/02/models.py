# models.py

from database import Base
from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class Boardtable(Base):
    __tablename__ = "boardtable"

    id = Column(Integer, primary_key=True) #고유 번호
    subject = Column(String, nullable=False) #제목
    content = Column(Text, nullable=False) #내용
    create_date = Column(DateTime, nullable=False) #작성일시
    
    # 수정일시 (수정이 발생할 경우에만 생성되므로 nullable True)
    modify_date = Column(DateTime, nullable=True) 

class Commenttable(Base):
    __tablename__ = "commenttable"

    id = Column(Integer, primary_key=True) #고유 번호
    content = Column(Text, nullable=False) #내용
    create_date = Column(DateTime, nullable=False) #작성일시

    # 수정일시 (수정이 발생할 경우에만 생성되므로 nullable True)
    modify_date = Column(DateTime, nullable=True) 

    # 게시글과 댓글을 연결하기 위한 속성
    # 'boardtable.id'는 board 테이블의 id 컬럼을 의미한다.
    # Comment 모델의 board_id 속성은 boardtable의 id 컬럼과 연결된다.
    board_id = Column(Integer, ForeignKey("boardtable.id"))

    # comment 모델에서 board모델을 참조하기 위해 추가
    # relationship으로 board속성을 생성하면 comment 객체에서 연결된
    # 게시글의 제목을 comment.board.subject 처럼 참조할 수 있다.
    # relationship의 첫번째 파라미터 : 참조할 모델명
    # 두번째 파라미터: 역참조 설정
    board = relationship("Boardtable", backref="comments")
    # Commenttable 모델은 Boardtable 모델과 comments 라는 이름으로 연결되어 있다. (backref)
    # 따라서 Board 스키마에도 comments라는 이름의 속성을 이용해야 등록된 댓글이 정확히 매핑된다.