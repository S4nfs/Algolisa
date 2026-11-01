"""Figures, tables and statistics for the four-way benchmark. Reads only results/*.json."""
import glob
import itertools
import math
import os
import sys

import matplotlib
import numpy as np

if "ipykernel" not in sys.modules:          # inline figures in the notebook, files everywhere
    matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import common as C  # noqa: E402

P = C.P
COL = {"Transformer": "tab:blue", "S4": "tab:green", "Mamba": "tab:orange", "RD-S4": "black", "RD-S4 v2": "tab:red"}
TAG = "T | S4 | Mamba | RD-S4 | v2"
plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 150, "font.size": 9, "axes.grid": True,
                     "grid.alpha": 0.25, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.constrained_layout.use": True})


# --------------------------------------------------------------------------- loading
def load_all():
    R = {"plan": C.load_json("plan.json"), "sweep": C.load_json("sweep.json"),
         "speed": C.load_json("speed.json"), "check": C.load_json("check.json"),
         "runs": {}, "eval": {}, "eval2": {}}
    for f in glob.glob(C.rpath("runs/*.json")):
        r = C.load_json(os.path.relpath(f, C.RESULTS_DIR))
        R["runs"][(r["arm"], r["lr"], r["seed"])] = r
    for sub in ("eval", "eval2"):
        for f in glob.glob(C.rpath(f"{sub}/*.json")):
            r = C.load_json(os.path.relpath(f, C.RESULTS_DIR))
            R[sub].setdefault(r["arm"], {})[r["seed"]] = r
    return R


def final_runs(R, arm):
    lr = R["sweep"][arm]["best_lr"]
    return [R["runs"][(arm, lr, s)] for s in P.seeds if (arm, lr, s) in R["runs"]]


def evals(R, arm):
    return [R["eval"][arm][s] for s in P.seeds if s in R["eval"].get(arm, {})]


def evals2(R, arm):
    return [R["eval2"][arm][s] for s in P.seeds if s in R["eval2"].get(arm, {})]


# --------------------------------------------------------------------------- statistics
def perm_test(a, b, alternative="two-sided"):
    """Exact permutation test on the difference of means (all C(n+m, n) relabellings).
    alternative='less' tests mean(a) < mean(b)."""
    a, b = list(map(float, a)), list(map(float, b))
    pooled = np.array(a + b)
    n = len(a)
    obs = np.mean(a) - np.mean(b)
    hits = tot = 0
    for idx in itertools.combinations(range(len(pooled)), n):
        m = np.zeros(len(pooled), bool)
        m[list(idx)] = True
        d = pooled[m].mean() - pooled[~m].mean()
        if alternative == "two-sided":
            hits += abs(d) >= abs(obs) - 1e-12
        elif alternative == "less":
            hits += d <= obs + 1e-12
        else:
            hits += d >= obs - 1e-12
        tot += 1
    return hits / tot


def msd(v):
    v = np.asarray(v, float)
    return float(v.mean()), float(v.std(ddof=1)) if len(v) > 1 else 0.0


# --------------------------------------------------------------------------- tables
def scorecard(R):
    """One row per metric, one column per arm: mean +- sd over seeds."""
    rows = []
    spd = R["speed"]["median"] if R.get("speed") else {}

    def add(label, fn, fmt, better="low"):
        cells = {}
        for a in C.ARMS:
            try:
                cells[a] = fn(a)
            except (KeyError, IndexError, TypeError, ValueError):
                cells[a] = None
        rows.append((label, cells, fmt, better))

    add("params", lambda a: (R["plan"]["arms"][a]["params"], 0), "{:,.0f}", None)
    add("training tokens (equal FLOPs)", lambda a: (R["plan"]["arms"][a]["tokens"] / 1e6, 0), "{:.1f} M", None)
    add("selected learning rate", lambda a: (R["sweep"][a]["best_lr"], 0), "{:g}", None)
    add("test CE (nats/char)", lambda a: msd([e["test"]["ce"] for e in evals(R, a)]), "{:.4f}")
    add("test perplexity (per char)", lambda a: msd([e["test"]["ppl"] for e in evals(R, a)]), "{:.3f}")
    add("test top-1 accuracy", lambda a: msd([100 * e["test"]["acc"] for e in evals(R, a)]), "{:.2f} %", "high")
    for c in P.long_ctx:
        add(f"CE at {c // 1024}K, full context",
            lambda a, c=c: msd([e["context"][str(c)]["ce_full"] for e in evals2(R, a)]), "{:.4f}")
    for c in P.long_ctx:
        add(f"CE at {c // 1024}K, 512-char window",
            lambda a, c=c: msd([e["context"][str(c)]["ce_window"] for e in evals2(R, a)]), "{:.4f}")
    for c in P.long_ctx:
        add(f"gain from context >512 @ {c // 1024}K",
            lambda a, c=c: msd([e["context"][str(c)]["benefit"] for e in evals2(R, a)]), "{:+.4f}", "high")
    for D in P.retrieval_gaps:
        add(f"retrieval gain, gap {D:,}",
            lambda a, D=D: msd([e["retrieval"][str(D)]["gain"] for e in evals2(R, a)]), "{:+.3f}", "high")
    for c in P.long_ctx:
        add(f"prefill tok/s @ {c // 1024}K", lambda a, c=c: (spd[a][str(c)]["prefill_tok_s"], 0), "{:,.0f}", "high")
    for c in P.long_ctx:
        add(f"decode tok/s @ {c // 1024}K (graphs)", lambda a, c=c: (spd[a][str(c)]["decode_graph_tok_s"], 0),
            "{:,.0f}", "high")
    for c in P.long_ctx:
        add(f"peak prefill MB @ {c // 1024}K", lambda a, c=c: (spd[a][str(c)]["peak_prefill_mb"], 0), "{:,.1f}")
    for c in P.long_ctx:
        add(f"decode state @ {c // 1024}K (KB)", lambda a, c=c: (spd[a][str(c)]["state_kb"], 0), "{:,.1f}")
    return rows


def scorecard_text(R):
    rows = scorecard(R)
    w = 34
    out = [f"{'metric':<{w}}" + "".join(f"{a:>22}" for a in C.ARMS)]
    out.append("-" * (w + 22 * len(C.ARMS)))
    for label, cells, fmt, better in rows:
        vals = {a: c[0] for a, c in cells.items() if c is not None}
        best = None
        if better and vals:
            best = (min if better == "low" else max)(vals, key=vals.get)
        line = f"{label:<{w}}"
        for a in C.ARMS:
            c = cells[a]
            if c is None:
                s = "n/a"
            else:
                s = fmt.format(c[0]) + (f" ±{fmt.format(c[1]).replace(' %', '').replace(' M', '')}" if c[1] else "")
                if a == best:
                    s = "*" + s
            line += f"{s:>22}"
        out.append(line)
    out.append("* = best on that row.  ± = sample standard deviation over seeds.")
    return "\n".join(out)


def significance(R):
    """Each RD-S4 version against each other arm on every per-seed quality metric. With 3 seeds per arm the
    exact permutation test has 20 relabellings, so the smallest attainable one-sided p is 0.05."""
    out = []
    metrics = [("test CE", lambda e1, e2: e1["test"]["ce"], "less")]
    for c in P.long_ctx:
        metrics.append((f"CE@{c // 1024}K full", lambda e1, e2, c=c: e2["context"][str(c)]["ce_full"], "less"))
    for D in P.retrieval_gaps:
        metrics.append((f"retrieval@{D}", lambda e1, e2, D=D: e2["retrieval"][str(D)]["gain"], "greater"))
    for model, bases in (("RD-S4", ("Transformer", "S4", "Mamba")),
                         ("RD-S4 v2", ("Transformer", "S4", "Mamba", "RD-S4"))):
        rd = list(zip(evals(R, model), evals2(R, model)))
        for base in bases:
            b = list(zip(evals(R, base), evals2(R, base)))
            if not rd or not b:
                continue
            for name, fn, alt in metrics:
                va, vb = [fn(*e) for e in rd], [fn(*e) for e in b]
                out.append({"model": model, "baseline": base, "metric": name, "rd_s4": float(np.mean(va)),
                            "baseline_mean": float(np.mean(vb)), "diff": float(np.mean(va) - np.mean(vb)),
                            "p_one_sided": perm_test(va, vb, alt), "p_two_sided": perm_test(va, vb),
                            "n": (len(va), len(vb))})
    return out


# --------------------------------------------------------------------------- figures
def _save(fig, name):
    fig.savefig(os.path.join(C.FIG_DIR, name), bbox_inches="tight")
    return fig


def fig_training(R):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
    for a in C.ARMS:
        runs = final_runs(R, a)
        if not runs:
            continue
        per = R["plan"]["arms"][a]["per_step"]
        ev = R["plan"]["arms"][a]["evolution_flops_total"] / max(1, R["plan"]["arms"][a]["steps"])
        xs = np.array(runs[0]["hist"]["eval_step"]) * (per + ev) / 1e15
        ys = np.array([r["hist"]["curve_ce"] for r in runs if len(r["hist"]["curve_ce"]) == len(xs)])
        ax[0].plot(xs, ys.mean(0), color=COL[a], lw=1.6, label=f"{a} (lr {R['sweep'][a]['best_lr']:g})")
        ax[0].fill_between(xs, ys.min(0), ys.max(0), color=COL[a], alpha=0.15)
        sw = R["sweep"][a]["select_ce"]
        lrs = sorted(sw, key=float)
        ax[1].plot([float(x) for x in lrs], [sw[x] for x in lrs], "o-", color=COL[a], label=a)
    ax[0].axvline(R["plan"]["budget_flops"] / 1e15, ls="--", lw=0.8, color="grey")
    ax[0].set_xlabel("training compute (PFLOP)")
    ax[0].set_ylabel("held-out CE (selection split)")
    ax[0].set_ylim(top=2.0)
    ax[0].set_title(f"[{TAG}] (a) learning curves at equal FLOPs, 3 seeds")
    ax[0].legend(fontsize=8)
    ax[1].set_xscale("log")
    ax[1].set_xlabel("peak learning rate")
    ax[1].set_ylabel("selection-split CE, seed 0")
    ax[1].set_title("(b) every arm gets its own learning-rate sweep")
    ax[1].legend(fontsize=8)
    return _save(fig, "fig1_training.png")


def fig_quality(R):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.0))
    for i, a in enumerate(C.ARMS):
        v = [e["test"]["ce"] for e in evals(R, a)]
        if not v:
            continue
        ax[0].bar(i, np.mean(v), color=COL[a], alpha=0.35)
        ax[0].plot([i] * len(v), v, "o", color=COL[a], ms=5)
        ax[0].text(i, np.mean(v), f"{np.mean(v):.4f}\nppl {math.exp(np.mean(v)):.3f}", ha="center",
                   va="bottom", fontsize=8)
    allv = [e["test"]["ce"] for a in C.ARMS for e in evals(R, a)]
    if allv:
        lo, hi = min(allv), max(allv)
        ax[0].set_ylim(lo - 0.6 * (hi - lo + 1e-3), hi + 0.8 * (hi - lo + 1e-3))
    ax[0].set_xticks(range(len(C.ARMS)), C.ARMS)
    ax[0].set_ylabel("test CE (nats/char), 2.1 M characters")
    ax[0].set_title(f"[{TAG}] (a) quality at equal FLOPs; dots are seeds")
    for a in C.ARMS:
        es = evals(R, a)
        if not es:
            continue
        acc = [100 * e["test"]["acc"] for e in es]
        ax[1].bar(C.ARMS.index(a), np.mean(acc), color=COL[a], alpha=0.35)
        ax[1].plot([C.ARMS.index(a)] * len(acc), acc, "o", color=COL[a], ms=5)
    ax[1].set_xticks(range(len(C.ARMS)), C.ARMS)
    accs = [100 * e["test"]["acc"] for a in C.ARMS for e in evals(R, a)]
    if accs:
        ax[1].set_ylim(min(accs) - 1.5, max(accs) + 1.0)
    ax[1].set_ylabel("next-character top-1 accuracy (%)")
    ax[1].set_title("(b) accuracy")
    return _save(fig, "fig2_quality.png")


def fig_long(R):
    """(a) CE against position with full context; (b) the deployable number at 8K/32K/128K;
    (c) what context beyond the 512-character training window is worth, on identical characters."""
    fig, ax = plt.subplots(1, 3, figsize=(17, 4.4))
    top = 1.25
    for a in C.ARMS:
        es = evals(R, a)
        if not es:
            continue
        edges = np.array(es[0]["long"]["edges"])
        mids = np.sqrt(edges[:-1] * edges[1:])
        cur = np.array([np.mean(e["long"]["curves"], 0) for e in es])
        ax[0].plot(mids, cur.mean(0), color=COL[a], lw=1.5, label=f"{a}, full context")
        ax[0].fill_between(mids, cur.min(0), cur.max(0), color=COL[a], alpha=0.15)
    e2 = evals2(R, "Transformer")
    if e2:
        edges = np.array(e2[0]["window_curves"]["edges"])
        mids = np.sqrt(edges[:-1] * edges[1:])
        cur = np.array([np.nanmean(e["window_curves"]["curves"], 0) for e in e2])
        ax[0].plot(mids, cur.mean(0), "--", color=COL["Transformer"], lw=1.3, label="Transformer, 512 window")
    tcol = [np.mean([e["context"][str(c)]["ce_full"] for e in evals2(R, "Transformer")]) for c in P.long_ctx] \
        if evals2(R, "Transformer") else []
    if tcol:
        ax[0].annotate(f"Transformer, full context: {tcol[0]:.2f} / {tcol[1]:.2f} / {tcol[2]:.2f}\n"
                       "at 8K / 32K / 128K (off scale; RoPE positions\nbeyond 512 were never trained)",
                       xy=(2048, top), xytext=(30, top - 0.17), fontsize=7.5, color=COL["Transformer"],
                       arrowprops=dict(arrowstyle="->", color=COL["Transformer"], lw=0.8))
    ax[0].set_ylim(0.55, top)
    ax[0].axvspan(1, P.seq_len, color="grey", alpha=0.08)
    for c in P.long_ctx:
        ax[0].axvline(c, ls=":", lw=0.8, color="grey")
    ax[0].set_xscale("log")
    ax[0].set_xlabel("position in the stream = context available (characters)")
    ax[0].set_ylabel("CE (nats/char), 4 streams, mean of 3 seeds")
    ax[0].set_title(f"[{TAG}] (a) quality at 16x-256x the training length", fontsize=9)
    ax[0].legend(fontsize=7, loc="lower left")
    keys = [str(c) for c in P.long_ctx]
    wdt = 0.8 / len(C.ARMS)
    for i, a in enumerate(C.ARMS):
        es = evals2(R, a)
        if not es:
            continue
        fld = "ce_window" if a == "Transformer" else "ce_full"
        v = np.array([[e["context"][k][fld] for k in keys] for e in es])
        x = np.arange(len(keys)) + (i - (len(C.ARMS) - 1) / 2) * wdt
        ax[1].bar(x, v.mean(0), wdt, color=COL[a], alpha=0.75,
                  label=a + (" (512 window)" if a == "Transformer" else " (full context)"))
        for j in range(len(keys)):
            ax[1].plot([x[j]] * len(v), v[:, j], ".", color="k", ms=3)
    allv = [e["context"][k]["ce_window" if a == "Transformer" else "ce_full"]
            for a in C.ARMS for e in evals2(R, a) for k in keys]
    if allv:
        ax[1].set_ylim(min(allv) - 0.05, max(allv) + 0.04)
    ax[1].set_xticks(range(len(keys)), ["8K", "32K", "128K"])
    ax[1].set_ylabel("CE over the 4,096 positions ending there")
    ax[1].set_title("(b) the deployable configuration of each arm", fontsize=9)
    ax[1].legend(fontsize=7)
    wr = 0.8 / len(C.RECURRENT)
    for i, a in enumerate(C.RECURRENT):
        es = evals2(R, a)
        if not es:
            continue
        v = np.array([[e["context"][k]["benefit"] for k in keys] for e in es])
        x = np.arange(len(keys)) + (i - (len(C.RECURRENT) - 1) / 2) * wr
        ax[2].bar(x, v.mean(0), wr, color=COL[a], alpha=0.75, label=a)
        for j in range(len(keys)):
            ax[2].plot([x[j]] * len(v), v[:, j], ".", color="k", ms=3)
    ax[2].axhline(0, color="k", lw=0.8)
    ax[2].set_xticks(range(len(keys)), ["8K", "32K", "128K"])
    ax[2].set_ylabel("CE(512 window) - CE(full context)  [nats/char]")
    ax[2].set_title("(c) gain from context beyond 512, same characters\n(> 0: the long state helps; < 0: it drifts)",
                    fontsize=9)
    ax[2].legend(fontsize=7)
    return _save(fig, "fig3_long_context.png")


def fig_retrieval(R):
    """Controlled retrieval: the same final passage scored after a sequence that contained it
    earlier (treated) or contained a different passage in that slot (control)."""
    fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.3))
    Ds = np.array(P.retrieval_gaps)
    for a in C.ARMS:
        es = evals2(R, a)
        if not es:
            continue
        use = Ds if a != "Transformer" else Ds[Ds + 2 * P.needle_len + P.retrieval_pre <= P.seq_len]
        g = np.array([[e["retrieval"][str(D)]["gain"] for D in use] for e in es])
        off = 1 + 0.05 * (C.ARMS.index(a) - (len(C.ARMS) - 1) / 2)
        ax[0].errorbar(use * off, g.mean(0), yerr=g.std(0, ddof=1) if len(g) > 1 else None,
                       fmt="o-", color=COL[a], capsize=3, label=a)
        at = np.array([[e["retrieval"][str(D)]["acc_treated"] for D in use] for e in es]).mean(0)
        ac = np.array([[e["retrieval"][str(D)]["acc_control"] for D in use] for e in es]).mean(0)
        ax[1].plot(use * off, 100 * (at - ac), "o-", color=COL[a], label=a)
    for k in range(2):
        ax[k].axhline(0, color="k", lw=0.8)
        ax[k].axvspan(1, P.seq_len, color="grey", alpha=0.08)
        ax[k].set_xscale("log")
        ax[k].set_xlabel("gap between the passage and its repeat (characters)")
    ax[0].set_ylabel("CE(control) - CE(treated)  [nats/char]")
    ax[0].set_title(f"[{TAG}] (a) controlled retrieval: value of having seen the passage", fontsize=9)
    ax[0].legend(fontsize=8)
    ax[1].set_ylabel("top-1 accuracy, treated - control (points)")
    ax[1].set_title("(b) the same, in accuracy. Shaded: inside the 512 training window.\n"
                    "Transformer shown only where both copies fit its trained positions.", fontsize=9)
    ax[1].legend(fontsize=8)
    return _save(fig, "fig4_retrieval.png")


def fig_efficiency(R):
    sp = R["speed"]["median"]
    ctx = np.array(P.speed_ctx)
    fig, ax = plt.subplots(1, 4, figsize=(17, 4.0))
    for a in C.ARMS:
        ok = [str(c) for c in ctx if "oom" not in sp[a][str(c)]]
        cs = np.array([int(c) for c in ok])
        ax[0].plot(cs, [sp[a][c]["prefill_tok_s"] for c in ok], "o-", color=COL[a], label=a)
        ax[1].plot(cs, [sp[a][c]["decode_graph_tok_s"] for c in ok], "o-", color=COL[a], label=f"{a} (CUDA graphs)")
        ax[1].plot(cs, [sp[a][c]["decode_eager_tok_s"] for c in ok], "x:", color=COL[a], alpha=0.6)
        ax[2].plot(cs, [sp[a][c]["peak_prefill_mb"] for c in ok], "o-", color=COL[a], label=a)
        ax[3].plot(cs, [sp[a][c]["state_kb"] / 1024 for c in ok], "o-", color=COL[a], label=a)
    titles = [f"[{TAG}] (a) prefill throughput", "(b) decode, batch 1 (dotted: eager)",
              "(c) peak working memory of prefill", "(d) decode state carried per stream"]
    ylab = ["tokens / s", "tokens / s", "MB above the weights", "MB (log)"]
    for i in range(4):
        ax[i].set_xscale("log", base=2)
        ax[i].set_xlabel("context (characters)")
        ax[i].set_ylabel(ylab[i])
        ax[i].set_title(titles[i], fontsize=9)
        ax[i].legend(fontsize=7)
    ax[1].set_yscale("log")
    ax[3].set_yscale("log")
    return _save(fig, "fig5_efficiency.png")


# --------------------------------------------------------------------------- RD-S4 v2 and SPOC
def load_extra(R):
    R["ablate"] = C.load_json("ablate_v2.json")
    R["dream"] = C.load_json("dream_RD-S4_v2.json")
    R["pc"] = C.load_json("pc_cost.json")
    R["speed_compiled"] = C.load_json("speed_compiled.json")
    R["pc_steps"] = C.load_json("pc_steps.json")
    R["pc_precision"] = C.load_json("pc_precision.json")
    return R


def run_clock(r):
    """Seconds of training per step, excluding one-off compilation (recorded as first_step_s)."""
    steps, wall = r["steps"], r["wall_s"]
    first = r.get("first_step_s")
    return (wall - first) / max(1, steps - 1) if first is not None else wall / steps


def time_to_quality(R, target_arm="RD-S4"):
    """Training compute and wall-clock each arm needs before its held-out curve (mean of 3 seeds, 64 selection
    windows every 100 steps) first reaches the final quality of `target_arm`."""
    tgt = np.mean([r["hist"]["curve_ce"][-1] for r in final_runs(R, target_arm)])
    out = {"target_arm": target_arm, "target_curve_ce": float(tgt), "arms": {}}
    for a in C.ARMS:
        runs = final_runs(R, a)
        if not runs:
            continue
        n = min(len(r["hist"]["curve_ce"]) for r in runs)
        cur = np.mean([r["hist"]["curve_ce"][:n] for r in runs], 0)
        steps = np.array(runs[0]["hist"]["eval_step"][:n])
        hit = np.nonzero(cur <= tgt)[0]
        # median over seeds: robust to a run slowed by the laptop's battery power cap
        rec = {"final_curve_ce": float(cur[-1]), "sec_per_step": float(np.median([run_clock(r) for r in runs])),
               "steps": runs[0]["steps"]}
        if len(hit):
            s = int(steps[hit[0]])
            rec.update({"step": s, "budget_fraction": s / runs[0]["steps"],
                        "minutes": s * rec["sec_per_step"] / 60,
                        "pflop": s * R["plan"]["arms"][a]["per_step"] / 1e15})
        rec["full_run_minutes"] = rec["steps"] * rec["sec_per_step"] / 60
        out["arms"][a] = rec
    return out


def fig_time_to_quality(R):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
    ttq = time_to_quality(R)
    for a in C.ARMS:
        runs = final_runs(R, a)
        if not runs:
            continue
        n = min(len(r["hist"]["curve_ce"]) for r in runs)
        cur = np.mean([r["hist"]["curve_ce"][:n] for r in runs], 0)
        steps = np.array(runs[0]["hist"]["eval_step"][:n])
        sps = ttq["arms"][a]["sec_per_step"]
        ax[0].plot(steps * sps / 60, cur, color=COL[a], lw=1.6, label=f"{a} ({sps * 1e3:.0f} ms/step)")
        if "minutes" in ttq["arms"][a]:
            ax[0].plot(ttq["arms"][a]["minutes"], ttq["target_curve_ce"], "o", color=COL[a], ms=6)
    ax[0].axhline(ttq["target_curve_ce"], ls="--", lw=0.8, color="grey")
    ax[0].text(0.2, ttq["target_curve_ce"] + 0.01, "final quality of RD-S4 v1", fontsize=8, color="grey")
    ax[0].set_ylim(0.6, 1.2)
    ax[0].set_xlabel("training wall-clock on the RTX 5050 (minutes, compilation excluded)")
    ax[0].set_ylabel("held-out CE (selection split)")
    ax[0].set_title(f"[{TAG}] (a) quality against training time, mean of 3 seeds", fontsize=9)
    ax[0].legend(fontsize=7)
    arms = [a for a in C.ARMS if "minutes" in ttq["arms"].get(a, {})]
    ax[1].bar(range(len(arms)), [100 * ttq["arms"][a]["budget_fraction"] for a in arms],
              color=[COL[a] for a in arms], alpha=0.75)
    for i, a in enumerate(arms):
        r = ttq["arms"][a]
        ax[1].text(i, 100 * r["budget_fraction"], f"{100 * r['budget_fraction']:.0f}%\n{r['minutes']:.1f} min",
                   ha="center", va="bottom", fontsize=8)
    ax[1].set_xticks(range(len(arms)), arms)
    ax[1].set_ylim(0, 118)
    ax[1].set_ylabel("share of the FLOP budget needed (%)")
    ax[1].set_title("(b) compute and time to reach RD-S4 v1's final quality", fontsize=9)
    return _save(fig, "fig6_time_to_quality.png"), ttq


def dream_table(R):
    """Mean and s.d. over seeds of every day-dreaming method's final state, and its compute."""
    d = R.get("dream")
    if not d:
        return {}
    out = {}
    for m in d["methods"]:
        runs = [v for k, v in d["runs"].items() if k.split("|")[0] == m]
        if not runs:
            continue
        f = lambda key, ep=-1: [r["curve"][ep][key] for r in runs]
        out[m] = {"n": len(runs),
                  "held_ce": msd(f("held_ce")), "held_ce_base": msd(f("held_ce", 0)),
                  "teach_ce": msd(f("teach_ce")),
                  "forgetting": msd([a - b for a, b in zip(f("old_ce"), f("old_ce", 0))]),
                  "learned": msd([b - a for a, b in zip(f("held_ce"), f("held_ce", 0))]),
                  "backward_windows": msd(f("backward_windows")), "screen_windows": msd(f("screen_windows")),
                  "wall_s": msd(f("wall_s"))}
    return out


def dream_frontier(R, limits=(0.01, 0.05, 0.10, 0.25)):
    """Stability-plasticity frontier of each family: the best held-out CE (mean over seeds) reached at any pass
    by any of its settings, subject to forgetting (TinyStories CE increase, mean over seeds) <= limit."""
    d = R.get("dream")
    if not d:
        return {}
    fam = {"fine-tuning (any learning rate, any layers)": [m for m in d["methods"] if m.startswith("fine-tune")],
           "surprise gate alone": ["surprise gate"],
           "SPOC: consolidation (+ gate), any alpha": [m for m in d["methods"]
                                                      if m.startswith("SPOC") or m == "orthogonal consolidation"]}
    out = {}
    for f, ms in fam.items():
        pts = []
        for m in ms:
            runs = [v for k, v in d["runs"].items() if k.split("|")[0] == m]
            if not runs:
                continue
            n = min(len(r["curve"]) for r in runs)
            for e in range(n):
                held = np.mean([r["curve"][e]["held_ce"] for r in runs])
                forg = np.mean([r["curve"][e]["old_ce"] - r["curve"][0]["old_ce"] for r in runs])
                pts.append((forg, held, m, e))
        out[f] = {}
        for lim in limits:
            ok = [p for p in pts if p[0] <= lim]
            if ok:
                b_ = min(ok, key=lambda p: p[1])
                out[f][str(lim)] = {"held_ce": float(b_[1]), "forgetting": float(b_[0]), "method": b_[2], "pass": b_[3]}
    return out


DREAM_STYLE = {"fine-tune": ("tab:gray", "o"), "fine-tune, lr/3": ("silver", "o"),
               "fine-tune, linear layers": ("tab:brown", "s"), "surprise gate": ("tab:purple", "^"),
               "orthogonal consolidation": ("tab:cyan", "D"), "SPOC (gate + consolidation)": ("tab:red", "*"),
               "SPOC, alpha 0.1": ("salmon", "*"), "fine-tune, lr/10": ("gainsboro", "o"),
               "SPOC, alpha 0.03": ("firebrick", "*"), "SPOC, alpha 0.3": ("lightsalmon", "*")}


def fig_dream(R):
    d = R.get("dream")
    if not d:
        return None
    fig, ax = plt.subplots(1, 3, figsize=(17, 4.3))
    for m in d["methods"]:
        runs = [v for k, v in d["runs"].items() if k.split("|")[0] == m]
        if not runs:
            continue
        col, mk = DREAM_STYLE.get(m, ("k", "o"))
        ep = np.array([c["epoch"] for c in runs[0]["curve"]])
        held = np.array([[c["held_ce"] for c in r["curve"]] for r in runs])
        forg = np.array([[c["old_ce"] - r["curve"][0]["old_ce"] for c in r["curve"]] for r in runs])
        bw = np.array([[c["backward_windows"] for c in r["curve"]] for r in runs]).mean(0)
        ax[0].plot(bw, held.mean(0), marker=mk, ms=4, color=col, label=m)
        ax[1].plot(ep, forg.mean(0), marker=mk, ms=4, color=col, label=m)
        ax[2].plot(forg.mean(0), held.mean(0), marker=mk, ms=4, color=col, label=m)
    ax[0].set_xlabel("windows learned with a backward pass (compute)")
    ax[0].set_ylabel("held-out Shakespeare CE (never taught)")
    ax[0].set_title("[RD-S4 v2] (a) learning the new text, per unit of compute", fontsize=9)
    ax[1].axhline(0, color="k", lw=0.8)
    ax[1].set_xlabel("teaching pass over the play")
    ax[1].set_ylabel("TinyStories CE increase (forgetting)")
    ax[1].set_title("(b) what the model forgets while it learns", fontsize=9)
    ax[2].set_xlabel("forgetting (TinyStories CE increase)")
    ax[2].set_ylabel("held-out Shakespeare CE")
    ax[2].set_title("(c) trade-off; lower-left is better, every point one pass", fontsize=9)
    for k in range(3):
        ax[k].legend(fontsize=6.5)
    return _save(fig, "fig8_day_dreaming.png")


def fig_spoc(R):
    """The three SPOC questions on RD-S4 v2: gate in pre-training, predictive coding instead of backprop,
    teaching without forgetting."""
    fig, ax = plt.subplots(1, 3, figsize=(17, 4.3))
    ab = R.get("ablate") or {}
    g = ab.get("gate")
    if g:
        base = R["runs"].get(("RD-S4 v2", g["lr"], g["seed"]))
        names = ["RD-S4 v2\n(plain sampling)", "RD-S4 v2\n+ SPOC surprise gate"]
        vals = [base["select_ce"], g["select_ce"]] if base else [float("nan"), g["select_ce"]]
        toks = [base["tokens"] / 1e6 if base else float("nan"), g["tokens_trained"] / 1e6]
        ax[0].bar([0, 1], vals, color=["tab:red", "tab:purple"], alpha=0.75)
        for i, (v, t) in enumerate(zip(vals, toks)):
            ax[0].text(i, v, f"{v:.4f}\n{t:.1f} M chars learned", ha="center", va="bottom", fontsize=8)
        ax[0].set_xticks([0, 1], names)
        ax[0].set_ylim(min(vals) - 0.05, max(vals) + 0.06)
        ax[0].set_ylabel("held-out CE (selection split), seed 0")
    ax[0].set_title("[RD-S4 v2] (a) surprise gate in pre-training, equal FLOPs\n(screening is charged)", fontsize=9)
    pc = R.get("pc")
    if pc:
        labels, ratio, cos, cols = ["backprop"], [1.0], [1.0], ["tab:red"]
        for key, name, col in (("pc", "PC", "tab:green"), ("pc_small", "PC, small\noutput error", "tab:cyan"),
                               ("pc_fpa", "PC-FPA", "tab:olive")):
            for T, r in pc.get(key, {}).items():
                if int(T) not in (1, 7, 24):
                    continue
                labels.append(f"{name}\nT={T}")
                ratio.append(r["time_ratio"])
                cos.append(r["cosine_to_backprop"])
                cols.append(col)
        ax[1].bar(range(len(labels)), ratio, color=cols, alpha=0.75)
        for i, (r_, c_) in enumerate(zip(ratio, cos)):
            ax[1].text(i, r_, f"{r_:.1f}x\ncos {c_:+.2f}", ha="center", va="bottom", fontsize=7)
        ax[1].set_xticks(range(len(labels)), labels, fontsize=7, rotation=45, ha="right")
        ax[1].set_ylabel("GPU time per weight update / backprop")
        ax[1].set_ylim(0, max(ratio) * 1.25)
    ax[1].set_title("(b) predictive-coding relaxation instead of backprop\n(cos = alignment of the update with "
                    "the exact gradient)", fontsize=9)
    dt = dream_table(R)
    for m, r in dt.items():
        col, mk = DREAM_STYLE.get(m, ("k", "o"))
        ax[2].errorbar(r["forgetting"][0], r["held_ce"][0], xerr=r["forgetting"][1], yerr=r["held_ce"][1],
                       fmt=mk, color=col, ms=9 if mk == "*" else 6, capsize=2, label=m)
    if dt:
        base = np.mean([r["held_ce_base"][0] for r in dt.values()])
        ax[2].axhline(base, ls=":", color="grey", lw=0.8)
        ax[2].text(ax[2].get_xlim()[0], base, " before teaching", fontsize=7, color="grey", va="bottom")
    ax[2].axvline(0, color="k", lw=0.8)
    ax[2].set_xlabel("forgetting: TinyStories CE increase")
    ax[2].set_ylabel("held-out Shakespeare CE after teaching")
    ax[2].set_title("(c) day-dreaming: learn new text, keep the old\n(mean ± s.d., 3 trained models)", fontsize=9)
    ax[2].legend(fontsize=6.5)
    return _save(fig, "fig7_spoc.png")


def jepa_ablation(R):
    ab = R.get("ablate") or {}
    nj = [v["test_ce"] for v in ab.get("no_jepa", {}).values()]
    wj = [e["test"]["ce"] for e in evals(R, "RD-S4 v2")]
    if not nj or not wj:
        return None
    return {"with_jepa": msd(wj), "without_jepa": msd(nj), "diff": float(np.mean(wj) - np.mean(nj)),
            "p_one_sided": perm_test(wj, nj, "less"), "p_two_sided": perm_test(wj, nj)}


def make_all():
    R = load_extra(load_all())
    figs = [fig_training(R), fig_quality(R), fig_long(R), fig_retrieval(R)]
    if R.get("speed"):
        figs.append(fig_efficiency(R))
    figs.append(fig_time_to_quality(R)[0])
    figs.append(fig_spoc(R))
    if R.get("dream"):
        figs.append(fig_dream(R))
    txt = scorecard_text(R)
    with open(C.rpath("scorecard.txt"), "w") as f:
        f.write(txt + "\n")
    C.save_json("significance.json", significance(R))
    return R, figs, txt


if __name__ == "__main__":
    _, _, t = make_all()
    print(t)
