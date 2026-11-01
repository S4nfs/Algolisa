"""Shared infrastructure for the four-way benchmark: Transformer vs S4 vs Mamba vs RD-S4 (v1 of record and v2).

Everything that has to be identical across the four arms lives here: the corpus and its
splits, the tokenizer, the optimizer recipe, the learning-rate schedule, the FLOP accountant
and the result store.

RD-S4 is not re-implemented here. Its classes are extracted from the notebooks of record by parsing their
code cells and keeping only definitions, so the benchmark always measures the code the notebooks describe:
RD-S4 v2 from RD-S4_EFR_TinyStories.ipynb (the main notebook), RD-S4 v1 from
RD-S4_EFR_Attention_Is_No_More_Needed.ipynb.
"""
import ast
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import time
import types
from dataclasses import dataclass, asdict

import numpy as np
import torch
from torch.utils._python_dispatch import TorchDispatchMode

HERE = os.path.dirname(os.path.abspath(__file__))
# RD-S4 v1 now lives only in the book notebook (its model cells are byte-identical to the TinyStories notebook
# that v1 was benchmarked from); RD-S4 v2 is the main notebook, RD-S4_EFR_TinyStories.ipynb.
NB_PATH = os.path.normpath(os.path.join(HERE, "..", "..", "RD-S4_EFR_Attention_Is_No_More_Needed.ipynb"))
NB_V2_PATH = os.path.normpath(os.path.join(HERE, "..", "..", "RD-S4_EFR_TinyStories.ipynb"))
RESULTS_DIR = os.path.join(HERE, "results")
CKPT_DIR = os.path.join(HERE, "checkpoints")
FIG_DIR = os.path.join(HERE, "figures")
DATA_CACHE = os.path.join(HERE, "data_cache")
for _d in (RESULTS_DIR, CKPT_DIR, FIG_DIR, DATA_CACHE):
    os.makedirs(_d, exist_ok=True)

ARMS = ("Transformer", "S4", "Mamba", "RD-S4", "RD-S4 v2")
RECURRENT = ("S4", "Mamba", "RD-S4", "RD-S4 v2")


@dataclass(frozen=True)
class Protocol:
    # ---- data
    seq_len: int = 512
    batch: int = 32
    train_chars: int = 80_000_000
    probe_chars: int = 1_000_000      # RD-S4 evolution probes, carved from the TRAIN stream
    select_chars: int = 2_000_000     # learning-rate selection only
    min_char_count: int = 100         # rarer characters map to UNK
    # ---- evaluation sizes
    curve_windows: int = 64
    select_windows: int = 1024
    test_windows: int = 4096
    eval_every: int = 100
    # ---- optimisation (shared by every arm)
    weight_decay: float = 0.05
    beta1: float = 0.9
    beta2: float = 0.95
    grad_clip: float = 1.0
    warmup_frac: float = 0.04
    min_lr_frac: float = 0.10
    lr_grid: tuple = (1.5e-3, 3e-3, 6e-3)
    seeds: tuple = (0, 1, 2)
    # ---- compute budget: training FLOPs of every arm (set by the `plan` stage)
    tokens_ref: int = 34_000_000      # ~20 tokens/parameter for the reference arm (Transformer)
    # ---- long context
    long_ctx: tuple = (8192, 32768, 131072)
    long_streams: int = 4
    needle_dist: tuple = (256, 2048, 8192, 32768, 131072)
    needle_len: int = 128
    needle_skip: int = 16             # repeat positions the model needs to recognise the copy
    needle_samples: int = 8
    # ---- efficiency
    speed_ctx: tuple = (2048, 8192, 32768, 131072)
    speed_chunk: int = 2048           # prefill chunk for every recurrent arm (the 128K sweep shows
                                      # it is as fast as 8192 for S4/RD-S4, faster for Mamba, 4x leaner)
    decode_tokens: int = 128
    graph_steps: int = 32             # one RD-S4 routing window per captured graph
    # ---- controlled retrieval (eval2): identical sequences except for an earlier copy of the passage
    retrieval_gaps: tuple = (32, 192, 2048, 8192, 32768, 131072)
    retrieval_pre: int = 32
    window: int = 512                 # in-distribution reference context = the training length
    window_stride: int = 256


P = Protocol()
EOS, UNK = "\x03", "\x1a"
TS_REPO = "roneneldan/TinyStories"
TS_TRAIN = "data/train-00000-of-00004-2d5a1467fff1081b.parquet"
TS_VALID = "data/validation-00000-of-00001-869c898b519ad725.parquet"


# --------------------------------------------------------------------------- runtime
def setup_torch():
    if not torch.cuda.is_available():
        raise SystemExit("This benchmark needs the CUDA device it is meant to measure.")
    torch.set_float32_matmul_precision("high")   # TF32 matmuls, identical for every arm
    torch.backends.cudnn.allow_tf32 = True
    return torch.device("cuda")


def seed_all(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def sync():
    torch.cuda.synchronize()


def gpu_snapshot():
    """Clocks, temperature, memory and the processes on the GPU, for the provenance record."""
    q = ("name,driver_version,memory.used,memory.total,temperature.gpu,power.draw,"
         "clocks.sm,clocks.mem,clocks_throttle_reasons.active")
    try:
        out = subprocess.run(["nvidia-smi", f"--query-gpu={q}", "--format=csv,noheader"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        apps = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory",
                               "--format=csv,noheader"], capture_output=True, text=True,
                              timeout=10).stdout.strip()
    except Exception as exc:                                      # noqa: BLE001
        return {"error": repr(exc)}
    return {"gpu": out, "compute_apps": apps or "none", "time": time.strftime("%Y-%m-%d %H:%M:%S")}


# --------------------------------------------------------------------------- result store
def rpath(name):
    return os.path.join(RESULTS_DIR, name)


def save_json(name, obj):
    tmp = rpath(name) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, default=float)
    os.replace(tmp, rpath(name))


def load_json(name, default=None):
    p = rpath(name)
    if not os.path.exists(p):
        return default
    with open(p) as f:
        return json.load(f)


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


# --------------------------------------------------------------------------- corpus
def _ts_file(fname):
    from huggingface_hub import hf_hub_download
    return hf_hub_download(TS_REPO, fname, repo_type="dataset")


def _stories(fname):
    import pyarrow.parquet as pq
    col = pq.read_table(_ts_file(fname), columns=["text"]).column("text").to_pylist()
    return [s.replace("\r", "").strip() for s in col if s and s.strip()]


def _codepoints(text):
    return np.frombuffer(text.encode("utf-32-le"), dtype=np.uint32)


class Corpus:
    """Character-level TinyStories with disjoint train / probe / select / test splits."""

    def __init__(self, itos, train, probe, select, test, meta):
        self.itos, self.meta = itos, meta
        self.stoi = {c: i for i, c in enumerate(itos)}
        self.train, self.probe, self.select, self.test = train, probe, select, test
        self.vocab = len(itos)

    def decode(self, ids):
        return "".join(self.itos[int(i)] for i in ids)

    # test-split regions, fixed so every arm and every seed is scored on the same text
    def test_short(self):
        n = P.test_windows * P.seq_len
        return self.test[:n].view(P.test_windows, P.seq_len)

    def long_streams(self):
        base, L = 2_200_000, max(P.long_ctx)
        return [self.test[base + i * L: base + (i + 1) * L] for i in range(P.long_streams)]

    def needle_regions(self):
        return self.test[2_900_000:3_000_000], self.test[3_000_000:]


def build_corpus():
    cache = os.path.join(DATA_CACHE, "tinystories_char_v1.pt")
    if os.path.exists(cache):
        d = torch.load(cache)
        return Corpus(d["itos"], d["train"], d["probe"], d["select"], d["test"], d["meta"])

    t0 = time.time()
    need = P.train_chars + P.probe_chars
    taken, tot = [], 0
    for s in _stories(TS_TRAIN):
        taken.append(s)
        tot += len(s) + 1
        if tot >= need:
            break
    train_text = EOS.join(taken) + EOS
    val_text = EOS.join(_stories(TS_VALID)) + EOS

    cps = _codepoints(train_text)
    uniq, counts = np.unique(cps, return_counts=True)
    keep = uniq[counts >= P.min_char_count]
    itos = [chr(int(c)) for c in keep]
    if EOS not in itos:
        itos.append(EOS)
    itos.append(UNK)
    if len(itos) > 255:
        raise ValueError("vocabulary does not fit uint8")
    unk_id = len(itos) - 1
    max_cp = int(max(ord(c) for c in itos))
    lut = np.full(max_cp + 1, unk_id, dtype=np.uint8)
    for i, c in enumerate(itos):
        lut[ord(c)] = i

    def enc(text):
        cp = _codepoints(text)
        out = np.full(cp.shape, unk_id, dtype=np.uint8)
        ok = cp <= max_cp
        out[ok] = lut[cp[ok]]
        return torch.from_numpy(out)

    tr, va = enc(train_text), enc(val_text)
    train_ids, probe_ids = tr[:-P.probe_chars].clone(), tr[-P.probe_chars:].clone()
    select_ids, test_ids = va[:P.select_chars].clone(), va[P.select_chars:].clone()
    meta = {
        "source": f"hf:{TS_REPO} ({TS_TRAIN}, {TS_VALID})",
        "train_stories": len(taken), "vocab": len(itos),
        "unk_rate_train": float((tr == unk_id).float().mean()),
        "unk_rate_valid": float((va == unk_id).float().mean()),
        "chars": {"train": len(train_ids), "probe": len(probe_ids),
                  "select": len(select_ids), "test": len(test_ids)},
        "build_seconds": round(time.time() - t0, 1),
    }
    torch.save({"itos": itos, "train": train_ids, "probe": probe_ids, "select": select_ids,
                "test": test_ids, "meta": meta}, cache)
    return Corpus(itos, train_ids, probe_ids, select_ids, test_ids, meta)


class Sampler:
    """Random training windows. The generator is seeded per run, so two arms with the same seed
    see the same batches in the same order for as many steps as both of them take."""

    def __init__(self, ids_gpu, seed, batch=P.batch, T=P.seq_len):
        self.ids, self.B, self.T = ids_gpu, batch, T
        self.g = torch.Generator(device=ids_gpu.device)
        self.g.manual_seed(10_007 + seed)
        self.ar = torch.arange(T + 1, device=ids_gpu.device)

    def __call__(self, B=None):
        B = B or self.B
        ix = torch.randint(0, len(self.ids) - self.T - 1, (B,), device=self.ids.device,
                           generator=self.g)
        w = self.ids[ix.unsqueeze(1) + self.ar].long()
        return w[:, :-1].contiguous(), w[:, 1:].contiguous()


def windows(ids, n, T=P.seq_len):
    """The first n non-overlapping windows of a split, as (x, y)."""
    w = ids[: n * T + 1]
    x = w[:-1].view(n, T).long()
    y = w[1:].view(n, T).long()
    return x, y


# --------------------------------------------------------------------------- RD-S4 of record
_NB_MARKERS = ("def select_device", "class RDS4Config", "def diag_scan", "class EFRBank",
               "class RDS4Block", "def vicreg", "def orth", "def make_optimizer", "CORR_TILE = 128")
_KEEP_ASSIGN = {"CORR_TILE"}
_V2_MARKERS = ("def select_device", "class RDS4Config", "def rdelta_chunk", "class ResonantDeltaMixer",
               "class SurpriseGate")
_V2_KEEP_ASSIGN = {"G_MAX", "SCAN_FROM"}


def _load_notebook(path, markers, keep_assign, device, modname):
    """Execute the definitions (and only the definitions) of the marked notebook cells."""
    with open(path) as f:
        nb = json.load(f)
    cells = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
    mod = types.ModuleType(modname)
    sys.modules[modname] = mod
    ns = mod.__dict__
    ns.update({"FAST_MODE": True, "DEVICE": device})
    used, code = [], []
    for marker in markers:
        hits = [s for s in cells if marker in s]
        if len(hits) != 1:
            raise ValueError(f"{os.path.basename(path)}: marker {marker!r} found in {len(hits)} cells")
        tree = ast.parse(hits[0])
        keep = [n for n in tree.body
                if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef))
                or (isinstance(n, ast.Assign)
                    and all(isinstance(t, ast.Name) and t.id in keep_assign for t in n.targets))]
        body = ast.Module(body=keep, type_ignores=[])
        exec(compile(body, f"<{os.path.basename(path)}:{marker}>", "exec"), ns)
        code.append(ast.unparse(body))
        used.append(marker)
    ns["DEVICE"] = device
    ns["__provenance__"] = {"notebook": os.path.basename(path), "sha256": file_sha256(path),
                            "code_sha256": hashlib.sha256("\n".join(code).encode()).hexdigest(), "cells": used}
    return ns


def load_rds4(device):
    """RD-S4 v1 (resonant SSM + EFR operator dictionary + in-network evolution)."""
    return _load_notebook(NB_PATH, _NB_MARKERS, _KEEP_ASSIGN, device, "rds4_v1_of_record")


def load_rds4_v2(device):
    """RD-S4 v2 (resonant prediction-error memory) and the SPOC learning rules, from the main notebook."""
    return _load_notebook(NB_V2_PATH, _V2_MARKERS, _V2_KEEP_ASSIGN, device, "rds4_v2_of_record")


# --------------------------------------------------------------------------- FLOP accounting
_aten = torch.ops.aten
_MM = {_aten.mm, _aten.addmm, _aten.bmm, _aten.baddbmm}


class MatmulFlops(TorchDispatchMode):
    """Counts every dense contraction the code actually executes, forward and backward.

    mm / addmm / bmm / baddbmm cover nn.Linear and einsum; convolution covers Mamba's depthwise
    conv. A complex multiply-accumulate is 4 real multiplies and 4 adds, so complex matmuls are
    weighted 4x. Fused attention, FFTs and elementwise scans are NOT seen here; each arm adds
    those analytically through `mixing_flops`, so nothing is counted twice.
    """

    def __init__(self):
        super().__init__()
        self.flops = 0.0
        self.by_op = {}

    def _add(self, name, n, cplx):
        n = float(n) * (4.0 if cplx else 1.0)
        self.flops += n
        self.by_op[name] = self.by_op.get(name, 0.0) + n

    def __torch_dispatch__(self, func, types, args=(), kwargs=None):
        kwargs = kwargs or {}
        out = func(*args, **kwargs)
        pk = func.overloadpacket
        if pk in _MM:
            a, b = (args[0], args[1]) if pk in (_aten.mm, _aten.bmm) else (args[1], args[2])
            if pk in (_aten.mm, _aten.addmm):
                n = 2 * a.shape[0] * a.shape[1] * b.shape[1]
            else:
                n = 2 * a.shape[0] * a.shape[1] * a.shape[2] * b.shape[2]
            self._add(str(pk), n, a.is_complex())
        elif pk is _aten.convolution:
            x, w = args[0], args[1]
            per_out = w.shape[1] * int(np.prod(w.shape[2:]))
            self._add("convolution", 2 * out.numel() * per_out, x.is_complex())
        elif pk is _aten.convolution_backward:
            g, w, mask = args[0], args[2], args[-1]
            per_out = w.shape[1] * int(np.prod(w.shape[2:]))
            self._add("convolution_backward", 2 * g.numel() * per_out * (int(mask[0]) + int(mask[1])),
                      g.is_complex())
        return out


def fft_flops(n_transforms, n):
    """Real FFT of length n: 2.5 n log2 n (half a complex FFT)."""
    return 2.5 * n * math.log2(n) * n_transforms


# --------------------------------------------------------------------------- optimisation
NO_DECAY_KEYS = ("theta", "rho", "log_dt", "A_log", "log_A_real", "A_imag")


def make_optimizer(model, lr, slow_keys=(), slow_lr=None):
    """AdamW with the notebook's rule (no decay on vectors or SSM dynamics), extended to the
    parameter names of the baselines. `slow_keys` reproduces S4's published recipe, which
    trains A and dt at min(lr, 1e-3)."""
    decay, no_decay, slow = [], [], []
    for n, p in model.named_parameters():
        if not p.requires_grad:
            continue
        if slow_keys and any(k in n for k in slow_keys):
            slow.append(p)
        elif p.ndim <= 1 or any(k in n for k in NO_DECAY_KEYS):
            no_decay.append(p)
        else:
            decay.append(p)
    groups = [{"params": decay, "weight_decay": P.weight_decay, "lr_scale": 1.0},
              {"params": no_decay, "weight_decay": 0.0, "lr_scale": 1.0}]
    if slow:
        groups.append({"params": slow, "weight_decay": 0.0,
                       "lr_scale": min(1.0, (slow_lr or lr) / lr)})
    return torch.optim.AdamW(groups, lr=lr, betas=(P.beta1, P.beta2))


def lr_at(step, steps, lr):
    """The notebook's schedule (linear warm-up, cosine to 10 percent) on each arm's own length."""
    warm = max(1, round(P.warmup_frac * steps))
    if step < warm:
        return lr * (step + 1) / warm
    prog = (step - warm) / max(1, steps - warm)
    return P.min_lr_frac * lr + (1 - P.min_lr_frac) * lr * 0.5 * (1 + math.cos(math.pi * prog))


def count_params(m):
    return sum(p.numel() for p in m.parameters() if p.requires_grad)


def protocol_dict():
    return asdict(P)
