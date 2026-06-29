#평가
from langsmith.evaluation import evaluate
from langsmith import Client

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

import os

DATASET_NAME = "sian-til-rag-eval"
EVAL_QUESTIONS = [
    {
        "question": "RAG란 무엇인가요?",
        "answer":   "RAG란 외부 문서를 가져와서 그것을 기반으로 LLM이 답변하도록 하는 기법입니다.",
    },
    {
        "question": "유사도 검색은 무엇인가요?",
        "answer":   "사용자 질문 벡터와 벡터 DB에 있는 벡터 사이의 각도를 계산하여 유사도를 측정하는 방법입니다.",
    },
    {
        "question": "멀티 프로세스는 무엇인가요?",
        "answer":   "멀티 프로세스는 하나의 프로그램을 여러 프로세스로 나누어 동시에 실행하는 방식으로 멀티 코어일 경우 병렬 처리가 가능합니다.",
    },
    {
        "question": "시간 역전파에 대해 설명해주세요.",
        "answer":   "시간 역전파는 층(Layer)을 역으로 가는 것이 아니라 시간을 역으로 가면서 역전파를 계산하는 것입니다.",
    },
]
print(f"검증 질문 수: {len(EVAL_QUESTIONS)}")

JUDGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
      "당신은 답변 품질을 평가하는 채점자입니다.\n"
      "의미가 일치하면 1, 부분적으로만 일치하면 0.5, 무관하면 0을 점수로 매기세요.\n"
      "응답은 반드시 첫 줄에 0/0.5/1 중 하나의 숫자만, 둘째 줄부터 짧은 이유를 적으세요."),
    (
        "human",
        "질문: {question}\n\n"
        "기대 답변: {reference}\n\n"
        "모델 답변: {prediction}"
    ),
  ])

# ============================================
# 1. 데이터셋 
def get_or_create_dataset(client):
  # 1. 평가용 입력/출력 분리
  inputs = [{"question": ex["question"]} for ex in EVAL_QUESTIONS]
  outputs = [{"answer": ex["answer"]} for ex in EVAL_QUESTIONS]

  # 2. 데이터셋 존재 여부 확인 (중복 생성 방지)
  # 이미 데이터셋 존재하면 재사용, 없으면 새로 생성

  # 이름이 일치하는 데이터셋들을 리스트로 반환
  existing = [d for d in client.list_datasets(dataset_name=DATASET_NAME)]

  if existing:
    dataset = existing[0]
    print(f"기존 Dataset 사용: {dataset.id}")
  else:
    dataset = client.create_dataset(  # 데이터셋 새로 생성
        dataset_name = DATASET_NAME,
        description="TIL RAG 답변 품질 평가용"
    )
    print(f"새 Dataset 생성: {dataset.id}")
    client.create_examples(           # 데이터셋 새로 만든 경우에만 example 추가
        dataset_id = dataset.id,
        inputs=inputs,
        outputs=outputs,
    )
    print(f"Example {len(EVAL_QUESTIONS)}건 추가 완료")

  return dataset

def preview_dataset(client, dataset, n):
  # 데이터셋 내용을 미리 확인 (디버깅용)
  examples = list(client.list_examples(dataset_id=dataset.id))
  print(f"총 Example 수: {len(examples)}")

  # Example 미리 보기 출력 : 데이터가 제대로 들어갔는지 확인하는 디버깅용 코드
  for ex in examples[:n]:
    print("Q:", ex.inputs["question"])
    print("A:", ex.outputs["answer"] if ex.outputs else "(없음)")
    print()

  return examples

# ==================================================
# 2. 평가자
def contains_expected_keyword(run, example):
  # === 평가자 1 : 키워드 포함 여부 (규칙 기반) ===
  pred = run.outputs.get("answer", "")
  expected = example.outputs.get("answer","")

  # === 기대 답변에서 명사로 보이는 단어(2글자 이상 단어) 2개를 키워드로 사용 ===
  # 단점: 단어 선택이 split()이라 조사가 안 붙은 정확한 단어가 아니면 매칭 실패 가능
  keywords = [w for w in expected.split() if len(w) >= 2][:2]
  hit = all(k in pred for k in keywords)

  return {
      "key": "contains_expected_keyword",
      "score": 1 if hit else 0,
      "comment": f"필수 키워드 {keywords} 포함 여부"
  }

def make_llm_judge(llm):
  # === 평가자 2 : LLM-as-Judge (의미 기반) ===
  # llm을 주입받아 llm_judge 평가자 함수를 생성하는 팩토리 함수
  judge_chain = JUDGE_PROMPT | llm | StrOutputParser()

  def llm_judge(run, example):
    # LLM을 채점자로 활용해 0/0.5/1 점수 산출
    # 첫 줄 숫자만 파싱, 실패시 0점 처리
    reply = judge_chain.invoke({
        "question": example.inputs["question"],
        "reference": example.outputs["answer"],
        "prediction": run.outputs["answer"],
    })
    # === 첫 줄의 숫자만 점수로 사용 ===
    first_line = reply.strip().splitlines()[0].strip()
    try:
      score = float(first_line)
    except ValueError:
      score = 0
    return {
        "key": "llm_judge_semantic_match",
        "score": score,
        "comment": reply,
    }
  
  return llm_judge

# ==================================================
# 3. 평가대상 (target)
def make_target(rag):
  def target(inputs):
    return {"answer": rag.invoke(inputs["question"])}
  return target

# ==================================================
# 4. EVALUATION
def eval_rag(rag):
  client = Client()

  #데이터셋 준비
  dataset = get_or_create_dataset(client)
  loaded = client.read_dataset(dataset_name=DATASET_NAME)
  # 확인용
  preview_dataset(client, loaded, 2)

  # 평가하는 모델은 평가 받는 모델과 다른 모델을 선택한다.
  judge_llm = ChatGoogleGenerativeAI(
          model="gemini-2.5-flash-lite",
          google_api_key=os.getenv("GOOGLE_API_KEY"),
      )
  
  # 평가자
  llm_judge = make_llm_judge(judge_llm)

  # 평가 대상
  target = make_target(rag)

  # === 평가 실행 === 
  # target 함수를 데이터셋의 모든 질문에 대해 실행
  result = evaluate(
      target,
      data=DATASET_NAME,
      evaluators = [contains_expected_keyword, llm_judge], # 규칙 기반 & 의미 기반
      experiment_prefix="v1-baseline",
  )

  return result