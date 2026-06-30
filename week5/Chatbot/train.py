import time, datetime
import torch
import torch.nn as nn

from dataset import tokenizer, load_chatbot_data
from model import build_gpt


@torch.no_grad()
def estimate_loss(model, get_batch, eval_iters= 20):
  """Average loss over several batches, with dropout off."""
  model.eval()
  # {"train": 평균loss, "val": 평균loss} 형태의 딕셔너리를 한 번에 생성
  out = {
    s: sum(model(*get_batch(s))[1].item() for _ in range(eval_iters)) / eval_iters
        # get_batch(s) -> (x, y) 튜플 -> model(*get_batch(s)) == model(x, y)
        # model(x, y) -> (logits, loss) 튜플 -> [1] 로 loss만 추출 -> .item()으로 python 숫자로 변환
        # 이 과정을 eval_iters 20번 반복해서 평균 -> 배치 하나만 보고 판단하면 노이즈가 크므로 여러 번 측정해서 평균냄
         for s in ("train", "val")
      }
  model.train()
  return out

def train(model, get_batch, device, lr=3e-4, steps=5000, eval_interval=100,
          decode=None, save_path="mini_gpt.pt"):
  """
  model          : build_gpt()로 만든 Transformer
  get_batch      : split('train'/'val')을 인자로 받아 (x, y) 텐서를 반환하는 함수
  device         : 'cuda' 또는 'cpu'
  lr             : 학습률
  steps          : 전체 학습 스텝 수
  eval_interval  : 몇 step마다 train/val loss를 측정해서 출력할지
  decode         : 토큰 id 리스트 -> 문자열 (샘플 출력용, 없으면 토큰 id를 그대로 출력)
  save_path      : 학습된 가중치를 저장할 파일 경로
  """
  model.to(device)
  model.train()
  # 모델 파라미터 총 개수를 천 단위 구분기호와 함께 출력
  print(f"{sum(p.numel() for p in model.parameters()):,} parameters, device={device}")

  opt = torch.optim.AdamW(model.parameters(), lr=lr)

  start = time.time()
  for step in range(steps):
    x, y = get_batch("train")  # x,y : (batch_size, block_size)
    _, loss = model(x,y)  # forward
    opt.zero_grad()
    loss.backward()
    opt.step()

    if step % eval_interval == 0 or step == steps -1:
      est = estimate_loss(model, get_batch) # train/val 평균 loss 측정
      sec = time.time()-start
      strtime = str(datetime.timedelta(seconds=sec)).split(".")[0]
      print(f"step {step:5d}/{steps} train {est['train']:.3f} val {est['val']:.3f} time {strtime}", flush=True)

  torch.save(model.state_dict(), save_path)
  print("saved weights to {save_path}")

  # 학습 끝난 후 평가 모드. 텍스트 생성 데모
  model.eval()
  prompt = torch.zeros((1,1), dtype=torch.long, device=device) # start token (token id 0)
  print("\n--- sample ---")
  # generate 500 tokens
  generated = model.generate(prompt, 500)[0].tolist()
  # decode 함수가 주어졌을 경우, 사람이 읽을 텍스트로 변환.
  print(decode(generated) if decode is not None else generated)


def decode(token_ids):
  return tokenizer.decode(token_ids)


if __name__ == "__main__":

  #HyperParameters
  block_size = 64
  batch_size = 32

  d_model = 256
  N = 4
  h = 4
  dropout = 0.1
  device = "cuda" if torch.cuda.is_available() else "cpu"
  print(f"selected device: {device}")
  # Load data by batch size
  get_batch, vocab_size = load_chatbot_data(block_size=block_size, batch_size=batch_size, device=device)
  print(f"vocab size: {vocab_size}")
  # Create model(from scratch)
  model = build_gpt(vocab_size=vocab_size, block_size=block_size,
                      d_model=256, N=4, h=4, dropout=0.1)
  
  # TRAIN
  #train(model, get_batch, device, lr=3e-4, steps=4000, eval_interval=100, decode=decode)

  