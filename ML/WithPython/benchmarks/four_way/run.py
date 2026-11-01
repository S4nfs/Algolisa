"""Four-way benchmark runner: Transformer vs S4 vs Mamba vs RD-S4 (v1 of record and v2) at ~1.7 M parameters.

    python run.py check            parity of every arm's streaming / decode paths
    python run.py plan             measure training FLOPs per step, fix the shared budget
    python run.py sweep            learning-rate sweep, seed 0, every arm
    python run.py seeds            remaining seeds at each arm's selected learning rate
    python run.py eval             test CE / perplexity / accuracy (all seeds)
    python run.py eval2            full-context vs 512-window CE at 8K/32K/128K; controlled retrieval
    python run.py speed            prefill / decode / peak memory at 2K-128K (seed 0)
    python run.py all              everything above, in order

Every stage writes JSON under results/ and is resumable: finished runs are skipped.
"""
import argparse
import math
import os
import statistics
import time
import traceback

from dataclasses import asdict

import numpy as np
import torch
import torch.nn.functional as F

import common as C
import arms as A

P = C.P
LOG = C.rpath("log.txt")


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


class Ctx:
    """Corpus on the GPU, RD-S4 of record, and the device."""

    def __init__(self):
        self.dev = C.setup_torch()
        self.cor = C.build_corpus()
        self.ns = C.load_rds4(self.dev)            # RD-S4 v1 (book notebook)
        self.ns2 = C.load_rds4_v2(self.dev)        # RD-S4 v2 and the SPOC rules (main notebook)
        self.train = self.cor.train.to(self.dev)
        self.probe = self.cor.probe.to(self.dev)
        sx, sy = C.windows(self.cor.select, P.select_windows)
        self.sel = (sx.to(self.dev), sy.to(self.dev))
        self.curve = (self.sel[0][:P.curve_windows], self.sel[1][:P.curve_windows])

    def build(self, name, **over):
        return A.build(name, self.cor.vocab, self.ns, self.ns2, **over).to(self.dev)


# --------------------------------------------------------------------------- evaluation helpers
@torch.no_grad()
def eval_ce(arm, x, y, bs=32):
    was = arm.training
    arm.eval()
    tot, ok, n = 0.0, 0, 0
    for i in range(0, len(x), bs):
        lg = arm.logits(x[i:i + bs]).float()
        tot += F.cross_entropy(lg.reshape(-1, lg.shape[-1]), y[i:i + bs].reshape(-1), reduction="sum").item()
        ok += (lg.argmax(-1) == y[i:i + bs]).sum().item()
        n += y[i:i + bs].numel()
    arm.train(was)
    return tot / n, ok / n


def ckpt_path(arm, lr, seed):
    return os.path.join(C.CKPT_DIR, f"{arm}_lr{lr:g}_s{seed}.pt")


def run_name(arm, lr, seed):
    return f"runs/{arm}_lr{lr:g}_s{seed}.json"


# --------------------------------------------------------------------------- stage: check
def stage_check(cx):
    """Every fast path must reproduce the parallel forward. Run on random weights here and again
    on trained weights in `eval`."""
    out = {}
    torch.manual_seed(0)
    ids = cx.cor.test[:2049].long().to(cx.dev)
    for name in C.ARMS:
        arm = cx.build(name).eval()
        res = {"params": C.count_params(arm)}
        x, y = ids[:-1].view(1, -1), ids[1:]
        with torch.no_grad():
            ref = F.cross_entropy(arm.logits(x)[0].float(), y, reduction="none")
            nll, _ = arm.nll_stream(ids, chunk=512)
        res["stream_vs_parallel_max_abs_nll"] = (nll - ref).abs().max().item()
        with torch.no_grad():
            lg_par = arm.logits(x)[0].float()
            _, st = arm.prefill(x[:, :1024], chunk=512)
            errs = []
            for t in range(1024, 1280):
                lg, st = arm.step(x[0, t:t + 1], st)
                errs.append((lg.float()[0] - lg_par[t]).abs().max().item() / lg_par[t].abs().max().item())
        res["decode_vs_parallel_max_rel_logit"] = max(errs)
        out[name] = res
        log(f"check {name:12s} params {res['params']:,}  stream|dNLL| {res['stream_vs_parallel_max_abs_nll']:.2e}"
            f"  decode rel {res['decode_vs_parallel_max_rel_logit']:.2e}")
        del arm
        torch.cuda.empty_cache()
    C.save_json("check.json", {"random_init": out, "gpu": C.gpu_snapshot()})


# --------------------------------------------------------------------------- stage: plan
def measure_step_flops(cx, arm):
    x, y = Sampler0(cx)()
    arm.train()
    with C.MatmulFlops() as fc:
        loss, _ = arm.train_loss(x, y)
        loss.backward()
    arm.zero_grad(set_to_none=True)
    with C.MatmulFlops() as ff:
        with torch.no_grad():
            arm.train_loss(x, y)
    mix = arm.mixing_flops(P.batch, P.seq_len, True)
    return {"matmul_fwd_bwd": fc.flops, "matmul_fwd": ff.flops, "mixing_fwd": mix,
            "per_step": fc.flops + 3.0 * mix, "by_op": fc.by_op}


def Sampler0(cx):
    return C.Sampler(cx.train, seed=12345)


def stage_plan(cx):
    """Measure training FLOPs per step and fix each arm's step count under the shared budget. The budget is
    set once (by the Transformer); arms added later are measured and merged without changing it."""
    plan = C.load_json("plan.json") or {"protocol": C.protocol_dict(), "arms": {}, "gpu": C.gpu_snapshot(),
                                        "rds4_provenance": cx.ns["__provenance__"], "corpus": cx.cor.meta}
    new = [n for n in C.ARMS if n not in plan["arms"]]
    for name in new:
        torch.manual_seed(0)
        arm = cx.build(name)
        f = measure_step_flops(cx, arm)
        rec = {"params": C.count_params(arm), **f}
        if hasattr(arm, "inference_params"):
            rec["inference_params"] = arm.inference_params()
        if name == "RD-S4":
            tc = cx.ns["TrainConfig"]()
            px, _ = C.Sampler(cx.probe, seed=1, batch=tc.probe_batch)()
            arm.m.eval()
            with C.MatmulFlops() as fp, torch.no_grad():
                arm.m(px)
            arm.m.train()
            per_fwd = fp.flops + arm.mixing_flops(tc.probe_batch, P.seq_len, False)
            n_fwd = 2 + tc.islands_per_generation * (2 + 2 * tc.children_per_island)
            rec["evolution"] = {"probe_forward_flops": per_fwd, "forwards_per_generation": n_fwd,
                                "every": tc.evolve_every}
        if name == "RD-S4 v2":
            plan["rds4_v2_provenance"] = {**cx.ns2["__provenance__"], "config": asdict(arm.cfg)}
        # wall-clock per step, for scheduling only (the budget is FLOPs, not time)
        if hasattr(arm, "enable_compile"):
            arm.enable_compile()
        opt = arm.make_optimizer(1e-3)
        smp = Sampler0(cx)
        for i in range(8):
            if i == 3:
                C.sync()
                t0 = time.perf_counter()
            xb, yb = smp()
            loss, _ = arm.train_loss(xb, yb)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            arm.after_step()
        C.sync()
        rec["sec_per_step"] = (time.perf_counter() - t0) / 5
        plan["arms"][name] = rec
        del arm, opt
        torch.cuda.empty_cache()
        torch._dynamo.reset()

    if "budget_flops" not in plan:
        ref = plan["arms"]["Transformer"]
        plan["budget_flops"] = round(P.tokens_ref / (P.batch * P.seq_len)) * ref["per_step"]
    budget = plan["budget_flops"]
    for name in new:
        rec = plan["arms"][name]
        ev = rec.get("evolution")
        if ev:
            per_gen = ev["probe_forward_flops"] * ev["forwards_per_generation"]
            s = int(budget // rec["per_step"])
            while s * rec["per_step"] + ((s - 1) // ev["every"]) * per_gen > budget:
                s -= 1
            rec["evolution_flops_total"] = ((s - 1) // ev["every"]) * per_gen
        else:
            s = int(budget // rec["per_step"])
            rec["evolution_flops_total"] = 0.0
        rec["steps"] = s
        rec["tokens"] = s * P.batch * P.seq_len
        rec["train_flops"] = s * rec["per_step"] + rec["evolution_flops_total"]
        rec["est_minutes"] = s * rec["sec_per_step"] / 60
        log(f"plan {name:12s} params {rec['params']:,}  {rec['per_step']/1e12:.3f} TFLOP/step "
            f"(matmul {rec['matmul_fwd_bwd']/1e12:.3f}, mixing x3 {3*rec['mixing_fwd']/1e12:.3f})  "
            f"steps {s}  tokens {rec['tokens']/1e6:.1f}M  ~{rec['est_minutes']:.1f} min/run")
    plan.setdefault("gpu_by_arm", {}).update({n: C.gpu_snapshot() for n in new})
    C.save_json("plan.json", plan)
    return plan


# --------------------------------------------------------------------------- stage: train
def train_run(cx, name, lr, seed, steps):
    rn = run_name(name, lr, seed)
    done = C.load_json(rn)
    if done is not None and os.path.exists(ckpt_path(name, lr, seed)):
        return done
    log(f"train {name} lr {lr:g} seed {seed}: {steps} steps")
    C.seed_all(seed)
    arm = cx.build(name)
    if hasattr(arm, "enable_compile"):              # fused training step (wall-clock only; FLOPs are the plan's)
        arm.enable_compile()
    opt = arm.make_optimizer(lr)
    smp = C.Sampler(cx.train, seed)
    evo = probe = None
    if name == "RD-S4":
        evo = arm.start_evolution(lr)
        probe = C.Sampler(cx.probe, seed + 1000, batch=evo.tcfg.probe_batch)
    hist = {"step": [], "train_ce": [], "eval_step": [], "curve_ce": [], "grad_norm": []}
    diverged = False
    C.sync()
    t0 = time.perf_counter()
    arm.train()
    for step in range(steps):
        lr_t = C.lr_at(step, steps, lr)
        for g in opt.param_groups:
            g["lr"] = lr_t * g.get("lr_scale", 1.0)
        x, y = smp()
        loss, stats = arm.train_loss(x, y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        gn = torch.nn.utils.clip_grad_norm_(arm.parameters(), P.grad_clip)
        opt.step()
        arm.after_step()
        if step == 0:
            C.sync()
            first_step_s = time.perf_counter() - t0          # includes one-off compilation, if any
        if evo is not None and step > 0 and step % evo.tcfg.evolve_every == 0:
            evo.generation(probe(), probe(), step)
        if step % 10 == 0 or step == steps - 1:
            ce = float(stats["ce"])
            hist["step"].append(step)
            hist["train_ce"].append(ce)
            hist["grad_norm"].append(float(gn))
            if not math.isfinite(ce):
                diverged = True
                log(f"   DIVERGED at step {step}")
                break
        if step % P.eval_every == 0 or step == steps - 1:
            hist["eval_step"].append(step)
            hist["curve_ce"].append(eval_ce(arm, *cx.curve)[0])
    C.sync()
    wall = time.perf_counter() - t0
    sel_ce, sel_acc = eval_ce(arm, *cx.sel) if not diverged else (float("inf"), 0.0)
    rec = {"arm": name, "lr": lr, "seed": seed, "steps": steps, "tokens": steps * P.batch * P.seq_len,
           "wall_s": wall, "first_step_s": first_step_s, "select_ce": sel_ce, "select_acc": sel_acc,
           "diverged": diverged,
           "params": C.count_params(arm), "hist": hist}
    if evo is not None:
        p_fp = 0.0228 * 0.5
        rec["evolution"] = {"generations": evo.gen, "trials": evo.n_trials, "ineurons": len(evo.ineurons),
                            "expected_false_positives": evo.n_trials * p_fp,
                            "coverage": evo.archive.coverage, "qd_score": evo.archive.qd_score}
    torch.save(arm.state_dict(), ckpt_path(name, lr, seed))
    C.save_json(rn, rec)
    torch._dynamo.reset()
    log(f"   done {name} lr {lr:g} s{seed}: select CE {sel_ce:.4f}  acc {sel_acc:.3f}  {wall/60:.1f} min"
        + (f"  ineurons {rec['evolution']['ineurons']} (FP exp {rec['evolution']['expected_false_positives']:.1f})"
           if evo is not None else ""))
    del arm, opt
    torch.cuda.empty_cache()
    return rec


def stage_sweep(cx, only=None):
    plan = C.load_json("plan.json")
    sweep = C.load_json("sweep.json", {})
    for name in (only or C.ARMS):
        steps = plan["arms"][name]["steps"]
        lrs = list(sweep.get(name, {}).get("lrs", P.lr_grid))
        res = {lr: train_run(cx, name, lr, 0, steps)["select_ce"] for lr in lrs}
        # extend the grid once in the direction of the optimum if it sits on an edge
        for _ in range(2):
            lrs = sorted(res)
            b = min(res, key=res.get)
            if b == lrs[0]:
                new = lrs[0] / 2
            elif b == lrs[-1]:
                new = lrs[-1] * 2
            else:
                break
            res[new] = train_run(cx, name, new, 0, steps)["select_ce"]
        b = min(res, key=res.get)
        sweep[name] = {"lrs": sorted(res), "select_ce": {f"{k:g}": v for k, v in sorted(res.items())},
                       "best_lr": b}
        C.save_json("sweep.json", sweep)
        log(f"sweep {name}: best lr {b:g}  " + "  ".join(f"{k:g}:{v:.4f}" for k, v in sorted(res.items())))


def stage_seeds(cx, only=None):
    plan, sweep = C.load_json("plan.json"), C.load_json("sweep.json")
    for name in (only or C.ARMS):
        lr = sweep[name]["best_lr"]
        for seed in P.seeds:
            train_run(cx, name, lr, seed, plan["arms"][name]["steps"])


# --------------------------------------------------------------------------- stage: eval
def needle_sample(cx, D, k):
    """[pre 256][needle 128][filler D][needle 128][pad] with the input length a multiple of 32."""
    pas, fil = cx.cor.needle_regions()
    needle = pas[k * 6000: k * 6000 + P.needle_len]
    span = D + 256 + 64
    off = (k * span) % (len(fil) - span - 1)
    pre, filler = fil[off: off + 256], fil[off + 256: off + 256 + D]
    body = torch.cat([pre, needle, filler, needle])
    n_x = math.ceil((len(body) + 1) / 32) * 32           # inputs = ids[:-1]
    tail = fil[off + 256 + D: off + 256 + D + (n_x + 1 - len(body))]
    ids = torch.cat([body, tail])
    s1, s2 = 256, 256 + P.needle_len + D
    return ids, s1, s2


def window_stats(nll, ok, positions):
    sel = torch.as_tensor(positions, device=nll.device)
    return nll[sel].mean().item(), ok[sel].float().mean().item()


def stage_eval(cx, only=None):
    sweep = C.load_json("sweep.json")
    tx, ty = (t.long().to(cx.dev) for t in C.windows(cx.cor.test, P.test_windows))
    streams = []
    base, L = 2_200_000, max(P.long_ctx)
    for i in range(P.long_streams):
        streams.append(cx.cor.test[base + i * L: base + (i + 1) * L + 1].long().to(cx.dev))
    edges = np.unique(np.round(np.logspace(0, math.log10(L), 41)).astype(int))
    for name in (only or C.ARMS):
        lr = sweep[name]["best_lr"]
        for seed in P.seeds:
            out_name = f"eval/{name}_s{seed}.json"
            if C.load_json(out_name) is not None:
                continue
            arm = cx.build(name)
            arm.load_state_dict(torch.load(ckpt_path(name, lr, seed), map_location=cx.dev))
            arm.eval()
            t0 = time.perf_counter()
            rec = {"arm": name, "seed": seed, "lr": lr}
            ce, acc = eval_ce(arm, tx, ty)
            rec["test"] = {"ce": ce, "acc": acc, "ppl": math.exp(ce), "bpc": ce / math.log(2),
                           "tokens": tx.numel()}
            # parity on trained weights
            ids = cx.cor.test[:2049].long().to(cx.dev)
            with torch.no_grad():
                ref = F.cross_entropy(arm.logits(ids[:-1].view(1, -1))[0].float(), ids[1:], reduction="none")
                nll, _ = arm.nll_stream(ids, chunk=512)
            rec["parity_stream_max_abs_nll"] = (nll - ref).abs().max().item()
            # long context: per-position NLL over 128K-character streams
            curves, win = [], {}
            for s in streams:
                with torch.no_grad():
                    nll, ok = arm.nll_stream(s, chunk=P.speed_chunk)
                n = nll.double().cpu().numpy()
                curves.append([float(n[a - 1:b - 1].mean()) for a, b in zip(edges[:-1], edges[1:])])
                for c in P.long_ctx:
                    lo = c - 4096
                    win.setdefault(str(c), []).append(window_stats(nll, ok, range(lo, c)))
                win.setdefault("0-512", []).append(window_stats(nll, ok, range(0, 512)))
                win.setdefault("512-4096", []).append(window_stats(nll, ok, range(512, 4096)))
            rec["long"] = {"edges": edges.tolist(), "curves": curves,
                           "windows": {k: {"ce": float(np.mean([v[0] for v in vs])),
                                           "acc": float(np.mean([v[1] for v in vs])),
                                           "per_stream_ce": [v[0] for v in vs]} for k, vs in win.items()}}
            # needle retrieval
            nd = {}
            for D in P.needle_dist:
                rows = []
                for k in range(P.needle_samples):
                    ids, s1, s2 = needle_sample(cx, D, k)
                    ids = ids.long().to(cx.dev)
                    with torch.no_grad():
                        nll, ok = arm.nll_stream(ids, chunk=P.speed_chunk)
                    p1 = range(s1 + P.needle_skip - 1, s1 + P.needle_len - 1)
                    p2 = range(s2 + P.needle_skip - 1, s2 + P.needle_len - 1)
                    c1, a1 = window_stats(nll, ok, p1)
                    c2, a2 = window_stats(nll, ok, p2)
                    rows.append({"ce_first": c1, "ce_repeat": c2, "acc_first": a1, "acc_repeat": a2})
                nd[str(D)] = {k2: float(np.mean([r[k2] for r in rows])) for k2 in rows[0]}
                nd[str(D)]["gain"] = nd[str(D)]["ce_first"] - nd[str(D)]["ce_repeat"]
                nd[str(D)]["gain_per_sample"] = [r["ce_first"] - r["ce_repeat"] for r in rows]
            rec["needle"] = nd
            rec["eval_seconds"] = time.perf_counter() - t0
            C.save_json(out_name, rec)
            w = rec["long"]["windows"]
            log(f"eval {name:12s} s{seed}: test CE {ce:.4f} (ppl {math.exp(ce):.3f})  "
                f"CE@8K {w['8192']['ce']:.3f} @32K {w['32768']['ce']:.3f} @128K {w['131072']['ce']:.3f}  "
                f"needle gain " + " ".join(f"{d}:{nd[str(d)]['gain']:+.3f}" for d in P.needle_dist)
                + f"  parity {rec['parity_stream_max_abs_nll']:.1e}  ({rec['eval_seconds']:.0f}s)")
            del arm
            torch.cuda.empty_cache()


# --------------------------------------------------------------------------- stage: eval2
def retrieval_pair(cx, D, k):
    """Two sequences that differ ONLY in one 128-character slot near the start:
        treatment  [pre][passage][gap D][passage][tail]
        control    [pre][decoy  ][gap D][passage][tail]
    Both are scored on the same final passage, so the difference is the value of having seen it."""
    pas, fil = cx.cor.needle_regions()
    n, pre = P.needle_len, P.retrieval_pre
    passage = pas[k * 6000: k * 6000 + n]
    decoy = pas[k * 6000 + 3000: k * 6000 + 3000 + n]
    span = D + pre + 64
    off = (k * span) % (len(fil) - span - 1)
    head, gap = fil[off: off + pre], fil[off + pre: off + pre + D]
    body = pre + n + D + n
    n_x = math.ceil((body + 1) / 32) * 32
    tail = fil[off + pre + D: off + pre + D + (n_x + 1 - body)]
    treat = torch.cat([head, passage, gap, passage, tail])
    ctrl = torch.cat([head, decoy, gap, passage, tail])
    return treat, ctrl, pre + n + D


@torch.no_grad()
def windowed_nll(arm, ids, W=None, S=None):
    """Per-position NLL when every prediction may use at most W characters (the training length):
    windows of W with stride S, scoring the last S positions of each (all W of the first)."""
    W, S = W or P.window, S or P.window_stride
    x, y = ids[:-1], ids[1:]
    N = len(x)
    starts = list(range(0, N - W + 1, S))
    if starts[-1] != N - W:
        starts.append(N - W)
    nll = torch.full((N,), float("nan"), device=ids.device)
    ok = torch.zeros(N, dtype=torch.bool, device=ids.device)
    for i in range(0, len(starts), 64):
        st = torch.tensor(starts[i:i + 64], device=ids.device)
        idx = st.unsqueeze(1) + torch.arange(W, device=ids.device)
        lg = arm.logits(x[idx]).float()
        l = F.cross_entropy(lg.reshape(-1, lg.shape[-1]), y[idx].reshape(-1), reduction="none").view(len(st), W)
        c = lg.argmax(-1) == y[idx]
        for j, s0 in enumerate(starts[i:i + 64]):
            lo = 0 if s0 == 0 else W - S
            nll[s0 + lo: s0 + W] = l[j, lo:]
            ok[s0 + lo: s0 + W] = c[j, lo:]
    return nll, ok


def stage_eval2(cx, only=None):
    sweep = C.load_json("sweep.json")
    base, L = 2_200_000, max(P.long_ctx)
    streams = [cx.cor.test[base + i * L: base + (i + 1) * L + 1].long().to(cx.dev) for i in range(P.long_streams)]
    edges = np.unique(np.round(np.logspace(0, math.log10(L), 41)).astype(int))
    for name in (only or C.ARMS):
        lr = sweep[name]["best_lr"]
        for seed in P.seeds:
            out_name = f"eval2/{name}_s{seed}.json"
            if C.load_json(out_name) is not None:
                continue
            arm = cx.build(name)
            arm.load_state_dict(torch.load(ckpt_path(name, lr, seed), map_location=cx.dev))
            arm.eval()
            t0 = time.perf_counter()
            rec = {"arm": name, "seed": seed, "lr": lr}
            # (1) the same long-stream characters, scored with full context and with a 512 window
            full_w, win_w, curves_win = {}, {}, []
            for s in streams:
                with torch.no_grad():
                    nf, okf = arm.nll_stream(s, chunk=P.speed_chunk)
                nw, okw = windowed_nll(arm, s)
                n = nw.double().cpu().numpy()
                curves_win.append([float(np.nanmean(n[a - 1:b - 1])) for a, b in zip(edges[:-1], edges[1:])])
                for c in P.long_ctx:
                    pos = range(c - 4096, c)
                    full_w.setdefault(str(c), []).append(window_stats(nf, okf, pos))
                    win_w.setdefault(str(c), []).append(window_stats(nw, okw, pos))
            rec["context"] = {
                str(c): {"ce_full": float(np.mean([v[0] for v in full_w[str(c)]])),
                         "ce_window": float(np.mean([v[0] for v in win_w[str(c)]])),
                         "acc_full": float(np.mean([v[1] for v in full_w[str(c)]])),
                         "acc_window": float(np.mean([v[1] for v in win_w[str(c)]])),
                         "benefit": float(np.mean([w[0] - f[0] for f, w in zip(full_w[str(c)], win_w[str(c)])]))}
                for c in P.long_ctx}
            rec["window_curves"] = {"edges": edges.tolist(), "curves": curves_win}
            # (2) controlled retrieval
            ret = {}
            for D in P.retrieval_gaps:
                rows = []
                for k in range(P.needle_samples):
                    treat, ctrl, s2 = retrieval_pair(cx, D, k)
                    pos = range(s2 + P.needle_skip - 1, s2 + P.needle_len - 1)
                    with torch.no_grad():
                        nt, okt = arm.nll_stream(treat.long().to(cx.dev), chunk=P.speed_chunk)
                        nc, okc = arm.nll_stream(ctrl.long().to(cx.dev), chunk=P.speed_chunk)
                    ct, at = window_stats(nt, okt, pos)
                    cc, ac = window_stats(nc, okc, pos)
                    rows.append({"ce_control": cc, "ce_treated": ct, "acc_control": ac, "acc_treated": at})
                agg = {k2: float(np.mean([r[k2] for r in rows])) for k2 in rows[0]}
                agg["gain"] = agg["ce_control"] - agg["ce_treated"]
                agg["gain_per_sample"] = [r["ce_control"] - r["ce_treated"] for r in rows]
                ret[str(D)] = agg
            rec["retrieval"] = ret
            rec["eval_seconds"] = time.perf_counter() - t0
            C.save_json(out_name, rec)
            cxr = rec["context"]
            log(f"eval2 {name:12s} s{seed}: CE full/window @8K {cxr['8192']['ce_full']:.3f}/{cxr['8192']['ce_window']:.3f}"
                f" @128K {cxr['131072']['ce_full']:.3f}/{cxr['131072']['ce_window']:.3f}  retrieval gain "
                + " ".join(f"{D}:{ret[str(D)]['gain']:+.3f}" for D in P.retrieval_gaps)
                + f"  ({rec['eval_seconds']:.0f}s)")
            del arm
            torch.cuda.empty_cache()


# --------------------------------------------------------------------------- stage: speed
def _paths(obj, prefix=()):
    if torch.is_tensor(obj):
        yield prefix, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _paths(v, prefix + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _paths(v, prefix + (i,))


def _get(obj, path):
    for p in path:
        obj = obj[p]
    return obj


def _set(obj, path, val):
    for p in path[:-1]:
        obj = obj[p]
    obj[path[-1]] = val


def _steps(arm, st, tok_buf, n, inputs):
    tok = tok_buf
    for _ in range(n):
        lg, st = arm.step(tok, st)
        tok = lg.argmax(-1)
    tok_buf.copy_(tok)
    for path, buf in inputs:               # write the advanced state back into the static buffers
        cur = _get(st, path)
        if cur is not buf:
            buf.copy_(cur)
            _set(st, path, buf)
    return st


def capture(arm, st, tok0, n):
    tok_buf = tok0.clone()
    inputs = list(_paths(st))
    s = torch.cuda.Stream()
    s.wait_stream(torch.cuda.current_stream())
    with torch.cuda.stream(s):
        st = _steps(arm, st, tok_buf, n, inputs)          # warm-up (cuBLAS workspaces etc.)
    torch.cuda.current_stream().wait_stream(s)
    g = torch.cuda.CUDAGraph()
    with torch.cuda.graph(g):
        st = _steps(arm, st, tok_buf, n, inputs)
    return g


class GraphPrefill:
    """Prefill with one CUDA graph per chunk: the arm's own chunk code (the same kernels as its eager prefill),
    captured once and replayed without Python launch overhead, as a server would. For the chunked recurrent
    arms whose chunk step has static shapes (S4, Mamba, RD-S4 v2)."""

    def __init__(self, arm, chunk, x0):
        dev = x0.device
        self.arm, self.chunk = arm, chunk
        self.st = arm.init_state(1, dev)
        self.xb = torch.zeros(1, chunk, dtype=torch.long, device=dev)
        self.lg = torch.zeros(1, arm.vocab, device=dev)
        self.inputs = list(_paths(self.st))
        C.sync()
        t0 = time.perf_counter()
        s = torch.cuda.Stream()
        s.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(s):
            self.xb.copy_(x0[:, :chunk])
            self._body()                               # warm-up (allocator, cuBLAS/cuFFT plans, Triton)
        torch.cuda.current_stream().wait_stream(s)
        C.sync()
        base = torch.cuda.memory_allocated()
        torch.cuda.reset_peak_memory_stats()
        self.g = torch.cuda.CUDAGraph()
        with torch.cuda.graph(self.g):
            self._body()
        C.sync()
        self.capture_s = time.perf_counter() - t0
        # peak live memory inside one captured chunk (same definition as the eager prefill peak)
        self.pool_mb = (torch.cuda.max_memory_allocated() - base) / 2**20

    def _body(self):
        arm, st = self.arm, self.st
        if isinstance(arm, A.S4Arm):
            h, new = arm._chunk(self.xb, st)
            st[:] = new
        else:
            h = arm._chunk(self.xb, st)
        self.lg.copy_(arm.head(arm.norm_f(h[:, -1])).float())
        for path, buf in self.inputs:                  # keep the state in the static buffers
            cur = _get(st, path)
            if cur is not buf:
                buf.copy_(cur)
                _set(st, path, buf)

    def __call__(self, x):
        for _, buf in self.inputs:
            buf.zero_()
        for i in range(0, x.shape[1], self.chunk):
            self.xb.copy_(x[:, i:i + self.chunk])
            self.g.replay()
        return self.lg.clone(), self.st


GRAPH_PREFILL = ("S4", "Mamba", "RD-S4 v2")


def measure_graph_prefill(gp, x):
    torch.cuda.empty_cache()
    base = torch.cuda.memory_allocated()
    torch.cuda.reset_peak_memory_stats()
    C.sync()
    t0 = time.perf_counter()
    gp(x)
    C.sync()
    t = time.perf_counter() - t0
    peak = torch.cuda.max_memory_allocated() - base
    return {"prefill_tok_s": x.shape[1] / t, "prefill_s": t, "peak_prefill_mb": max(gp.pool_mb, peak / 2**20)}


def measure_speed(arm, x):
    """Prefill time and peak memory, then decode in eager mode and with CUDA graphs."""
    T = x.shape[1]
    torch.cuda.empty_cache()
    base = torch.cuda.memory_allocated()
    torch.cuda.reset_peak_memory_stats()
    C.sync()
    t0 = time.perf_counter()
    lg, st = arm.prefill(x, chunk=P.speed_chunk)
    C.sync()
    t_pre = time.perf_counter() - t0
    peak_pre = torch.cuda.max_memory_allocated() - base
    sbytes = arm.decode_state_bytes(T) if hasattr(arm, "decode_state_bytes") else A.BaseArm.state_bytes(st)
    tok = lg.argmax(-1).view(1)
    # eager decode
    torch.cuda.reset_peak_memory_stats()
    C.sync()
    t0 = time.perf_counter()
    for _ in range(P.decode_tokens):
        lg2, st = arm.step(tok, st)
        tok = lg2.argmax(-1).view(1)
    C.sync()
    t_eager = (time.perf_counter() - t0) / P.decode_tokens
    peak_dec = torch.cuda.max_memory_allocated() - base
    del st
    torch.cuda.empty_cache()
    # graph decode from a fresh prefill
    lg, st = arm.prefill(x, chunk=P.speed_chunk)
    tok = lg.argmax(-1).view(1)
    g = capture(arm, st, tok, P.graph_steps)
    reps = P.decode_tokens // P.graph_steps
    g.replay()
    C.sync()
    t0 = time.perf_counter()
    for _ in range(reps):
        g.replay()
    C.sync()
    t_graph = (time.perf_counter() - t0) / (reps * P.graph_steps)
    del g, st
    torch.cuda.empty_cache()
    return {"prefill_s": t_pre, "prefill_tok_s": T / t_pre, "peak_prefill_mb": peak_pre / 2**20,
            "peak_decode_mb": peak_dec / 2**20, "state_kb": sbytes / 1024,
            "decode_eager_ms": t_eager * 1e3, "decode_graph_ms": t_graph * 1e3,
            "decode_eager_tok_s": 1 / t_eager, "decode_graph_tok_s": 1 / t_graph}


def stage_speed(cx, rounds=3):
    sweep = C.load_json("sweep.json")
    snap0 = C.gpu_snapshot()
    models = {}
    for name in C.ARMS:
        arm = cx.build(name)
        arm.load_state_dict(torch.load(ckpt_path(name, sweep[name]["best_lr"], 0), map_location=cx.dev))
        models[name] = arm.eval()
    src = cx.cor.test[2_200_000:2_200_000 + max(P.speed_ctx)].long().to(cx.dev)
    for name, arm in models.items():                  # warm-up: kernels, cuBLAS handles, Triton JIT
        measure_speed(arm, src[:4096].view(1, -1))
    raw = {n: {str(c): [] for c in P.speed_ctx} for n in C.ARMS}
    for c in P.speed_ctx:
        x = src[:c].view(1, -1)
        for r in range(rounds):                       # interleave arms so drift hits all equally
            for name, arm in models.items():
                try:
                    m = measure_speed(arm, x)
                except torch.OutOfMemoryError:
                    torch.cuda.empty_cache()
                    m = {"oom": True}
                raw[name][str(c)].append(m)
                if r == rounds - 1:
                    ms = raw[name][str(c)]
                    if "oom" in ms[0]:
                        log(f"speed {name:12s} ctx {c:>7,}: OOM")
                        continue
                    med = {k: statistics.median(v[k] for v in ms) for k in ms[0]}
                    log(f"speed {name:12s} ctx {c:>7,}: prefill {med['prefill_tok_s']:>10,.0f} tok/s  "
                        f"peak {med['peak_prefill_mb']:7.1f} MB  decode graph {med['decode_graph_tok_s']:>7,.0f} tok/s "
                        f"eager {med['decode_eager_tok_s']:>5,.0f} tok/s  state {med['state_kb']:9.1f} KB")
    summary = {n: {c: ({k: statistics.median(v[k] for v in ms) for k in ms[0]} if "oom" not in ms[0]
                       else {"oom": True}) for c, ms in d.items()} for n, d in raw.items()}
    # prefill memory/speed trade-off of the recurrent arms: chunk size is a free knob for them
    chunk_sweep = {}
    x = src.view(1, -1)
    for name in C.RECURRENT:
        chunk_sweep[name] = {}
        for ck in (2048, 8192, 32768):
            ts, pk = [], []
            for _ in range(rounds):
                torch.cuda.empty_cache()
                base = torch.cuda.memory_allocated()
                torch.cuda.reset_peak_memory_stats()
                C.sync()
                t0 = time.perf_counter()
                try:
                    models[name].prefill(x, chunk=ck)
                except torch.OutOfMemoryError:
                    ts, pk = [float("nan")], [float("nan")]
                    break
                C.sync()
                ts.append(time.perf_counter() - t0)
                pk.append((torch.cuda.max_memory_allocated() - base) / 2**20)
            chunk_sweep[name][str(ck)] = {"prefill_tok_s": x.shape[1] / statistics.median(ts),
                                          "peak_mb": statistics.median(pk)}
            log(f"chunk {name:8s} {ck:>6,}: {chunk_sweep[name][str(ck)]['prefill_tok_s']:>10,.0f} tok/s  "
                f"peak {chunk_sweep[name][str(ck)]['peak_mb']:7.1f} MB")
    # prefill without launch overhead, for every chunked arm with static chunk shapes (captured once, replayed)
    graph = {}
    for name in GRAPH_PREFILL:
        arm = models[name]
        try:
            with torch.no_grad():
                gp = GraphPrefill(arm, P.speed_chunk, src[:P.speed_chunk].view(1, -1))
                lg_e, _ = arm.prefill(src[:8192].view(1, -1), chunk=P.speed_chunk)
                lg_g, _ = gp(src[:8192].view(1, -1))
        except Exception as exc:                                           # noqa: BLE001
            graph[name] = {"error": repr(exc)}
            log(f"graph prefill {name}: not capturable ({exc!r})")
            continue
        graph[name] = {"capture_s": gp.capture_s, "max_abs_logit_diff_vs_eager": (lg_e.float() - lg_g).abs().max().item()}
        for c in P.speed_ctx:
            x = src[:c].view(1, -1)
            with torch.no_grad():
                ms = [measure_graph_prefill(gp, x) for _ in range(rounds)]
            graph[name][str(c)] = {k: statistics.median(m[k] for m in ms) for k in ms[0]}
            log(f"graph prefill {name:10s} ctx {c:>7,}: {graph[name][str(c)]['prefill_tok_s']:>10,.0f} tok/s  "
                f"peak {graph[name][str(c)]['peak_prefill_mb']:7.1f} MB  (capture {gp.capture_s:.2f}s, |dlogit| vs eager "
                f"{graph[name]['max_abs_logit_diff_vs_eager']:.1e})")
        del gp
        torch.cuda.empty_cache()
    C.save_json("speed.json", {"median": summary, "raw": raw, "chunk_sweep_128k": chunk_sweep,
                               "graph_prefill": graph,
                               "gpu_before": snap0, "gpu_after": C.gpu_snapshot(),
                               "precision": {n: m.precision for n, m in models.items()},
                               "chunk": P.speed_chunk, "decode_tokens": P.decode_tokens,
                               "graph_steps": P.graph_steps})


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["check", "plan", "sweep", "seeds", "eval", "eval2", "speed", "all"])
    ap.add_argument("--arms", nargs="*", default=None)
    a = ap.parse_args()
    os.makedirs(C.rpath("runs"), exist_ok=True)
    os.makedirs(C.rpath("eval"), exist_ok=True)
    os.makedirs(C.rpath("eval2"), exist_ok=True)
    cx = Ctx()
    log(f"=== stage {a.stage}  gpu: {C.gpu_snapshot().get('gpu')}")
    try:
        if a.stage in ("check", "all"):
            stage_check(cx)
        if a.stage in ("plan", "all"):
            stage_plan(cx)
        if a.stage in ("sweep", "all"):
            stage_sweep(cx, a.arms)
        if a.stage in ("seeds", "all"):
            stage_seeds(cx, a.arms)
        if a.stage in ("eval", "all"):
            stage_eval(cx, a.arms)
        if a.stage in ("eval2", "all"):
            stage_eval2(cx, a.arms)
        if a.stage in ("speed", "all"):
            stage_speed(cx)
    except Exception:
        log("FAILED:\n" + traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
