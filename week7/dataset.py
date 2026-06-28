import torch
from datasets import load_dataset
from transformers import PreTrainedTokenizerFast

#공통: 토크나이저
# 한국어를 토큰화해야하므로 사전 학습된 한국어 GPT 토크나이저를 그대로 가져와서 사용

MODEL_NAME = "skt/kogpt2-base-v2"
tokenizer = PreTrainedTokenizerFast.from_pretrained(
    MODEL_NAME,
    bos_token='</s>',
    eos_token='</s>',
    unk_token='<unk>',
    pad_token='<pad>',
    mask_token='<mask>'
)
# <usr>, <bot>을 special token으로 추가 (쪼개지지 않게)
special_tokens = {"additional_special_tokens": ["<usr>", "<bot>"]}
num_added = tokenizer.add_special_tokens(special_tokens)

vocab_size = len(tokenizer)  # 토큰 추가로 늘어난 크기 반영

## songys/Chatbot_data : 질문-답변 쌍 (단순 Q&A)
def load_chatbot_data(block_size=64, batch_size=32, device="cpu"):
    """
    songys/Chatbot_data를 로드해서 "<usr> 질문 <bot> 답변" 형태의 한 줄 텍스트로 합치고
    전체를 토큰화해서 하나의 긴 토큰 시퀀스로 이어 붙인다.
    데이터가 작기 때문에 GPT 사전학습처럼 전체를 이어 붙여서 학습하는 방식이 잘 맞다
    """

    # huggingface hub에 정식 등록된 형태가 아니기때문에 보통 CSV를 직접 받아서 사용
    ds = load_dataset(
        "csv",
        data_files="https://raw.githubusercontent.com/songys/Chatbot_data/master/ChatbotData.csv"
    )["train"]
    # ds[i] = {"Q": "질문 텍스트", "A": "답변 텍스트", "label": 0/1/2}
    # 0=일상, 1=이별/부정, 2=사랑/긍정

    # 모든 질문-답변 쌍을 "<usr> Q <bot> A" 형태의 한 문자열로 합침
    texts = [f"<usr> {row['Q']} <bot> {row['A']}" for row in ds]
    full_text = "\n".join(texts) # 전체를 하나의 긴 텍스트로 연결

    # 토큰화: 텍스트 -> 토큰 id 리스트 (전체를 한번에 인코딩)
    all_ids = tokenizer.encode(full_text)
    data = torch.tensor(all_ids, dtype=torch.long)

    # train/val 분리 (9:1)
    n = int(len(data)* 0.9)
    train_data, val_data = data[:n], data[n:]

    def get_batch(split="train"):
        # split에 따라 train/val 데이터 중 하나를 선택
        d = train_data if split == "train" else val_data
        #배치 크기만큼 랜덤한 시작 위치를 뽑음
        ix = torch.randint(0, len(d) - block_size -1, (batch_size,))
        # x: 입력 시퀀스, y: x를 한칸씩 뒤로 민 시퀀스 (= next-token 정답)
        x = torch.stack([d[i:i+block_size] for i in ix]).to(device)
        y = torch.stack([d[i+1:i+block_size+1] for i in ix]).to(device)

        return x,y

    return get_batch, len(tokenizer) # vocab_size