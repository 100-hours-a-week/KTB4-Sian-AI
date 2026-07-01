# Hugging Face Transformers 라이브러리에서 텍스트 생성용 모델 클래스와 토크나이저 클래스를 가져옵니다.
from transformers import AutoModelForCausalLM, AutoTokenizer
from indexing import embedding

# 사용할 LLM 모델 이름을 문자열로 지정합니다.
# Qwen2.5-1.5B-Instruct는 대화형 지시(instruct) 형식에 맞게 답변을 생성할 수 있는 경량 모델입니다.
# 한국어를 포함한 다국어를 지원하므로, 한국어 질문-답변 실습에 사용할 수 있습니다.
llm_model_name = "Qwen/Qwen2.5-1.5B-Instruct"

# 지정한 모델 이름에 맞는 토크나이저를 불러옵니다.
# 토크나이저는 사람이 읽는 문자열을 모델이 처리할 수 있는 토큰 ID로 변환하는 역할을 합니다.
llm_tokenizer = AutoTokenizer.from_pretrained(llm_model_name)

# 지정한 모델 이름에 맞는 텍스트 생성용 LLM을 불러옵니다.
# from_pretrained()는 Hugging Face 저장소에서 모델 가중치를 다운로드하여 로드합니다.
llm_model = AutoModelForCausalLM.from_pretrained(
    llm_model_name,

    # torch_dtype="auto"는 실행 환경에 맞는 적절한 데이터 타입을 자동으로 선택합니다.
    # 예를 들어 GPU 환경에서는 더 효율적인 dtype을 사용할 수 있습니다.
    torch_dtype="auto",

    # device_map="auto"는 사용 가능한 장치(CPU/GPU)에 모델을 자동으로 배치합니다.
    # Colab이나 GPU 환경에서는 가능한 경우 GPU에 자동으로 올려 실행합니다.
    device_map="auto"
)


def generate_answer(query, retrieved_chunks):
    """
    검색된 청크를 프롬프트에 삽입하고, LLM으로 답변을 생성합니다.

    매개변수
    query : str
        사용자의 자연어 질문
    retrieved_chunks : list[str]
        Retrieval에서 반환된 청크 텍스트 목록
    llm_model : AutoModelForCausalLM
        답변 생성에 사용할 LLM
    llm_tokenizer : AutoTokenizer
        LLM의 토크나이저
    """

    # 1. 검색된 청크를 하나의 문맥(context)으로 합칩니다.
    # 청크 사이를 "---"로 구분하여 LLM이 각 청크의 경계를 인식할 수 있도록 합니다.
    # context는 LLM이 참고할 근거 문서 묶음입니다.
    context = "\n---\n".join(retrieved_chunks)

    # 2. 프롬프트를 구성합니다.
    # system: LLM의 답변 규칙 (문서 근거 답변, 환각 방지 지시)
    # user: 검색된 문서 + 사용자 질문
    # messages는 채팅형 LLM이 이해하는 대화 형식입니다.
    messages = [
        {
            "role": "system",
            "content": (
                "당신은 한국은행에서 만든 금융 용어를 설명해주는 금융 전문가입니다. "
                "다음 문서를 참고하여 질문에 상세히 설명하고 한국어 존댓말로 답하세요. "
                "문서에 없는 내용은 '제공된 문서에서 해당 정보를 찾을 수 없습니다'라고 답하세요."
            )
        },
        {
            "role": "user",
            # user 메시지 안에 검색된 문서와 질문을 함께 넣습니다.
            "content": f"[문서]\n{context}\n\n[질문]\n{query}"
        }
    ]

    # 3. chat template을 적용하여 LLM 입력 형식으로 변환합니다.
    # apply_chat_template()는 messages를 Qwen이 기대하는 실제 입력 문자열로 바꿉니다.
    # text는 최종 프롬프트 문자열입니다.
    text = llm_tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # 문자열 프롬프트를 토큰 ID로 변환합니다.
    # model_inputs에는 input_ids, attention_mask 등이 들어 있습니다.
    model_inputs = llm_tokenizer([text], return_tensors="pt").to(llm_model.device)

    # 4. LLM을 호출하여 답변을 생성합니다.
    # generated_ids에는 입력 토큰 + 새로 생성된 답변 토큰이 함께 들어 있습니다.
    generated_ids = llm_model.generate(
        **model_inputs,
        max_new_tokens=256
    )

    # 5. 입력 부분을 제외하고 생성된 답변만 디코딩합니다.
    # 입력 프롬프트 길이만큼 앞부분을 잘라, 새로 생성된 토큰만 남깁니다.
    generated_ids = [
        output_ids[len(input_ids):]
        for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    # batch_decode()는 토큰 ID를 사람이 읽을 수 있는 문자열로 변환합니다.
    answer = llm_tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    return answer

def generate_main(query, collection):
    query_embedding = embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )
    # 검색된 청크 텍스트를 꺼냅니다.
    retrieved_chunks = results["documents"][0]

    # 검색 결과를 확인합니다.
    print("===== Retrieval 결과 =====")
    for i, chunk in enumerate(retrieved_chunks):
        pages = results["metadatas"][0][i]["page"]
        dist = results["distances"][0][i]
        print(f"  [{i+1}위] {chunk[:80]}...")
        print(f"       출처: p.{pages}, 거리: {dist:.4f}")
    print()

    # Generation: 검색된 청크를 근거로 답변을 생성합니다.
    answer = generate_answer(query, retrieved_chunks)

    print("===== Generation 결과 =====")
    print(f"질문: {query}")
    print(f"답변: {answer}")

    return answer
