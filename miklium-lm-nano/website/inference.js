class MikliumModel {
    constructor() {
        this.modelData = null;
        this.BOS = null;
        this.token_to_idx = {};
        this.idx_to_token = {};
        this.head_dim = 0;
    }

    async load(url) {
        console.log("Loading model from", url);
        const response = await fetch(url);
        this.modelData = await response.json();

        // Setup vocab
        this.BOS = this.modelData.vocab.length;
        this.modelData.vocab.forEach((t, i) => {
            this.token_to_idx[t] = i;
            this.idx_to_token[i] = t;
        });

        // Same logic as index.html
        this.idx_to_token[this.BOS] = "<|endoftext|>";
        this.head_dim = this.modelData.n_embd / this.modelData.n_head;
        console.log("Model loaded successfully, vocab size:", this.modelData.vocab.length);
    }

    getTokens(text) {
        // word_level=True equivalent in model.py
        const regex = /<[^>]+>|[\w']+|[^\w\s\n]|\s+/g;
        return text.match(regex) || [];
    }

    matmul(A, B, A_rows, A_cols, B_cols) {
        let out = new Float32Array(A_rows * B_cols);
        for (let i = 0; i < A_rows; i++) {
            for (let j = 0; j < B_cols; j++) {
                let sum = 0;
                for (let k = 0; k < A_cols; k++) {
                    sum += A[i * A_cols + k] * B[j][k];
                }
                out[i * B_cols + j] = sum;
            }
        }
        return out;
    }

    rmsnorm(x, T, C) {
        let out = new Float32Array(x.length);
        for (let i = 0; i < T; i++) {
            let sum_sq = 0;
            for (let j = 0; j < C; j++) {
                let val = x[i * C + j];
                sum_sq += val * val;
            }
            let ms = sum_sq / C;
            let scale = 1.0 / Math.sqrt(ms + 1e-5);
            for (let j = 0; j < C; j++) {
                out[i * C + j] = x[i * C + j] * scale;
            }
        }
        return out;
    }

    softmax(x) {
        let max_val = -Infinity;
        for (let i = 0; i < x.length; i++) {
            if (x[i] > max_val) max_val = x[i];
        }
        let exp_sum = 0;
        let exp_vals = new Float32Array(x.length);
        for (let i = 0; i < x.length; i++) {
            let e = Math.exp(x[i] - max_val);
            exp_vals[i] = e;
            exp_sum += e;
        }
        for (let i = 0; i < x.length; i++) {
            exp_vals[i] /= exp_sum;
        }
        return exp_vals;
    }

    forward(tokens) {
        const T = tokens.length;
        const C = this.modelData.n_embd;

        let x = new Float32Array(T * C);
        for (let i = 0; i < T; i++) {
            let tok_idx = tokens[i];
            let tok_emb = this.modelData.params.wte[tok_idx] || new Array(C).fill(0);
            let pos_emb = this.modelData.params.wpe[i] || new Array(C).fill(0);
            for (let j = 0; j < C; j++) {
                x[i * C + j] = tok_emb[j] + pos_emb[j];
            }
        }

        const L = this.modelData.n_layer;
        const n_head = this.modelData.n_head;
        const head_dim = this.head_dim;

        for (let l = 0; l < L; l++) {
            let x_norm = this.rmsnorm(x, T, C);

            let q_full = this.matmul(x_norm, this.modelData.params[`layer${l}.attn_wq`], T, C, C);
            let k_full = this.matmul(x_norm, this.modelData.params[`layer${l}.attn_wk`], T, C, C);
            let v_full = this.matmul(x_norm, this.modelData.params[`layer${l}.attn_wv`], T, C, C);

            let y_attn_heads = new Float32Array(T * C);

            for (let h = 0; h < n_head; h++) {
                for (let i = 0; i < T; i++) {
                    let row_att = new Float32Array(T).fill(-1e10);
                    for (let j = 0; j <= i; j++) {
                        let dot = 0;
                        for (let d = 0; d < head_dim; d++) {
                            dot += q_full[i * C + h * head_dim + d] * k_full[j * C + h * head_dim + d];
                        }
                        row_att[j] = dot / Math.sqrt(head_dim);
                    }
                    let row_probs = this.softmax(row_att);

                    for (let d = 0; d < head_dim; d++) {
                        let sum_v = 0;
                        for (let j = 0; j <= i; j++) {
                            sum_v += row_probs[j] * v_full[j * C + h * head_dim + d];
                        }
                        y_attn_heads[i * C + h * head_dim + d] = sum_v;
                    }
                }
            }

            let y_out = this.matmul(y_attn_heads, this.modelData.params[`layer${l}.attn_wo`], T, C, C);
            for (let i = 0; i < x.length; i++) { x[i] += y_out[i]; }

            let x_norm2 = this.rmsnorm(x, T, C);
            let h_val = this.matmul(x_norm2, this.modelData.params[`layer${l}.mlp_fc1`], T, C, 4 * C);

            for (let i = 0; i < h_val.length; i++) { h_val[i] = Math.max(0, h_val[i]); }

            let y_mlp = this.matmul(h_val, this.modelData.params[`layer${l}.mlp_fc2`], T, 4 * C, C);
            for (let i = 0; i < x.length; i++) { x[i] += y_mlp[i]; }
        }

        let vocab_size = this.modelData.vocab.length + 1;
        let logitsMatrix = this.matmul(x, this.modelData.params.lm_head, T, C, vocab_size);

        let last_logits = new Float32Array(vocab_size);
        for (let i = 0; i < vocab_size; i++) {
            last_logits[i] = logitsMatrix[(T - 1) * vocab_size + i];
        }

        return last_logits;
    }

    async generate(prompt, length = 100, temp = 0.5, callback = null) {
        let prompt_tokens = this.getTokens(prompt);
        let tokens = [this.BOS];
        for (let t of prompt_tokens) {
            if (this.token_to_idx.hasOwnProperty(t)) {
                tokens.push(this.token_to_idx[t]);
            }
        }

        let out = "";
        let max_ctx = this.modelData.block_size;

        for (let s = 0; s < length; s++) {
            let ctx = tokens.slice(-max_ctx);
            let logits = this.forward(ctx);

            let exps = new Float32Array(logits.length);
            let exp_sum = 0;
            let max_l = -Infinity;
            for (let i = 0; i < logits.length; i++) { if (logits[i] > max_l) max_l = logits[i]; }

            for (let i = 0; i < logits.length; i++) {
                let val = Math.exp((logits[i] - max_l) / (temp + 1e-6));
                exps[i] = val;
                exp_sum += val;
            }

            let rand = Math.random() * exp_sum;
            let accum = 0;
            let next_token = logits.length - 1;
            for (let i = 0; i < logits.length; i++) {
                accum += exps[i];
                if (rand < accum) {
                    next_token = i;
                    break;
                }
            }

            if (next_token === this.BOS) break;
            tokens.push(next_token);

            let text_chunk = this.idx_to_token[next_token] || "";
            out += text_chunk;

            if (callback) {
                // To prevent UI blocking, we yield occasionally or on every token.
                // We'll yield the new text chunk!
                await callback(text_chunk);
            }
        }
        return out;
    }
}
