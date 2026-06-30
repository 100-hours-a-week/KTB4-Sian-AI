from dataset import load_chatbot_data, tokenizer
from model import build_gpt, train
import torch

ckpt_path = "./checkpoint/mini_gpt_260629.pt"

def chat(model, tokenizer, checkpoint_path="mini_gpt.pt",
         device="cpu", max_new_tokens=100, stop_tokens=("<usr>",),
):
    """
    학습된 GPT 모델을 로드해서 터미널 기반 챗봇 인터페이스를 실행

    Args:
        model: block_size, generate(idx, max_new_tokens, stop_ids) 를 갖춘 모델 객체 (가중치 로드 전 상태)
        tokenizer: encode/decode, eos_token_id, convert_tokens_to_ids 를 지원하는 토크나이저
        checkpoint_path: 학습된 state_dict 파일 경로
        device: "cpu" 또는 "cuda"
        max_new_tokens: 답변 생성 시 최대 토큰 수
        stop_tokens: eos 외에 생성을 멈출 추가 토큰들 (기본: "<usr>")
    """
    model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    model.to(device)
    model.eval()

    eos_id = tokenizer.eos_token_id
    stop_ids = [eos_id] + [tokenizer.convert_tokens_to_ids(t) for t in stop_tokens]

    print("Type a prompt and the model will continue it (empty line or Ctrl-D to quit)")
    while True:
          try:
               prompt = input("> ")
          except EOFError:
               break
          if not prompt:
               break

          formatted = f"<usr> {prompt} <bot>"
          ids = tokenizer.encode(formatted)
          if not ids:
               print("(no tokens from the prompt are in the vocabulary)")
               continue

          if len(ids) >= model.block_size:
               ids =  ids[-(model.block_size -1):]

          idx = torch.tensor([ids], dtype=torch.long, device=device)
          out = model.generate(idx, max_new_tokens, stop_ids=stop_ids)[0].tolist()

          generated_ids = out[len(ids):]
          if generated_ids and generated_ids[-1] in stop_ids:
               generated_ids = generated_ids[:-1]

          response = tokenizer.decode(generated_ids, skip_special_tokens=True)
          print(response)

def main():
     block_size = 64
     batch_size = 32

     d_model = 256
     N = 4
     h = 4
     dropout = 0.1

     print("Chat.py started")
     # Load data by batch size
     _, vocab_size = load_chatbot_data(block_size=block_size, batch_size=batch_size, device="cpu")


     model = build_gpt(vocab_size=vocab_size, block_size=block_size,
                         d_model=d_model, N=N, h=h, dropout=dropout)

     chat(model, tokenizer, checkpoint_path=ckpt_path, device="cpu")


if __name__ == "__main__":
    main()