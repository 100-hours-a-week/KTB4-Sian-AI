# 7주차 Weekly Challenge

| # | 과제 목표 | 진행 |
|---|---|---|
|1| 개인 프로젝트에 LangChain 기반으로 RAG 파이프라인을 구축|✅|
|2| LangChain 기반 RAG 파이프라인을 FastAPI로 래핑하여 REST API로 배포|✅|
|3|LangSmith로 체인 실행을 Tracing하고 Dataset 기반으로 평가|✅|

---
### 파일 구조
```
week7/
├── app.py          REST API
├── main.py         LangChain 단일 테스트 또는 LangSmith 평가 실행
└── langchainfile/
    ├── eval.py     LangSmith 평가
    └── rag.py      LangChain
```
---
### RAG 시스템 간단 설명
- 주제 : TIL 검색 RAG System using LangChain
- 내용 : TIL(Today I Learned)을 작성해둔 문서들(.md)을 이용하여 정리해둔 개념의 정의와 사용 이유 등을 간편히 찾을 수 있다.
---
### RAG 문서
- TIL.md 파일
- 지금까지 배운 강의 TIL 정리 마크다운 파일들을 사용하였다.
- 내가 정리해둔 언어로 개념에 대한 정의 검색이 가능한 모델 구현

---
### 실행 방법

#### LangChain 단일 검색 : 정해진 쿼리
```
uv run main.py --mode chaintest
```
```
TIL에서 알고 싶은 개념을 입력하세요:
>>
```

![01langchaintest](./image/01langchaintest.png)

#### REST API
```
uvicorn app:app

스웨거 문서로 확인
http://localhost:8000/docs

query에 질문을 문장으로 입력
```

#### LangSmith 평가
```
uv run main.py --mode eval
```
![langsmithtest](./image/02langsmithevaltest.png)
두번째 Example: 키워드는 정확히 포함되지 않았지만, 의미상으로는 기대 답변과 일치하다는 의미.

---

---
### 코드 참고 출처
- Alex RAG 코드를 참고하여 서브 퀘스트를 달성함
- 서브 퀘스트
    1. 인덱싱을 매번 하지 않고 인덱싱 결과를 파일이나 영속성 있게 저장한다.
    2. 평가하는 llm이 generation하는 llm과 동일한 상태인데
평가 LLM을 평가 대상 LLM보다 성능이 좋은 모델로 변경한다.

---
### 문제 상황
- model gemini-2.5-flash-lite 토큰 금방 다 쓰는 문제
    - gemini-3.1-flash-lite 사용
- colab 기준: langchain 패키지들 설치시, import가 안되는 경우가 있음. (나눠서 설치하거나 다시 설치하면 됨..)
```
!pip install -q langchain langchain-google-genai langchain-chroma
!pip install -q langchain-community langchain-text-splitters
```

- 문서에서 검색하지 않고 자체적으로 검색하여 대답하는 문제
    - -> 프로젝트 폴더를 옮기는 과정에서 VectorDB파일이 제대로 옮겨지지 않아서 그런듯하다.
    - -> 해결: 인덱싱 처음부터 하고 Vector DB 재생성

---
### 추가 필요한 부분
- 평가하는 LLM이 평가 대상 LLM과 동일한 상황
    - 다른 LLM 사용 가능하도록 수정하기 완료.
    - 그러나 어떤 LLM을 사용해도 좋을지 정하지 못하여 일단 같은 LLM으로 구현해둠.

---
### 회고
#### 1. 배운 점
- 문서를 주고 LLM이 그 문서를 이용해 찾고자 하는 내용을 검색하는 RAG 시스템을 LangChain으로 구현하는 방법에 대해 알게 되었다.
- 과제를 진행하며, 현재는 단순히 주어진 문서에 집중하여 답하도록 되어있으나 일반적으로 문서가 주어진다는 것은 대답할 수 있는 범위를 넓혀주는 것인데, 지금은 오히려 대답하는 범위를 주어진 문서만으로 좁힌 상태였다. 따라서 이를 일반적으로 사용되는 형태로 바꾸려면 어떻게 하면 좋을지 고민이 되었다.

#### 2. 어려웠던 점
- LLM 토큰을 계속 꽉 채워서 사용중임을 깨닫지 못하고 있었어서 exhausted resources 에러가 왜 자꾸 나는지 몰랐는데 Google AI Studio 홈페이지에서 사용한 토큰 량을 볼 수 있다는 것을 깨닫고 원인을 알 수 있었다.
- 코드 설명 작성의 어려움: 어느 깊이까지 상세히 적어야하는지 아직 감이 오지 않아서 자주 작성해보면서 요령을 터득해야 한다.

#### 3. 최종 회고
1. RAG 시스템에 대해 클로드에게 질문한 결과, 가장 기본적인 형태는 문서를 검색해서 답변에 활용하는 보강형으로 쓰인다고 한다. 질문이 들어오면 무조건 관련 문서를 검색하고 검색 결과와 일반 지식을 같이 활용해 답변하여 문서와 무관한 질문도 기존처럼 답변이 가능한 방식을 가장 흔하게 사용하기 때문에 이 방식으로 개선해 나가고 싶다.
2. 챗봇 개인 프로젝트와 연결하게 된다면 반대로 좁은 범위에 대한 전문적인 대답을 할 수 있는 챗봇을 만들어야 할지, 일반화가 가능한 챗봇을 만들어야할지 모르겠다.
