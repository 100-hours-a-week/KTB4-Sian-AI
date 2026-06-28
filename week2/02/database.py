# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 프로젝트 루트 디렉터리의 sqp02.db 를 sqlite 데이터베이스에 연결
DB_URL = "sqlite:///./sql02.db"

engine = create_engine(
    # 스레드가 하나만 실행되게 ?
    DB_URL, connect_args ={"check_same_thread":False}
)

# 데이터베이스 세션, 접속하기 위해 필요한 클래스
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 이 클래스를 상속 받은 클래스들을 자동으로 데이터베이스 테이블에 매핑
Base = declarative_base()

# db 세션 객체를 리턴하는 제너레이터인 get_db 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
