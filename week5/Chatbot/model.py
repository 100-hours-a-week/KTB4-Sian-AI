import torch
import torch.nn as nn
import math

#int id -> vector
#d_model : dimension of vector
#vocab_size : how many words in vocabulary
class InputEmbeddings(nn.Module):
    def __init__(self, vocab_size:int, d_model:int):
        super().__init__()
        self.d_model = d_model
        self.vocab_size = vocab_size
        self.embedding = nn.Embedding(vocab_size, d_model)

    def forward(self, x):
        return self.embedding(x) * math.sqrt(self.d_model)

class PositionalEncoding(nn.Module):
    def __init__(self, d_model:int, block_size:int, dropout: float) -> None:
        super().__init__()
        self.d_model = d_model
        self.block_size = block_size
        self.dropout = nn.Dropout(dropout)

        # Create a matrix of shape (block_size, d_model)
        pe = torch.zeros(block_size, d_model)
         # Create a vector of shape (block_size, 1)
        position = torch.arange(0, block_size, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0,d_model, 2).float()* -(math.log(10000.0)/d_model))
        #Apply the sin to even positions
        pe[:, 0::2] = torch.sin(position * div_term)
        #Apply the cosin to odd positions
        pe[:, 1::2] = torch.cos(position * div_term)

        pe = pe.unsqueeze(0) # (1, block_size, d_model)
        # keep inside model not as parameter but want to save
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + (self.pe[:, :x.shape[1], :]).requires_grad_(False)
        return self.dropout(x)

class LayerNormalization(nn.Module):
    def __init__(self, eps: float = 1e-6) -> None: # 1e-6 == 10**-6
        super().__init__()
        self.eps = eps
        self.alpha = nn.Parameter(torch.ones(1)) # Multiplied
        self.bias = nn.Parameter(torch.zeros(1)) # Added

    def forward(self, x):
        mean = x.mean(dim = -1, keepdim=True)
        std = x.std(dim = -1, keepdim=True)
        return self.alpha * (x-mean)/ (std+self.eps) + self.bias

class FeedForwardBlock(nn.Module):
    def __init__(self, d_model: int, d_ff:int, dropout: float) -> None:
        super().__init__()
        self.linear_1 = nn.Linear(d_model, d_ff) # W1 and B1
        self.dropout = nn.Dropout(dropout)
        self.linear_2 = nn.Linear(d_ff, d_model) # W2 and B2

    def forward(self, x):
        # (Batch, block_size, d_model) --> (Batch, block_size, d_ff) --> (Batch,block_size, d_model)
        return self.linear_2(self.dropout(torch.relu(self.linear_1(x))))

class MultiHeadAttentionBlock(nn.Module):
    def __init__(self, d_model:int, h: int, dropout:float) -> None:
        super().__init__()
        self.d_model = d_model
        self.h = h
        assert d_model % h == 0, "d_model is not divisible by h"

        self.d_k = d_model // h
        self.w_q = nn.Linear(d_model, d_model) # wq
        self.w_k = nn.Linear(d_model, d_model) # wk
        self.w_v = nn.Linear(d_model, d_model) # wv
        # d_k = d_v
        self.w_o = nn.Linear(d_model, d_model) # wo
        self.dropout = nn.Dropout(dropout)

    @staticmethod
    def attention(query, key, value, mask, dropout: nn.Dropout):
        d_k = query.shape[-1]

        # (Batch, h, block_size, d_k) --> (Batch, h, block_size, block_size)
        attention_scores = (query @ key.transpose(-2,-1)) / math.sqrt(d_k)
        # Before softmax , Apply Mask
        if mask is not None:
            attention_scores.masked_fill_(mask ==0, -1e9)
        attention_scores  = attention_scores.softmax(dim = -1) # (Batch, h, block_size, block_size)
        if dropout is not None:
            attention_scores = dropout(attention_scores)

        return (attention_scores @ value), attention_scores # attention_scores for visualizing
                #(Batch, h, block_size, d_k)

    def forward(self, q, k, v, mask):
        query = self.w_q(q) # (Batch, block_size, d_model) --> (Batch, block_size, d_model)
        key = self.w_k(k)   # (Batch, block_size, d_model) --> (Batch, block_size, d_model)
        value = self.w_v(v) # (Batch, block_size, d_model) --> (Batch, block_size, d_model)

        # Divide to Multi head
        # (Batch, block_size, d_model) --> (Batch, block_size, h, d_k) --> (Batch, h, block_size, d_k)
        # We want Head to watch (block_size, d_k)
        query = query.view(query.shape[0], query.shape[1], self.h, self.d_k).transpose(1,2)
        key = key.view(key.shape[0], key.shape[1], self.h, self.d_k).transpose(1,2)
        value = value.view(value.shape[0], value.shape[1], self.h, self.d_k).transpose(1,2)

        x, self.attention_scores = MultiHeadAttentionBlock.attention(query, key, value, mask, self.dropout)

        # (Batch, h, block_size, d_k) --> (Batch, block_size, h, d_k) --> (Batch, block_size, d_model) ##**(d_model = h*d_k)
        x = x.transpose(1,2).contiguous().view(x.shape[0], -1, self.h * self.d_k)

        # (Batch, block_size,d_model ) --> (Batch, block_size, d_model )
        return self.w_o(x)

class ResidualConnection(nn.Module):
    def __init__(self, dropout: float) -> None:
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        self.norm = LayerNormalization()

    def forward(self, x, sublayer):
        return x + self.dropout(sublayer(self.norm(x))) # 논문과 다르게 sublayer를 나중에 적용함. 대부분의 코드가 그래서

class EncoderBlock(nn.Module):
    def __init__(self, self_attention_block: MultiHeadAttentionBlock, feed_forward_block : FeedForwardBlock, dropout: float):
        super().__init__()
        self.self_attention_block = self_attention_block
        self.feed_forward_block = feed_forward_block
        self.residual_connections = nn.ModuleList([ResidualConnection(dropout) for _ in range(2)])

    def forward(self, x, src_mask):
        x = self.residual_connections[0](x, lambda x: self.self_attention_block(x,x,x, src_mask))
        x = self.residual_connections[1](x, self.feed_forward_block)
        return x

class Encoder(nn.Module):
    def __init__(self, layers: nn.ModuleList) -> None:
        super().__init__()
        self.layers = layers
        self.norm = LayerNormalization()

    def forward(self, x, mask):
        for layer in self.layers:
            x = layer(x, mask)
        return self.norm(x)

# 인코더-디코더 구조 모델에서의 디코더 블록 (사용하지 않음)
class DecoderBlock(nn.Module):
    def __init__(self, self_attention_block: MultiHeadAttentionBlock,
                 cross_attention_block:MultiHeadAttentionBlock,
                 feed_forward_block: FeedForwardBlock, dropout: float)->None:
        super().__init__()
        self.self_attention_block = self_attention_block
        self.cross_attention_block = cross_attention_block
        self.feed_forward_block = feed_forward_block
        self.residual_connections = nn.ModuleList([ResidualConnection(dropout) for _ in range(3)])

    def forward(self, x, encoder_output, src_mask, tgt_mask):
        # source language, target language
        x = self.residual_connections[0](x, lambda x: self.self_attention_block(x,x,x, tgt_mask))
        x = self.residual_connections[1](x, lambda x: self.cross_attention_block(x,encoder_output, encoder_output, src_mask))
        x = self.residual_connections[2](x, self.feed_forward_block)
        return x

class Decoder(nn.Module):
    def __init__(self, layers:nn.ModuleList)->None:
        super().__init__()
        self.layers = layers
        self.norm = LayerNormalization()

    def forward(self, x, encoder_output, src_mask, tgt_mask):
        for layer in self.layers:
            x = layer(x, encoder_output, src_mask, tgt_mask)
        return self.norm(x)

# Last layer : project into vocab_size
class ProjectionLayer(nn.Module):
    def __init__(self, d_model:int, vocab_size:int):
        super().__init__()
        self.proj = nn.Linear(d_model, vocab_size)

    def forward(self,x):
        # (Batch, block_size, d_model) --> (Batch, block_size, vocab_size)
        return self.proj(x) # torch.log_softmax(self.proj(x), dim= -1) 수정 logit계산을 위해 log_softmax 제거
                # raw logits 반환
### Sian =======================================================================================
class GPTDecoderBlock(nn.Module):
    """ 원래 DecoderBlock과 달리 cross-attention 없는 버전.
    self-attention(causal mask) + feed-forward만 사용 """
    def __init__(self,
                 self_attention_block:MultiHeadAttentionBlock,
                 feed_forward_block: FeedForwardBlock, dropout: float) -> None:
        super().__init__()
        self.self_attention_block = self_attention_block
        self.feed_forward_block = feed_forward_block
        self.residual_connections = nn.ModuleList([ResidualConnection(dropout) for _ in range(2)])

    def forward(self, x, tgt_mask):
        x = self.residual_connections[0](x, lambda x: self.self_attention_block(x,x,x, tgt_mask))
        x = self.residual_connections[1](x, self.feed_forward_block)
        return x

class GPTDecoder(nn.Module):
    def __init__(self, layers: nn.ModuleList):
        super().__init__()
        self.layers = layers
        self.norm = LayerNormalization()

    def forward(self, x, tgt_mask):
        for layer in self.layers:
            x = layer(x, tgt_mask)
        return self.norm(x)
    
class MiniGPT(nn.Module):
    # forward(x,y)를 호출하면 (logits, loss)를 반환하도록
    def __init__(self,
                 decoder: GPTDecoder,
                 tok_embed: InputEmbeddings,
                 pos_embed: PositionalEncoding,
                 projection_layer: ProjectionLayer,
                 block_size:int)-> None:
        super().__init__()
        self.decoder = decoder
        self.tok_embed = tok_embed
        self.pos_embed = pos_embed
        self.projection_layer = projection_layer
        self.block_size = block_size

        #######
        # causal mask buffer에 저장.
        mask = torch.tril(torch.ones(block_size, block_size)).unsqueeze(0).unsqueeze(0)
        self.register_buffer('causal_mask', mask) # (1,1, block_size, block_size)

        # initialize parameter
        # 모델의 모든 가중치(weight)를 처음 학습 시작 전에 어떤 값으로 채워둘지 정하는 부분
        # 없어도 동작하지만
        """ GPT 논문/구현체들은 경험적으로 표준편차 0.02짜리 정규분포로 초기화하면 학습이 안정적으로 잘 된다는 걸 발견해서,
        이게 거의 표준 관례가 됐습니다 (GPT-2 논문에서 유래)
        """
        self.apply(self._init_weights)

    def _init_weights(self, module):
        # GPT류 모델의 초기화 방식: Linear/Embedding: normal분포, LayerNorm계열은 건드리지 않고 그대로)
        if isinstance(module, nn.Linear): # Linear 층이면 가중치는 정규분포, bias = 0
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding): # 임베딩 테이블도 가중치는 정규분포, bias = 0
            nn.init.normal_(module.weight, mean=0.0, std=0.02)



    def forward(self, idx, targets=None): # x: idx, y: targets
        # idx, targets : (Batch, block_size)
        B, T = idx.shape
        x_tok_emb = self.tok_embed(idx) # (Batch, block_size)->(Batch, block_size, d_model)
        x = self.pos_embed(x_tok_emb) #(Batch, block_size, d_model)->(Batch, block_size, d_model)

        tgt_mask = self.causal_mask[:,:,:T,:T] # (1,1,T,T)
        x = self.decoder(x, tgt_mask) # (Batch, block_size, d_model)

        logits = self.projection_layer(x)
        # 주의: ProjectionLayer.forward는 log_softmax까지 적용하지만,
        # cross_entropy는 log_softmax 안 된 raw logits를 받아야 하므로 .proj()만 직접 호출
        # => projection_layer 수정

        loss = None
        if targets is not None:
            loss = nn.functional.cross_entropy(
                logits.view(-1, logits.size(-1)),   #(B*T, vocab_size)
                targets.view(-1)                    #(B*T, )
            )
        return logits, loss
    '''
    @torch.no_grad()
    def generate(self, idx, max_new_tokens):
        self.eval()
        for _ in range(max_new_tokens):
            logits, _ = self(idx[:, -self.block_size:]) # block_size 넘으면 뒤에서부터 자르기
            probs = torch.softmax(logits[:, -1, :], dim=-1) # 마지막 타임스텝 분포만 사용
            idx = torch.cat([idx, torch.multinomial(probs, 1)], dim=1)
        return idx
    '''
    @torch.no_grad()
    def generate(self, idx, max_new_tokens, stop_ids=None):
        self.eval()

        # stop_ids 추가
        stop_ids = set(stop_ids) if stop_ids else set()

        for _ in range(max_new_tokens):
            logits, _ = self(idx[:, -self.block_size:]) # block_size 넘으면 뒤에서부터 자르기
            probs = torch.softmax(logits[:, -1, :], dim=-1) # 마지막 타임스텝 분포만 사용
            next_id = torch.multinomial(probs, 1)
            idx = torch.cat([idx, next_id], dim=1)

            # batch_size=1 가정: stop 토큰이 나오면 즉시 멈춤
            if stop_ids and next_id.item() in stop_ids:
                break

        return idx
    
def build_gpt(vocab_size: int, block_size:int, d_model:int=384, N:int=6, h:int=6,
              dropout:float=0.1, d_ff:int = None) -> MiniGPT:
    # 디코더 전용 GPT 스타일 모델 생성
    if d_ff is None: # dimension of feed forward
        d_ff = 4 * d_model

    tok_embed = InputEmbeddings(vocab_size, d_model)
    pos_embed = PositionalEncoding(d_model, block_size, dropout)

    decoder_blocks = []
    for _ in range(N):
        self_attention_block = MultiHeadAttentionBlock(d_model,h,dropout)
        feed_forward_block = FeedForwardBlock(d_model, d_ff, dropout)
        decoder_blocks.append(GPTDecoderBlock(self_attention_block, feed_forward_block, dropout))

    decoder = GPTDecoder(nn.ModuleList(decoder_blocks))
    projection_layer = ProjectionLayer(d_model, vocab_size)

    model = MiniGPT(decoder, tok_embed,pos_embed, projection_layer,block_size)
    return model




###### Encoder-Decoder###  =======================================================================================    
class Transformer(nn.Module):
    def __init__(self, encoer:Encoder, decoder:Decoder, src_embed: InputEmbeddings, 
                 tgt_embed: InputEmbeddings, src_pos: PositionalEncoding, 
                 tgt_pos: PositionalEncoding, projection_layer: ProjectionLayer):
        super().__init__()
        self.encoder = Encoder
        self.decoder = Decoder
        self.src_embed = src_embed
        self.tgt_embed = tgt_embed
        self.src_pos = src_pos
        self.tgt_pos = tgt_pos
        self.projection_layer = projection_layer

    def encode(self, src, src_mask):
        # (Batch, seq_len, d_model)
        src = self.src_embed(src)
        src = self.src_pos(src)
        return self.encoder(src, src_mask)

    def decode(self, encoder_output, src_mask, tgt, tgt_mask ):
        # (Batch, seq_len, d_model)
        tgt = self.tgt_embed(tgt)
        tgt = self.tgt_pos(tgt)
        return self.decoder(tgt, encoder_output, src_mask, tgt_mask)
        
    def project(self, x):
        # (Batch, seq_len, vocab_size)
        return self.projection_layer(x)
    
def build_transformer(src_vocab_size:int, tgt_vocab_size:int, src_seq_len:int, tgt_seq_len:int, d_model:int = 512, N:int=6, h:int=8, dropout:float=0.1, d_ff:int = 2048):
    # Create the embedding layers
    src_embed = InputEmbeddings(src_vocab_size, d_model)
    tgt_embed = InputEmbeddings(tgt_vocab_size, d_model)

    # Create the positional encoding Layers
    src_pos = PositionalEncoding(d_model, src_seq_len, dropout)
    tgt_pos = PositionalEncoding(d_model, tgt_seq_len, dropout)

    #Create the encoder blocks
    encoder_blocks = []
    for _ in range(N):
        encoder_self_attention_block = MultiHeadAttentionBlock(d_model, h, dropout)
        feed_forward_block = FeedForwardBlock(d_model, d_ff, dropout)
        encoder_block = EncoderBlock(encoder_self_attention_block, feed_forward_block, dropout)
        encoder_blocks.append(encoder_block)

    # Create the decoder blocks
    decoder_blocks = []
    for _ in range(N):
        decoder_self_attention_block = MultiHeadAttentionBlock(d_model, h, dropout)
        decoder_cross_attention_block = MultiHeadAttentionBlock(d_model, h, dropout)
        feed_forward_block = FeedForwardBlock(d_model, d_ff, dropout)
        decoder_block = DecoderBlock(decoder_self_attention_block, decoder_cross_attention_block, feed_forward_block, dropout)
        decoder_blocks.append(decoder_block)

    # Create the encoder and the decoder
    encoder = Encoder(nn.ModuleList(encoder_blocks))
    decoder = Decoder(nn.ModuleList(decoder_blocks))

    # Create the projection layer
    projection_layer = ProjectionLayer(d_model, tgt_vocab_size)

    # Create the transformer
    transformer = Transformer(encoder, decoder, src_embed, tgt_embed, src_pos, tgt_pos, projection_layer)

    # Initialize the parameters
    for p in transformer.parameters():
        if p.dim() > 1:
            nn.init.xavier_uniform_(p)

    return transformer
