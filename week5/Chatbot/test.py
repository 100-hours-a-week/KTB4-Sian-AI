
import torch
from datasets import load_dataset
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel

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

print(vocab_size)