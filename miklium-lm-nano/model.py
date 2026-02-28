import os
import re
import random
import json
import time
import numpy as np

word_level = True

np.random.seed(42)
random.seed(42)

training_data_path = 'assets/training_data/data.txt'
with open(training_data_path, 'r') as f:
    text = f.read()

# Tokenizer logic
def get_tokens(t):
    if word_level:
        # Regex to capture:
        # 1. Tags like <user>, <ai>, <think>, </think>, <eos>
        # 2. Words (including apostrophes)
        # 3. Punctuation mark (single chars)
        # 4. Whitespace (one or more spaces/newlines/tabs)
        return re.findall(r"<[^>]+>|[\w']+|[^\w\s\n]|\s+", t)
    else:
        # Character-level tokenizer (Default)
        return list(t)

all_text_tokens = get_tokens(text)
uchars = sorted(list(set(all_text_tokens)))
vocab_size = len(uchars) + 1 # +1 for BOS/EOS
BOS = len(uchars)
token_to_idx = {t: i for i, t in enumerate(uchars)}
idx_to_token = {i: t for i, t in enumerate(uchars)}
idx_to_token[BOS] = "<|endoftext|>"

# More robust data processing: concatenate into one long sequence
all_tokens = []
sections = text.split('<eos>')
for sec in sections:
    if not sec.strip(): continue
    all_tokens.append(BOS)
    # Re-attach <eos> for tokenization if it's the end of a section
    sec_content = sec.strip() + " <eos>"
    all_tokens.extend([token_to_idx[t] for t in get_tokens(sec_content) if t in token_to_idx])
all_tokens = np.array(all_tokens)

# Hyperparameters
n_layer = 4
n_embd = 64
block_size = 128
n_head = 4
head_dim = n_embd // n_head
batch_size = 4
learning_rate = 0.008

def init_matrix(nout, nin):
    # Xavier Init
    return np.random.randn(nout, nin) * np.sqrt(1.0 / nin)

state_dict = {
    'wte': init_matrix(vocab_size, n_embd),
    'wpe': init_matrix(block_size, n_embd),
    'lm_head': init_matrix(vocab_size, n_embd)
}
for i in range(n_layer):
    state_dict[f'layer{i}.attn_wq'] = init_matrix(n_embd, n_embd)
    state_dict[f'layer{i}.attn_wk'] = init_matrix(n_embd, n_embd)
    state_dict[f'layer{i}.attn_wv'] = init_matrix(n_embd, n_embd)
    state_dict[f'layer{i}.attn_wo'] = init_matrix(n_embd, n_embd)
    state_dict[f'layer{i}.mlp_fc1'] = init_matrix(4 * n_embd, n_embd)
    state_dict[f'layer{i}.mlp_fc2'] = init_matrix(n_embd, 4 * n_embd)

params = {k: v for k, v in state_dict.items()}
grads = {k: np.zeros_like(v) for k, v in params.items()}

def get_readable_params(count):
    if count >= 1e6: return f"{count/1e6:.1f}M"
    if count >= 1e3: return f"{count/1e3:.1f}K"
    return str(count)

total_params_count = sum(p.size for p in params.values())
readable_count = get_readable_params(total_params_count)
print(f"Training miklium-lm-nano ({readable_count} params) with NumPy...")

def rmsnorm_fwd(x):
    ms = np.mean(x**2, axis=-1, keepdims=True)
    scale = (ms + 1e-5)**-0.5
    return x * scale, ms, scale

def rmsnorm_bwd(dy, x, ms, scale):
    n = x.shape[-1]
    # Correct RMSNorm backward
    dscale = np.sum(dy * x, axis=-1, keepdims=True)
    dx = (dy * scale) - (x * scale**3 * dscale / n)
    return dx

def forward(tokens):
    T = len(tokens)
    idx = np.arange(T)
    x = params['wte'][tokens] + params['wpe'][idx]
    
    cache = []
    for i in range(n_layer):
        # Attention
        x_norm1, ms1, sc1 = rmsnorm_fwd(x)
        q = x_norm1 @ params[f'layer{i}.attn_wq'].T
        k = x_norm1 @ params[f'layer{i}.attn_wk'].T
        v = x_norm1 @ params[f'layer{i}.attn_wv'].T
        
        q = q.reshape(T, n_head, head_dim).transpose(1, 0, 2)
        k = k.reshape(T, n_head, head_dim).transpose(1, 0, 2)
        v = v.reshape(T, n_head, head_dim).transpose(1, 0, 2)
        
        att = (q @ k.transpose(0, 2, 1)) / (head_dim**0.5)
        mask = np.triu(np.ones((T, T)), k=1) * -1e10
        att = att + mask
        
        att_max = np.max(att, axis=-1, keepdims=True)
        exp_att = np.exp(att - att_max)
        probs = exp_att / (np.sum(exp_att, axis=-1, keepdims=True) + 1e-10)
        
        y_attn_heads = (probs @ v).transpose(1, 0, 2).reshape(T, n_embd)
        y_out = y_attn_heads @ params[f'layer{i}.attn_wo'].T
        x = x + y_out
        
        # MLP
        x_norm2, ms2, sc2 = rmsnorm_fwd(x)
        h = x_norm2 @ params[f'layer{i}.mlp_fc1'].T
        h_relu = np.maximum(0, h)
        y_mlp = h_relu @ params[f'layer{i}.mlp_fc2'].T
        x = x + y_mlp
        
        cache.append((x_norm1, ms1, sc1, q, k, v, probs, y_attn_heads, x_norm2, ms2, sc2, h, h_relu))
        
    logits = x @ params['lm_head'].T
    return logits, cache, x

def backward(tokens, logits, cache, x_final):
    T = len(tokens)
    targets = tokens[1:]
    logits_target = logits[:-1]
    
    # Softmax
    shift_logits = logits_target - np.max(logits_target, axis=-1, keepdims=True)
    exps = np.exp(shift_logits)
    probs = exps / (np.sum(exps, axis=-1, keepdims=True) + 1e-10)
    
    loss = -np.mean(np.log(probs[np.arange(T-1), targets] + 1e-10))
    dlogits = probs.copy()
    dlogits[np.arange(T-1), targets] -= 1
    dlogits /= (T-1)
    
    # Gradient for lm_head
    grads['lm_head'] += dlogits.T @ x_final[:-1]
    dx = dlogits @ params['lm_head']
    dx_full = np.zeros((T, n_embd))
    dx_full[:-1] = dx
    dx = dx_full
    
    for i in reversed(range(n_layer)):
        x_norm1, ms1, sc1, q, k, v, p, y_attn_h, x_norm2, ms2, sc2, h, h_relu = cache[i]
        
        # dMLP
        dy_mlp = dx
        grads[f'layer{i}.mlp_fc2'] += dy_mlp.T @ h_relu
        dh_relu = dy_mlp @ params[f'layer{i}.mlp_fc2']
        dh = dh_relu * (h > 0)
        grads[f'layer{i}.mlp_fc1'] += dh.T @ x_norm2
        dx_norm2 = dh @ params[f'layer{i}.mlp_fc1']
        dx += rmsnorm_bwd(dx_norm2, x_norm2, ms2, sc2)
        
        # dAttn
        dy_out = dx
        grads[f'layer{i}.attn_wo'] += dy_out.T @ y_attn_h
        dy_attn = dy_out @ params[f'layer{i}.attn_wo']
        
        dy_attn_v = dy_attn.reshape(T, n_head, head_dim).transpose(1, 0, 2)
        dp = dy_attn_v @ v.transpose(0, 2, 1) # (H, T, T)
        dv = p.transpose(0, 2, 1) @ dy_attn_v # (H, T, D)
        
        # dsoftmax
        datt = p * (dp - np.sum(dp * p, axis=-1, keepdims=True))
        datt /= (head_dim**0.5)
        
        dq = datt @ k # (H, T, D)
        dk = datt.transpose(0, 2, 1) @ q # (H, T, D)
        
        dq = dq.transpose(1, 0, 2).reshape(T, n_embd)
        dk = dk.transpose(1, 0, 2).reshape(T, n_embd)
        dv = dv.transpose(1, 0, 2).reshape(T, n_embd)
        
        grads[f'layer{i}.attn_wq'] += dq.T @ x_norm1
        grads[f'layer{i}.attn_wk'] += dk.T @ x_norm1
        grads[f'layer{i}.attn_wv'] += dv.T @ x_norm1
        
        dx_norm1 = dq @ params[f'layer{i}.attn_wq'] + dk @ params[f'layer{i}.attn_wk'] + dv @ params[f'layer{i}.attn_wv']
        dx += rmsnorm_bwd(dx_norm1, x_norm1, ms1, sc1)
        
    np.add.at(grads['wte'], tokens, dx)
    np.add.at(grads['wpe'], np.arange(T), dx)
    return loss

# Adam
m = {k: np.zeros_like(v) for k, v in params.items()}
v_adam = {k: np.zeros_like(v) for k, v in params.items()}
beta1, beta2, eps = 0.9, 0.95, 1e-8

num_steps = 5000
start_time = time.time()

for step in range(num_steps):
    step_loss = 0
    # Batching
    for _ in range(batch_size):
        start_idx = np.random.randint(0, len(all_tokens) - block_size)
        tokens = all_tokens[start_idx : start_idx + block_size]
        
        logits, cache, x_final = forward(tokens)
        step_loss += backward(tokens, logits, cache, x_final) / batch_size
    
    # Optimizer step
    lr_t = learning_rate * (1.0 - step / num_steps) # Linear decay
    for k in params:
        # Gradient clipping
        np.clip(grads[k], -5.0, 5.0, out=grads[k])
        
        m[k] = beta1 * m[k] + (1 - beta1) * grads[k]
        v_adam[k] = beta2 * v_adam[k] + (1 - beta2) * grads[k]**2
        m_hat = m[k] / (1 - beta1**(step + 1))
        v_hat = v_adam[k] / (1 - beta2**(step + 1))
        params[k] -= lr_t * m_hat / (np.sqrt(v_hat) + eps)
        grads[k].fill(0)
    
    if (step + 1) % 10 == 0 or step == 0:
        elapsed = time.time() - start_time
        steps_done = step + 1
        eta_sec = (elapsed / steps_done) * (num_steps - steps_done)
        eta_fmt = f"{int(eta_sec//3600):02d}:{int((eta_sec%3600)//60):02d}:{int(eta_sec%60):02d}"
        print(f"step {steps_done:4d} / {num_steps:4d} | loss {step_loss:.4f} | ETA: {eta_fmt}", end='\r')

# Save model
os.makedirs('website', exist_ok=True)
save_path = f"website/miklium-lm-nano_{readable_count}.miklium_model"
model_data = {
    'vocab': uchars,
    'idx_to_token': idx_to_token,
    'params': {k: v.tolist() for k, v in params.items()},
    'n_layer': n_layer, 'n_embd': n_embd, 'block_size': block_size, 'n_head': n_head
}
with open(save_path, 'w') as f:
    json.dump(model_data, f)

def generate(prompt, length=500, temp=0.5):
    prompt_tokens = get_tokens(prompt)
    tokens = [BOS] + [token_to_idx[t] for t in prompt_tokens if t in token_to_idx]
    
    start_offset = len(tokens)
    for _ in range(length):
        ctx = tokens[-block_size:]
        logits, _, _ = forward(np.array(ctx))
        logits_last = logits[-1] / (temp + 1e-6)
        exp_l = np.exp(logits_last - np.max(logits_last))
        probs = exp_l / np.sum(exp_l)
        next_token = np.random.choice(len(probs), p=probs)
        if next_token == BOS: break
        tokens.append(next_token)
    
    out = ""
    for t in tokens[start_offset:]:
        if t == BOS: break
        out += idx_to_token.get(t, "")
    return out

print("\n\n--- Training Complete ---")
for p in ["<user> Hello!", "<user> What is the capital of France?", "<user> Why do we yawn?"]:
    print(f"Prompt: {p}\nResponse: {generate(p, length=512, temp=0.4)}\n")