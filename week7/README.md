# 7주차 Weekly Challenge 회고

| # | 과제 목표 | 진행 |
|---|---|---|
|1| 개인 프로젝트에 LangChain 기반으로 RAG 파이프라인을 구축|✅|
|2| LangChain 기반 RAG 파이프라인을 FastAPI로 래핑하여 REST API로 배포|✅|
|3|LangSmith로 체인 실행을 Tracing하고 Dataset 기반으로 평가|✅|

---
### 파일 구조 (차후 변경 예정)
```
week7/
├── app.py          REST API
├── main.py         LangChain 단일 테스트 또는 LangSmith 평가 실행
└── langchainfile/
    ├── eval.py     LangSmith 평가
    └── rag.py      LangChain
```
---
### RAG 문서
- TIL.md 파일
- 지금까지 배운 강의 TIL 정리 마크다운 파일들을 사용하였다.
- 내가 정리해둔 언어로 개념에 대한 정의 검색이 가능한 모델 구현

---
### 실행 방법

#### LangChain
```
uv run main.py --mode chaintest
```

#### REST API
```
uvicorn app:app
```

#### LangSmith 평가
```
uv run main.py --mode eval
```
---
### 코드 참고
- Alex RAG 코드를 참고하여 서브 퀘스트를 달성함
- 서브 퀘스트 1. 인덱싱을 매번 하지 않고 인덱싱 결과를 파일이나 영속성 있게 저장한다.
- 서브 퀘스트 2. 평가하는 llm이 generation하는 llm과 동일한 상태인데
평가 LLM을 평가 대상 LLM보다 성능이 좋은 모델로 변경한다.

---
### 문제 상황
- colab에서 코드 실행했을때보다 자주 LLM resources exhausted 가 발생하는 것 같다.

---
### 추가 필요한 부분
- 평가하는 LLM이 평가 대상 LLM과 동일한 상황
    - 다른 LLM 사용 가능하도록 수정하기 완료.
    - 그러나 어떤 LLM을 사용해도 좋을지 정하지 못하여 일단 같은 LLM으로 구현해둠.

