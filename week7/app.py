from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from langchainfile.rag import build_rag_chain

# === 요청 / 응답 스키마 ===
class QueryRequest(BaseModel):
  question: str

class QueryResponse(BaseModel):
  answer: str


# Lifespan : 앱 생명주기 관리
# FastAPI 앱 초기화 시점에 인덱싱 + RAG 체인 구성
# build_rag_chain()은 무거운 초기화 작업을 포함하기 때문에 서버가 켜질 때 딱 한번만 실행되게 한다.
@asynccontextmanager  #진입 시 처리/ 종료 시 처리 를 나누는 데코레이터
async def lifespan(app: FastAPI):
  #app.state : FastAPI가 제공하는 앱 전역 저장소
  #다른 모든 라우트 함수에서 app.state.rag로 접근 가능
  app.state.rag = build_rag_chain()
  yield

# FastAPI 앱 인스턴스를 생성하면서 lifespan 함수를 등록
app = FastAPI(lifespan=lifespan)

# 라우트 핸들러 비동기 처리
# 기다리는 동안 다른 일 처리 가능
# async def 함수는 호출하는 즉시 실행되지 않고, 코루틴 객체를 반환한다.
# 이 코루틴 객체는 await되거나 이벤트 루프에 의해 스케줄링 되어야 실제로 실행된다.
@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
  answer = await app.state.rag.ainvoke(req.question)
  return QueryResponse(answer=answer)