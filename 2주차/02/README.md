# 2주차 과제
# 2. FastAPI로 커뮤니티 서비스의 백엔드 구현
### 1. HTTP REST API 설계 및 구현
### 2. AI 모델 서빙
### 3. 데이터베이스 적용하기
### 4. 구조 개선하기
### 5. (선택) 프론트엔드 만들기
## 프로그램 목적
게시글 조회, 작성, 수정, 삭제 그리고 해당 게시글에 대한 댓글 조회, 작성, 수정, 삭제해 주는 기능 구현.

게시글과 댓글을 gemma4로 요약해주는 기능 구현.

## 프로그램 구조
```
02
├── main.py
├── database.py
├── models.py
├── board
│   ├── board_crud.py
│   ├── board_router.py
│   └── board_schema.py
└── comment
    ├── comment_crud.py
    ├── comment_router.py
    └── comment_schema.py

````
database.py : 데이터베이스와 관련된 설정

models.py : SQLAlchemy를 이용해 모델 기반으로 데이터베이스 처리

board 디렉터리 : 게시글과 관련된 파일들 모음

comment 디렉터리 : 댓글과 관련된 파일들 모음

board_router.py, comment_router.py : 라우터 파일, URL과 API 동작 관리

board_crud.py, comment_crud.py : 데이터의 CRUD를 처리

board_schema.py, comment_schema.py : 입출력 관리 파일

## 프로그램 기능

### 게시글 관련 기능
|API명|요청 방법|URL|
|------|---|---|
|게시글 작성|POST|/board/create|
|전체 게시글 조회|GET|/board/posts|
|게시글 한 개 조회 (댓글도 함께 조회됨)|GET| /board/detail/{board_id}|
|게시글 수정|PUT|/board/update|
|게시글 삭제|DELETE| /board/delete|
|게시글 요약 (LLM 사용)|POST| /board/summary/{board_id}|


---
### 댓글 관련 기능
|API명|요청 방법|URL|
|------|---|---|
|댓글 작성 (특정 게시글에 대한 )|POST|/comment/create/{board_id}|
|전체 댓글 조회|GET|/comment/comments|
|댓글 한 개 조회 |GET| /comment/detail/{comment_id}|
|댓글 수정|PUT|/comment/update|
|댓글 삭제|DELETE| /comment/delete|
|댓글 요약 (LLM 사용)|POST| /comment/summary/{comment_id}|



## How to use
```
uv add uvicorn
uv add fastapi
uv add SQLAlchemy
uv add httpx
```
ollama 사용하여 gemma4:e2b 갖고오기

```
uvicorn main:app
```
http://localhost:8000/docs 에서 실행 확인

## 실행 예시

<img width="585" height="763" alt="Image" src="https://github.com/user-attachments/assets/d5b20919-daff-489b-9d63-3dae45261f6f" />

## 주의사항
실행 전 테이블 초기화를 위해 다음을 실행하기를 권장함.

Alembic 리비전 파일 생성하고 실행하기
```

alembic revision -autogenerate
alembic upgrade head

```

## 필요한 추가 기능
1. 게시글이 삭제되거나 댓글이 삭제되면 게시글 id와 댓글 id가 다시 1부터 차례대로 부여되는 기능

2. 게시글 조회시 자동으로 요약본을 보여주는 기능

## 과제 참고 링크
[점프투 fastAPI](https://wikidocs.net/175950) : 예제 따라하며 익히고 과제에 적용 
