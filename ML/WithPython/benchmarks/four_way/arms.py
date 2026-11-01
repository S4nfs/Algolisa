"""The four arms of the benchmark, behind one interface.

    logits(x)             parallel forward, (B,T) -> (B,T,V)
    train_loss(x, y)      the arm's own training objective -> (loss, stats)
    after_step()          per-step bookkeeping (RD-S4: EMA teacher)
    make_optimizer(lr)    shared AdamW recipe (RD-S4: the notebook's own optimizer)
    mixing_flops(B,T,tr)  analytic forward FLOPs of the sequence mixer (attention / FFT / scan)
    nll_stream(ids, ck)   exact per-position (NLL, top-1 correct) over an arbitrarily long stream
    prefill(x, ck)        consume a prompt -> (last logits, decode state)
    step(tok, state)      one decode step -> (logits, state); free of host syncs (graph-safe)

Parameter counts are matched to RD-S4 (1,721,760) within one percent:
    Transformer  d=192, 4 layers, 6 heads, RoPE, MLP 736
    S4           S4D-Lin, ZOH, d=192, 4 layers, 64 complex modes/channel, GLU, MLP 784
    Mamba        Mamba-1, d=188, 7 layers, expand 2, d_state 16, d_conv 4
    RD-S4        the notebook's RDS4LM, unmodified
    RD-S4 v2     the main notebook's RDS4LM (resonant prediction-error memory), unmodified
"""
import math

import torch
import torch.nn as nn
import torch.nn.functional as F

import common as C
from ssm_kernels import selective_scan, scan_fwd


def _nll_acc(logits, y):
    logits = logits.float()
    return F.cross_entropy(logits, y, reduction="none"), (logits.argmax(-1) == y)


class RMSNorm(nn.Module):
    def __init__(self, d, eps=1e-6):
        super().__init__()
        self.g = nn.Parameter(torch.ones(d))
        self.eps = eps

    def forward(self, x):
        # one fused kernel, numerically the same as g * x * rsqrt(mean(x^2) + eps); shared by every arm
        return F.rms_norm(x, self.g.shape, self.g, self.eps)


def _gpt_init(module, n_layers, resid_names):
    for name, p in module.named_parameters():
        if p.ndim >= 2 and ("emb" in name or name.endswith("weight")):
            std = 0.02 / math.sqrt(2 * n_layers) if any(r in name for r in resid_names) else 0.02
            nn.init.normal_(p, std=std)
        elif name.endswith("bias"):
            nn.init.zeros_(p)


class BaseArm(nn.Module):
    name = "base"
    precision = "fp32 (TF32 matmul)"

    def train_loss(self, x, y):
        ce = F.cross_entropy(self.logits(x).reshape(-1, self.vocab), y.reshape(-1))
        return ce, {"ce": ce.detach()}

    def after_step(self):
        pass

    def make_optimizer(self, lr):
        return C.make_optimizer(self, lr)

    @staticmethod
    def state_bytes(state):
        tot = 0
        for v in (state.values() if isinstance(state, dict) else state):
            if torch.is_tensor(v):
                tot += v.numel() * v.element_size()
            elif isinstance(v, (dict, list, tuple)):
                tot += BaseArm.state_bytes(v)
        return tot


# =============================================================================== Transformer
def _rope(x, cos, sin):
    h = x.shape[-1] // 2
    x1, x2 = x[..., :h], x[..., h:]
    cos, sin = cos.to(x.dtype), sin.to(x.dtype)
    return torch.cat([x1 * cos - x2 * sin, x1 * sin + x2 * cos], -1)


class TBlock(nn.Module):
    def __init__(self, d, n_heads, d_mlp):
        super().__init__()
        self.H, self.dh = n_heads, d // n_heads
        self.n1, self.n2 = RMSNorm(d), RMSNorm(d)
        self.qkv = nn.Linear(d, 3 * d, bias=False)
        self.o = nn.Linear(d, d, bias=False)
        self.fc = nn.Linear(d, d_mlp, bias=False)
        self.proj = nn.Linear(d_mlp, d, bias=False)

    def forward(self, x, cos, sin, cache=None):
        B, T, d = x.shape
        q, k, v = self.qkv(self.n1(x)).view(B, T, 3, self.H, self.dh).unbind(2)
        q, k, v = (t.transpose(1, 2) for t in (q, k, v))
        q, k = _rope(q, cos, sin), _rope(k, cos, sin)
        if cache is not None:
            cache[0][:, :, :T].copy_(k)
            cache[1][:, :, :T].copy_(v)
        a = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        x = x + self.o(a.transpose(1, 2).reshape(B, T, d))
        return x + self.proj(F.gelu(self.fc(self.n2(x))))

    def step(self, x, cos, sin, K, V, pos, mask):
        q, k, v = self.qkv(self.n1(x)).view(1, 1, 3, self.H, self.dh).unbind(2)
        q, k, v = (t.transpose(1, 2) for t in (q, k, v))
        q, k = _rope(q, cos, sin), _rope(k, cos, sin)
        K.index_copy_(2, pos.view(1), k.to(K.dtype))
        V.index_copy_(2, pos.view(1), v.to(V.dtype))
        # Explicit matmuls instead of the fused SDPA kernel: with one query the fused kernel
        # parallelises over 6 heads only, and was measured 11x slower at 128K. This form is
        # bandwidth-bound (reads K and V once), i.e. the Transformer's best case.
        s = (q.to(K.dtype) @ K.transpose(-1, -2)).float() * (self.dh ** -0.5)
        a = s.masked_fill(~mask, float("-inf")).softmax(-1).to(V.dtype) @ V
        x = x + self.o(a.transpose(1, 2).reshape(1, 1, -1))
        return x + self.proj(F.gelu(self.fc(self.n2(x))))


class TransformerArm(BaseArm):
    name = "Transformer"
    precision = ("bf16 autocast, bf16 KV cache; flash-attention prefill; bandwidth-bound matmul "
                 "decode attention (inference); fp32/TF32 (training)")

    def __init__(self, vocab, d=192, n_layers=4, n_heads=6, d_mlp=736, base=10000.0):
        super().__init__()
        self.vocab, self.d, self.n_layers = vocab, d, n_layers
        self.emb = nn.Embedding(vocab, d)
        self.blocks = nn.ModuleList([TBlock(d, n_heads, d_mlp) for _ in range(n_layers)])
        self.norm_f = RMSNorm(d)
        self.head = nn.Linear(d, vocab, bias=False)
        self.head.weight = self.emb.weight
        dh = d // n_heads
        self.register_buffer("inv_freq", 1.0 / base ** (torch.arange(0, dh, 2).float() / dh),
                             persistent=False)
        _gpt_init(self, n_layers, (".o.", ".proj."))

    def _cs(self, pos):
        f = pos.float().unsqueeze(-1) * self.inv_freq
        return f.cos(), f.sin()

    def logits(self, x):
        cos, sin = self._cs(torch.arange(x.shape[1], device=x.device))
        h = self.emb(x)
        for b in self.blocks:
            h = b(h, cos, sin)
        return self.head(self.norm_f(h))

    def mixing_flops(self, B, T, training):
        return self.n_layers * 2.0 * B * T * (T + 1) * self.d          # causal QK^T and AV

    @torch.no_grad()
    def nll_stream(self, ids, chunk=None):
        x, y = ids[:-1].view(1, -1), ids[1:]
        nll, ok = _nll_acc(self.logits(x)[0], y)
        return nll, ok

    # ---- decode with a pre-allocated bf16 KV cache (as served in production)
    @torch.no_grad()
    def prefill(self, x, chunk=None, extra=256):
        T = x.shape[1]
        L = T + extra
        H, dh = self.blocks[0].H, self.blocks[0].dh
        st = {"K": [torch.zeros(1, H, L, dh, device=x.device, dtype=torch.bfloat16)
                    for _ in self.blocks],
              "V": [torch.zeros(1, H, L, dh, device=x.device, dtype=torch.bfloat16)
                    for _ in self.blocks],
              "pos": torch.tensor(T, device=x.device), "T": T}
        ar = torch.arange(L, device=x.device)
        st["cos"], st["sin"] = self._cs(ar)
        st["ar"] = ar
        with torch.autocast("cuda", dtype=torch.bfloat16, cache_enabled=False):
            cos, sin = st["cos"][:T], st["sin"][:T]
            h = self.emb(x)
            for b, K, V in zip(self.blocks, st["K"], st["V"]):
                h = b(h, cos, sin, cache=(K, V))
            lg = self.head(self.norm_f(h[:, -1]))
        return lg.float(), st

    @torch.no_grad()
    def step(self, tok, st):
        pos = st["pos"]
        with torch.autocast("cuda", dtype=torch.bfloat16, cache_enabled=False):
            cos = st["cos"].index_select(0, pos.view(1))
            sin = st["sin"].index_select(0, pos.view(1))
            mask = (st["ar"] <= pos).view(1, 1, 1, -1)
            h = self.emb(tok.view(1, 1))
            for b, K, V in zip(self.blocks, st["K"], st["V"]):
                h = b.step(h, cos, sin, K, V, pos, mask)
            lg = self.head(self.norm_f(h)).view(1, -1)
        pos.add_(1)
        return lg.float(), st

    def decode_state_bytes(self, T):
        """KV cache actually holding T tokens, bf16."""
        return 2 * self.n_layers * T * self.d * 2


# =============================================================================== S4 (S4D)
class S4DCore(nn.Module):
    """S4D (Gu, Gupta, Goel, Re 2022): diagonal complex SSM, S4D-Lin init, ZOH discretisation.

    Written with the same interface as RD-S4's ResonantSSM (log_a, C, forward, step), so the
    notebook's exact chunked long-context routine `ssm_chunk` serves both LTI models and any
    difference between them is the model, not the long-context code path.
    """

    def __init__(self, H, N=64, dt_min=1e-3, dt_max=1e-1):
        super().__init__()
        self.log_dt = nn.Parameter(torch.rand(H) * (math.log(dt_max) - math.log(dt_min))
                                   + math.log(dt_min))
        self.C_ri = nn.Parameter(torch.view_as_real(torch.randn(H, N, dtype=torch.cfloat)).clone())
        self.log_A_real = nn.Parameter(torch.log(0.5 * torch.ones(H, N)))
        self.A_imag = nn.Parameter(math.pi * torch.arange(N).float().repeat(H, 1))
        self.D = nn.Parameter(torch.randn(H))

    def _A(self):
        return torch.complex(-torch.exp(self.log_A_real), self.A_imag)

    def log_a(self):
        return self._A() * torch.exp(self.log_dt).unsqueeze(-1)            # dt * A

    def C(self):
        """C with the ZOH input matrix folded in, so that h_t = a h_{t-1} + u_t."""
        A = self._A()
        return torch.view_as_complex(self.C_ri) * (torch.exp(self.log_a()) - 1.0) / A

    def forward(self, u):                                                  # (B,T,H) -> (B,T,H)
        T = u.shape[1]
        n = 2 * T
        la, Cb = self.log_a(), self.C()
        t = torch.arange(T, device=u.device, dtype=torch.float32)
        k = 2.0 * (Cb.unsqueeze(-1) * torch.exp(la.unsqueeze(-1) * t)).real.sum(1)
        y = torch.fft.irfft(torch.fft.rfft(u.transpose(1, 2), n=n) * torch.fft.rfft(k, n=n), n=n)[..., :T]
        return y.transpose(1, 2) + u * self.D

    @torch.no_grad()
    def step(self, u_t, h):
        h.mul_(torch.exp(self.log_a()).unsqueeze(0)).add_(u_t.unsqueeze(-1).to(h.dtype))
        return 2.0 * (self.C().unsqueeze(0) * h).real.sum(-1) + u_t * self.D


class S4Block(nn.Module):
    def __init__(self, d, d_mlp, N):
        super().__init__()
        self.n1, self.n2 = RMSNorm(d), RMSNorm(d)
        self.core = S4DCore(d, N)
        self.out = nn.Linear(d, 2 * d)               # the official 1x1 conv to 2H, then GLU
        self.fc = nn.Linear(d, d_mlp, bias=False)
        self.proj = nn.Linear(d_mlp, d, bias=False)

    def post(self, x, y):
        x = x + F.glu(self.out(F.gelu(y)), dim=-1)
        return x + self.proj(F.gelu(self.fc(self.n2(x))))

    def forward(self, x):
        return self.post(x, self.core(self.n1(x)))


class S4Arm(BaseArm):
    name = "S4"

    def __init__(self, vocab, ns, d=192, n_layers=4, N=64, d_mlp=784):
        super().__init__()
        self.vocab, self.d, self.n_layers, self.N = vocab, d, n_layers, N
        self._ssm_chunk = ns["ssm_chunk"]
        self.emb = nn.Embedding(vocab, d)
        self.blocks = nn.ModuleList([S4Block(d, d_mlp, N) for _ in range(n_layers)])
        self.norm_f = RMSNorm(d)
        self.head = nn.Linear(d, vocab, bias=False)
        self.head.weight = self.emb.weight
        _gpt_init(self, n_layers, (".out.", ".proj."))   # Linear/embedding only; S4D params keep their init

    def make_optimizer(self, lr):
        # the published S4 recipe: A and dt at min(lr, 1e-3) without weight decay
        return C.make_optimizer(self, lr, slow_keys=("log_dt", "log_A_real", "A_imag"), slow_lr=1e-3)

    def logits(self, x):
        h = self.emb(x)
        for b in self.blocks:
            h = b(h)
        return self.head(self.norm_f(h))

    def mixing_flops(self, B, T, training):
        n = 2 * T
        fft = C.fft_flops(2 * B * self.d + self.d, n) + 6.0 * B * self.d * (T + 1)
        kern = 8.0 * self.d * self.N * T
        return self.n_layers * (fft + kern)

    def init_state(self, B, dev):
        return [torch.zeros(B, self.d, self.N, dtype=torch.complex64, device=dev) for _ in self.blocks]

    @torch.no_grad()
    def _chunk(self, x, hs):
        h = self.emb(x)
        new = []
        for b, h0 in zip(self.blocks, hs):
            y, hT = self._ssm_chunk(b.core, b.n1(h), h0)
            h = b.post(h, y)
            new.append(hT)
        return h, new

    @torch.no_grad()
    def nll_stream(self, ids, chunk=8192):
        x, y = ids[:-1].view(1, -1), ids[1:]
        hs, out = self.init_state(1, ids.device), []
        for s in range(0, x.shape[1], chunk):
            h, hs = self._chunk(x[:, s:s + chunk], hs)
            out.append(_nll_acc(self.head(self.norm_f(h))[0], y[s:s + chunk]))
        return torch.cat([o[0] for o in out]), torch.cat([o[1] for o in out])

    @torch.no_grad()
    def prefill(self, x, chunk=8192):
        hs = self.init_state(1, x.device)
        for s in range(0, x.shape[1], chunk):
            h, hs = self._chunk(x[:, s:s + chunk], hs)
        return self.head(self.norm_f(h[:, -1])), {"h": hs}

    @torch.no_grad()
    def step(self, tok, st):
        h = self.emb(tok)
        for b, hs in zip(self.blocks, st["h"]):
            h = b.post(h, b.core.step(b.n1(h), hs))
        return self.head(self.norm_f(h)), st


# =============================================================================== Mamba
class MambaMixer(nn.Module):
    """Mamba-1 mixer (Gu and Dao 2023), initialised as in the reference implementation."""

    def __init__(self, d, n_layers, d_state=16, d_conv=4, expand=2,
                 dt_min=1e-3, dt_max=1e-1, dt_floor=1e-4):
        super().__init__()
        di = expand * d
        self.di, self.N, self.k = di, d_state, d_conv
        self.dt_rank = math.ceil(d / 16)
        self.in_proj = nn.Linear(d, 2 * di, bias=False)
        self.conv1d = nn.Conv1d(di, di, d_conv, groups=di, padding=d_conv - 1, bias=True)
        self.x_proj = nn.Linear(di, self.dt_rank + 2 * d_state, bias=False)
        self.dt_proj = nn.Linear(self.dt_rank, di, bias=True)
        self.out_proj = nn.Linear(di, d, bias=False)
        s = self.dt_rank ** -0.5
        nn.init.uniform_(self.dt_proj.weight, -s, s)
        dt = torch.exp(torch.rand(di) * (math.log(dt_max) - math.log(dt_min)) + math.log(dt_min))
        dt = dt.clamp(min=dt_floor)
        with torch.no_grad():
            self.dt_proj.bias.copy_(dt + torch.log(-torch.expm1(-dt)))      # softplus^-1
        self.A_log = nn.Parameter(torch.log(torch.arange(1, d_state + 1).float().repeat(di, 1)))
        self.D = nn.Parameter(torch.ones(di))
        nn.init.kaiming_uniform_(self.out_proj.weight, a=math.sqrt(5))
        with torch.no_grad():
            self.out_proj.weight /= math.sqrt(n_layers)                    # prenorm residual rescale

    def _ssm_inputs(self, xi):
        dt, Bm, Cm = self.x_proj(xi).split([self.dt_rank, self.N, self.N], dim=-1)
        return F.softplus(self.dt_proj(dt)), Bm, Cm, -torch.exp(self.A_log.float())

    def forward(self, x):
        L = x.shape[1]
        xi, z = self.in_proj(x).chunk(2, dim=-1)
        xi = F.silu(self.conv1d(xi.transpose(1, 2))[..., :L]).transpose(1, 2)
        dt, Bm, Cm, A = self._ssm_inputs(xi)
        return self.out_proj(selective_scan(xi, dt, A, Bm, Cm, self.D) * F.silu(z))

    @torch.no_grad()
    def chunk(self, x, st):
        xi, z = self.in_proj(x).chunk(2, dim=-1)
        xc = torch.cat([st["conv"], xi.transpose(1, 2)], dim=-1)
        st["conv"] = xc[..., -(self.k - 1):].contiguous()
        xi = F.silu(F.conv1d(xc, self.conv1d.weight, self.conv1d.bias, groups=self.di)).transpose(1, 2)
        dt, Bm, Cm, A = self._ssm_inputs(xi)
        y, st["h"] = scan_fwd(xi.contiguous(), dt.contiguous(), A.contiguous(), Bm.contiguous(),
                              Cm.contiguous(), self.D.float(), h0=st["h"])
        return self.out_proj(y * F.silu(z))

    @torch.no_grad()
    def step(self, x, st):
        xi, z = self.in_proj(x).chunk(2, dim=-1)
        win = torch.cat([st["conv"], xi.unsqueeze(-1)], dim=-1)
        st["conv"].copy_(win[..., 1:])
        xi = F.silu((win * self.conv1d.weight.squeeze(1)).sum(-1) + self.conv1d.bias)
        dt, Bm, Cm, A = self._ssm_inputs(xi)
        h = st["h"]
        h.mul_(torch.exp(dt.unsqueeze(-1) * A)).add_((dt * xi).unsqueeze(-1) * Bm.unsqueeze(1))
        y = (h * Cm.unsqueeze(1)).sum(-1) + self.D * xi
        return self.out_proj(y * F.silu(z))


class MambaBlock(nn.Module):
    def __init__(self, d, n_layers):
        super().__init__()
        self.norm = RMSNorm(d)
        self.mixer = MambaMixer(d, n_layers)

    def forward(self, x):
        return x + self.mixer(self.norm(x))


class MambaArm(BaseArm):
    name = "Mamba"
    precision = "fp32 (TF32 matmul); selective scan in a fused Triton kernel"

    def __init__(self, vocab, d=188, n_layers=7):
        super().__init__()
        self.vocab, self.d, self.n_layers = vocab, d, n_layers
        self.emb = nn.Embedding(vocab, d)
        self.blocks = nn.ModuleList([MambaBlock(d, n_layers) for _ in range(n_layers)])
        self.norm_f = RMSNorm(d)
        self.head = nn.Linear(d, vocab, bias=False)
        self.head.weight = self.emb.weight
        nn.init.normal_(self.emb.weight, std=0.02)

    def logits(self, x):
        h = self.emb(x)
        for b in self.blocks:
            h = b(h)
        return self.head(self.norm_f(h))

    def mixing_flops(self, B, T, training):
        m = self.blocks[0].mixer
        return self.n_layers * 7.0 * B * T * m.di * m.N        # dtA, dt*x, *B, a*h, +, *C, sum

    def init_state(self, B, dev):
        m = self.blocks[0].mixer
        return [{"conv": torch.zeros(B, m.di, m.k - 1, device=dev),
                 "h": torch.zeros(B, m.di, m.N, device=dev)} for _ in self.blocks]

    @torch.no_grad()
    def _chunk(self, x, sts):
        h = self.emb(x)
        for b, st in zip(self.blocks, sts):
            h = h + b.mixer.chunk(b.norm(h), st)
        return h

    @torch.no_grad()
    def nll_stream(self, ids, chunk=8192):
        x, y = ids[:-1].view(1, -1), ids[1:]
        sts, out = self.init_state(1, ids.device), []
        for s in range(0, x.shape[1], chunk):
            h = self._chunk(x[:, s:s + chunk], sts)
            out.append(_nll_acc(self.head(self.norm_f(h))[0], y[s:s + chunk]))
        return torch.cat([o[0] for o in out]), torch.cat([o[1] for o in out])

    @torch.no_grad()
    def prefill(self, x, chunk=8192):
        sts = self.init_state(1, x.device)
        for s in range(0, x.shape[1], chunk):
            h = self._chunk(x[:, s:s + chunk], sts)
        return self.head(self.norm_f(h[:, -1])), {"layers": sts}

    @torch.no_grad()
    def step(self, tok, st):
        h = self.emb(tok)
        for b, s in zip(self.blocks, st["layers"]):
            h = h + b.mixer.step(b.norm(h), s)
        return self.head(self.norm_f(h)), st


# =============================================================================== RD-S4
class RDS4Arm(BaseArm):
    """The notebook's RDS4LM with its full objective (CE + JEPA + VICReg + PTV drafts + router
    balance), EMA teacher, and in-network evolution. Nothing here changes the model; the
    long-stream NLL mirrors the notebook's `_prefill_once` but keeps every position's logits."""

    name = "RD-S4"

    def __init__(self, vocab, ns):
        super().__init__()
        self.vocab = vocab
        self.ns = ns
        self.cfg = ns["RDS4Config"](vocab_size=vocab, seq_len=C.P.seq_len)
        self.m = ns["RDS4LM"](self.cfg)
        self.evo = None

    def tcfg(self, lr):
        return self.ns["TrainConfig"](lr=lr, weight_decay=C.P.weight_decay)

    def make_optimizer(self, lr):
        return self.ns["make_optimizer"](self.m, self.tcfg(lr))

    def start_evolution(self, lr):
        self.evo = self.ns["EFREvolver"](self.m, self.tcfg(lr), self.cfg)
        return self.evo

    def logits(self, x):
        return self.m(x)["logits"]

    def train_loss(self, x, y):
        out = self.m(x, collect_routes=True)
        return self.ns["compute_loss"](self.m, out, x, y, self.cfg)

    def after_step(self):
        self.m.update_ema()

    def mixing_flops(self, B, T, training):
        cfg = self.cfg
        d, N, Ns = cfg.d_model, cfg.d_state, cfg.d_summary
        fft = C.fft_flops(2 * B * d + d, 2 * T) + 6.0 * B * d * (T + 1)
        kern = 8.0 * d * N * T
        summary = 8.0 * B * T * Ns                    # diag_scan's carry combine; its einsum is counted
        return cfg.n_layers * (fft + kern + summary) + summary

    @torch.no_grad()
    def _chunk(self, x, st, plan_carry):
        """One chunk of the notebook's `_prefill_once`, returning the hidden state at EVERY position."""
        ns, m, cfg = self.ns, self.m, self.cfg
        resonance, sum_chunk, ssm_chunk = ns["resonance"], ns["sum_chunk"], ns["ssm_chunk"]
        L = cfg.chunk
        B, T = x.shape
        Cn = T // L
        e = m.emb(x)
        sp, st["plan_s"] = sum_chunk(m.planner.summary, e, st["plan_s"])
        z = m.planner.enc(torch.cat([sp.real, sp.imag, resonance(m.planner.summary.query(e), sp)], -1))
        z_pred = torch.stack([m.planner.pred(torch.cat([z, m.planner.horizon.weight[i].expand_as(z)], -1))
                              for i in range(len(cfg.jepa_horizons))], 0)
        plan_end = z_pred.mean(0).view(B, Cn, L, -1)[:, :, -1, :]
        if plan_carry is None:
            plan_carry = torch.zeros_like(plan_end[:, :1])
        plan_win = torch.cat([plan_carry, plan_end[:, :-1]], 1)
        plan_carry = plan_end[:, -1:]
        h = e
        for blk, bst in zip(m.blocks, st["blocks"]):
            u, zg = blk.in_proj(blk.norm(h)).chunk(2, dim=-1)
            u = F.silu(u)
            y, bst["h"] = ssm_chunk(blk.ssm, u, bst["h"])
            sv, bst["s"] = sum_chunk(blk.summary, u, bst["s"])
            rho = resonance(blk.summary.query(u), sv)
            y = y * (1.0 + torch.tanh(blk.res_gate(rho)))
            win_end = torch.cat([sv.real, sv.imag, rho], -1).view(B, Cn, L, -1)[:, :, -1, :]
            prev = torch.cat([bst["prev"].unsqueeze(1), win_end[:, :-1]], 1)
            bst["prev"] = win_end[:, -1]
            alpha, idx, _ = blk.efr.route(torch.cat([prev, plan_win], -1))
            h = h + blk.out_proj(blk.efr.apply_window(y, alpha, idx, L) * F.silu(zg))
        st["tick"] += T
        return h, plan_carry

    @torch.no_grad()
    def nll_stream(self, ids, chunk=8192):
        x, y = ids[:-1].view(1, -1), ids[1:]
        if x.shape[1] % self.cfg.chunk:
            raise ValueError("RD-S4 needs stream lengths that are a multiple of its window")
        st, carry, out = self.m.init_state(1, ids.device), None, []
        for s in range(0, x.shape[1], chunk):
            h, carry = self._chunk(x[:, s:s + chunk], st, carry)
            out.append(_nll_acc(self.m.lm_head(self.m.norm_f(h))[0], y[s:s + chunk]))
        return torch.cat([o[0] for o in out]), torch.cat([o[1] for o in out])

    @torch.no_grad()
    def prefill(self, x, chunk=8192):
        return self.ns["prefill"](self.m, x, pf_chunk=chunk)        # the notebook's own routine

    @torch.no_grad()
    def step(self, tok, st):
        lg, _, st = self.m.step(tok, st)
        return lg, st


# =============================================================================== RD-S4 v2
_V2_CLASSES = {}


def v2_arm_class(ns2):
    """The main notebook's RDS4LM with the benchmark interface: the arm IS the notebook model (same parameter
    names, same code), plus the shared optimiser recipe, FLOP accounting and an optionally compiled step."""
    if id(ns2) in _V2_CLASSES:
        return _V2_CLASSES[id(ns2)]
    Model = ns2["RDS4LM"]

    class RDS4v2Arm(BaseArm, Model):
        name = "RD-S4 v2"
        precision = "fp32 (TF32 matmul); chunked parallel form on tensor cores, no custom kernels"

        def __init__(self, vocab, **over):
            Model.__init__(self, ns2["RDS4Config"](vocab_size=vocab, seq_len=C.P.seq_len, **over))

        def train_loss(self, x, y, w=None):
            return self.loss(x, y, w)

        def mixing_flops(self, B, T, training):
            """Sequence-mixing work that is not a dense matmul (matmuls, including the cross-chunk ones, are
            counted by the dispatcher): the triangular solve, masks, decays, exponentials and rotations."""
            m = self.blocks[0].mixer
            Cn, K, V, H = m.chunk, m.dk, m.dv, m.H
            per_tok_head = Cn * (K + V) + 8 * Cn + 30 * K
            return self.n_layers * B * T * H * per_tok_head

    _V2_CLASSES[id(ns2)] = RDS4v2Arm
    return RDS4v2Arm


# =============================================================================== factory
def build(name, vocab, ns, ns2=None, **over):
    if name == "Transformer":
        return TransformerArm(vocab)
    if name == "S4":
        return S4Arm(vocab, ns)
    if name == "Mamba":
        return MambaArm(vocab)
    if name == "RD-S4":
        return RDS4Arm(vocab, ns)
    if name == "RD-S4 v2":
        return v2_arm_class(ns2)(vocab, **over)
    if name == "RD-S4 v2 (no JEPA)":                  # ablation only (ablate_v2.py), not a benchmark arm
        return v2_arm_class(ns2)(vocab, jepa=0.0, **over)
    raise KeyError(name)
