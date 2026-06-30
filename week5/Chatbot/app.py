# app.py
import torch
from fastapi import FastAPI
from pydantic import BaseModel

from model import MiniGPT          # 직접 구현한 모델 클래스
from tokenizer_setup import tokenizer  # special token 추가된 PreTrainedTokenizerFast

ckpt_path = "./checkpoint/mini_gpt_260629.pt"

# ----------------------------
# 1. 모델 / 토크나이저 준비 (서버 시작 시 한 번만 로드)
# ----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"

model = MiniGPT(vocab_size=len(tokenizer), block_size=64)  # 학습 때 쓴 값과 동일하게
model.load_state_dict(torch.load(ckpt_path, map_location=device))
model.to(device)
model.eval()

eos_id = tokenizer.eos_token_id
usr_id = tokenizer.convert_tokens_to_ids("<usr>")
stop_ids = [eos_id, usr_id]


# ----------------------------
# 2. 요청/응답 스키마
# ----------------------------
class ChatRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 100


class ChatResponse(BaseModel):
    response: str


# ----------------------------
# 3. FastAPI 앱
# ----------------------------
app = FastAPI(title="MiniGPT Chatbot")


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    formatted = f"<usr> {req.prompt} <bot>"
    ids = tokenizer.encode(formatted)

    if not ids:
        return ChatResponse(response="(no tokens from the prompt are in the vocabulary)")

    if len(ids) >= model.block_size:
        ids = ids[-(model.block_size - 1):]

    idx = torch.tensor([ids], dtype=torch.long, device=device)
    out = model.generate(idx, req.max_new_tokens, stop_ids=stop_ids)[0].tolist()

    generated_ids = out[len(ids):]
    if generated_ids and generated_ids[-1] in stop_ids:
        generated_ids = generated_ids[:-1]

    response = tokenizer.decode(generated_ids, skip_special_tokens=True)
    return ChatResponse(response=response)