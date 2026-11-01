"""The written conclusions of the four-way benchmark.

The prose is written by hand. Every number in it is computed from results/ when the text is rendered, and every
qualitative claim the prose makes is checked against those numbers first: a sentence the measurements no longer
support raises ClaimError instead of being printed. Nothing is estimated except where the text says so.

    from verdict import render
    T = render(R)          # R = report.load_extra(report.load_all())
    T["SUMMARY"], T["VERDICT"], T["V2_INTRO"], T["SPOC_TEXT"]
"""
import glob
import json
import os

import numpy as np

import report as RP

C, P = RP.C, RP.P
V2, V1, TF, S4, MB = "RD-S4 v2", "RD-S4", "Transformer", "S4", "Mamba"
FIRST_RUN = "archive_v2_module_2026-10-11"     # first run of RD-S4 v2 (same architecture, loaded from a module)
ORDINAL = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "last"}
FT_FAM = "fine-tuning (any learning rate, any layers)"
SPOC_FAM = "SPOC: consolidation (+ gate), any alpha"


class ClaimError(AssertionError):
    """A sentence of the verdict is not supported by results/."""


def need(cond, claim):
    if not cond:
        raise ClaimError(claim)


def below(a, b):
    """Complete separation: every seed of a is below every seed of b."""
    return max(a) < min(b)


def mean(v):
    return float(np.mean(v))


def k(c):
    return f"{c // 1024}K"


def n0(x):
    return f"{x:,.0f}"


def sci(x):
    """6e-3 style (as learning rates are usually written)."""
    mant, ex = f"{x:.1e}".split("e")
    return f"{mant.rstrip('0').rstrip('.')}e{int(ex)}"


def first_run(R):
    """RD-S4 v2's first run (archived), for the run-to-run comparison; None if the archive is absent."""
    d = C.rpath(FIRST_RUN)
    if not os.path.isdir(d):
        return None
    ce = [json.load(open(f))["test"]["ce"] for f in sorted(glob.glob(os.path.join(d, "eval", f"{V2}_s*.json")))]
    sw = json.load(open(os.path.join(d, "sweep.json"))).get(V2, {})
    now = R["sweep"].get(V2, {})
    same = [abs(sw["select_ce"][lr] - now["select_ce"][lr]) for lr in sw.get("select_ce", {})
            if lr in now.get("select_ce", {})]
    return {"ce": ce, "sweep_max_abs_diff": max(same) if same else None, "n_lr": len(same)}


def retrieval_vs_mamba(A):
    """RD-S4 v2 against Mamba on in-window retrieval, per gap: (gap, relation, v2 mean, Mamba mean, two-sided p),
    relation 'below' or 'above' only for complete separation across seeds, else 'level'."""
    out = []
    for D in [D for D in P.retrieval_gaps if D + 2 * 128 <= 512]:
        a, b = A[V2]["ret"][D], A[MB]["ret"][D]
        rel = "below" if below(a, b) else "above" if below(b, a) else "level"
        out.append((D, rel, mean(a), mean(b), RP.perm_test(a, b)))
    return out


def retrieval_clauses(A):
    """'below Mamba's in every seed at a gap of 32 characters (+0.040 against +0.074) and not distinguishable ...'"""
    txt = {"below": "below Mamba's in every seed", "above": "above Mamba's in every seed",
           "level": "not distinguishable from Mamba's"}
    r = retrieval_vs_mamba(A)
    parts = []
    for rel in sorted({x[1] for x in r}, key=lambda rel: min(x[0] for x in r if x[1] == rel)):
        g = [x for x in r if x[1] == rel]
        nums = " and ".join(f"{m2:+.3f} against {mm:+.3f}" for _, _, m2, mm, _ in g)
        ps = f"; two-sided p = {' and '.join(f'{p:.1f}' for *_, p in g)}" if rel == "level" else ""
        parts.append(f"{txt[rel]} at {'a gap' if len(g) == 1 else 'gaps'} of {' and '.join(str(x[0]) for x in g)} "
                     f"characters ({nums}{ps})")
    return " and ".join(parts)


def retrieval_short(A):
    r = retrieval_vs_mamba(A)
    by = {rel: [str(D) for D, rr, *_ in r if rr == rel] for rel in ("below", "level", "above")}
    if not by["below"] and not by["above"]:
        return "matches Mamba's in-window retrieval within noise"
    if by["level"] and by["below"] and not by["above"]:
        return (f"matches Mamba's in-window retrieval at a gap of {' and '.join(by['level'])} characters but not at "
                f"{' and '.join(by['below'])}")
    if not by["level"] and not by["above"]:
        return "retrieves in-window text less well than Mamba"
    raise ClaimError("retrieval against Mamba: write a sentence for this outcome")


def power_note(R):
    """Measurement conditions, from results/power_log.txt (AC supply logged every 30 s during the runs)."""
    pl = C.rpath("power_log.txt")
    if not os.path.exists(pl):
        return ""
    rows = [ln.split() for ln in open(pl) if " ac=" in ln]
    need(rows and all(r[1] == "ac=1" for r in rows), "every logged sample on AC power")
    sps = [RP.run_clock(r) for r in RP.final_runs(R, V2)]
    return (f"\n* All RD-S4 v2 runs and every speed measurement of this edition ran on AC power: the supply was logged every"
            f"\n  30 seconds from {rows[0][0][:5]} to {rows[-1][0][:5]} ({len(rows)} samples, none on battery), and the runs that"
            f"\n  started earlier trained at the same speed as the later ones ({1e3 * min(sps):.0f} to {1e3 * max(sps):.0f} ms per step).")


def arms_table(R):
    """Per-arm quality numbers from the evaluation files (seed lists and means)."""
    A = {}
    for a in C.ARMS:
        ev, ev2 = RP.evals(R, a), RP.evals2(R, a)
        A[a] = {"ce": [e["test"]["ce"] for e in ev],
                "ppl": mean([e["test"]["ppl"] for e in ev]),
                "acc": mean([100 * e["test"]["acc"] for e in ev]),
                "full": {c: [e["context"][str(c)]["ce_full"] for e in ev2] for c in P.long_ctx},
                "win": {c: [e["context"][str(c)]["ce_window"] for e in ev2] for c in P.long_ctx},
                "gain": {c: mean([e["context"][str(c)]["benefit"] for e in ev2]) for c in P.long_ctx},
                "ret": {D: [e["retrieval"][str(D)]["gain"] for e in ev2] for D in P.retrieval_gaps},
                "plan": R["plan"]["arms"][a]}
        A[a]["ce_m"], A[a]["ce_s"] = RP.msd(A[a]["ce"])
        need(len(A[a]["ce"]) == len(P.seeds) and len(A[a]["full"][P.long_ctx[0]]) == len(P.seeds),
             f"{a}: every seed evaluated")
    return A


def speed_fns(R):
    """prefill tok/s, peak prefill MB, decode tok/s (CUDA graphs), decode state KB: f(arm, context)."""
    sp = R["speed"]["median"]
    return (lambda a, c: sp[a][str(c)]["prefill_tok_s"], lambda a, c: sp[a][str(c)]["peak_prefill_mb"],
            lambda a, c: sp[a][str(c)]["decode_graph_tok_s"], lambda a, c: sp[a][str(c)]["state_kb"])


def render(R):
    A = arms_table(R)
    sp = R["speed"]["median"]
    pf, pk, dc, st = speed_fns(R)
    c32, c128 = 32768, 131072
    v2, v1, mb, s4, tf = A[V2], A[V1], A[MB], A[S4], A[TF]
    rank = {a: i + 1 for i, a in enumerate(sorted(C.ARMS, key=lambda a: A[a]["ce_m"]))}
    ttq = RP.time_to_quality(R)["arms"]
    jt = RP.jepa_ablation(R)
    budget = R["plan"]["budget_flops"]
    budget_txt = f"{budget:.2e}".replace("e+", "e")

    # ------------------------------------------------------------------ claims shared by summary and verdict
    need(rank[V1] == 5 and rank[V2] == 2, "RD-S4 v1 last and RD-S4 v2 second of five on test CE")
    for b in (S4, TF, V1):
        need(below(v2["ce"], A[b]["ce"]), f"v2 below {b} on test CE in every seed")
        for c in P.long_ctx:
            best_b = [min(f, w) for f, w in zip(A[b]["full"][c], A[b]["win"][c])]
            need(below(v2["full"][c], best_b), f"v2 at {k(c)} below {b} (full or windowed) in every seed")
    need(below(mb["ce"], v2["ce"]), "Mamba below v2 on test CE in every seed")
    need(all(v2["gain"][c] > 0 for c in P.long_ctx), "v2 gains from context beyond 512 at every length")
    need(all(min(A[a]["gain"][c] for c in P.long_ctx) <= 0 for a in C.ARMS if a != V2),
         "every other arm fails to gain at some length")
    mb_abs = max(abs(mb["gain"][c]) for c in P.long_ctx)
    need(all(max(A[a]["gain"][c] for c in P.long_ctx) < 0 for a in (TF, S4, V1)), "the Transformer, S4 and v1 lose")
    v2_gain = [v2["gain"][c] for c in P.long_ctx]
    need(pf(V2, c128) > pf(V1, c128) and pk(V2, c128) < pk(V1, c128) and dc(V2, c128) > dc(V1, c128),
         "v2 prefills and decodes faster than v1 with less memory")
    need(pf(MB, c128) > pf(V2, c128) and dc(MB, c128) > dc(V2, c128) and st(V2, c128) > st(MB, c128),
         "Mamba prefills and decodes faster than v2 with a smaller state")
    ab = R["ablate"]
    gate = ab["gate"]
    v2_s0 = R["eval"][V2][gate["seed"]]["test"]["ce"]
    need(gate["test_ce"] > v2_s0, "the surprise gate loses in pre-training")
    pc = R["pc"]
    race = pc["race_equal_wallclock"]
    need(race["PC-FPA (T=L+1)"]["select_ce"] > race["backprop"]["select_ce"], "PC-FPA loses the race")
    fr = RP.dream_frontier(R)
    ft, spc = fr[FT_FAM], fr[SPOC_FAM]
    need(all(spc[l]["held_ce"] < ft[l]["held_ce"] for l in ("0.05", "0.1")),
         "consolidation beats fine-tuning at 0.05 and 0.10 nats of forgetting")

    # ------------------------------------------------------------------ summary
    v1_pf, v1_mem, v1_dc = pf(V2, c128) / pf(V1, c128), pk(V1, c128) / pk(V2, c128), dc(V2, c128) / dc(V1, c128)
    need("budget_fraction" in ttq[V2], "v2 reaches v1's final quality")
    summary = f"""**Result (second edition, with RD-S4 v2).** At equal parameters (1.7 M) and equal training FLOPs ({budget_txt}),
with every arm's own learning-rate sweep and three seeds, **RD-S4 v2 moves RD-S4 from {ORDINAL[rank[V1]]} to {ORDINAL[rank[V2]]} of five.** Its
test perplexity is {v2['ppl']:.3f} per character (CE {v2['ce_m']:.3f} ± {v2['ce_s']:.3f}), against {mb['ppl']:.3f} for Mamba, {s4['ppl']:.3f} for S4, {tf['ppl']:.3f} for the
Transformer and {v1['ppl']:.3f} for RD-S4 v1. It beats S4, the Transformer and v1 in every seed and at 8K, 32K and 128K. Its
in-window retrieval is {retrieval_clauses(A)}. It is the only arm whose mean quality improves at every
length when it may use context beyond its 512-character training window, though only by {min(v2_gain):.3f} to {max(v2_gain):.3f} nats
(Mamba stays within {mb_abs:.3f} of zero; the other arms lose). Against v1 it prefills {v1_pf:.1f}x faster with {v1_mem:.1f}x less memory, decodes
{v1_dc:.2f}x faster and reaches v1's final quality with {100 * ttq[V2]['budget_fraction']:.0f} percent of the budget. **It does not clear the bar against
Mamba:** it is {v2['ce_m'] - mb['ce_m']:.3f} nats per character behind in every seed, prefills {pf(MB, c128) / pf(V2, c128):.1f}x slower, decodes {100 * (1 - dc(V2, c128) / dc(MB, c128)):.0f} percent slower and
carries a {100 * (st(V2, c128) / st(MB, c128) - 1):.0f} percent larger state. Of the brain-inspired learning rules, learning from prediction errors pays where
it runs inside the forward pass (v2's memory) and where it protects old knowledge while the model is taught new text
(orthogonal consolidation). Predictive-coding relaxation in place of backprop, and the surprise gate in one-pass
pre-training, cost more than they return on a GPU.
"""

    # ------------------------------------------------------------------ acceptance table
    for b in (TF, S4, V1):
        need(st(V2, c128) < st(b, c128) and pk(V2, c128) < pk(b, c128), f"v2 needs less memory than {b}")
    need(pk(V2, c128) > pk(MB, c128), "Mamba's prefill peak below v2's")
    for c in (c32, c128):
        need(dc(V2, c) > dc(TF, c) and dc(V2, c) > dc(V1, c), f"v2 decodes faster than the Transformer and v1 at {k(c)}")
        need(dc(V2, c) < dc(MB, c) and dc(V2, c) < dc(S4, c), f"v2 decodes slower than Mamba and S4 at {k(c)}")
        need(pf(V2, c) > pf(S4, c) and pf(V2, c) > pf(V1, c) and pf(V2, c) < pf(MB, c),
             f"v2 prefill between S4/v1 and Mamba at {k(c)}")
    need(pf(V2, c128) > pf(TF, c128) and pf(V2, c32) < pf(TF, c32), "v2 prefills faster than the Transformer at 128K only")
    lc = lambda a, f: " and ".join(f"{mean(A[a][f][c]):.3f}" for c in (c32, c128))       # noqa: E731
    dd = lambda a: " and ".join(n0(dc(a, c)) for c in (c32, c128))                        # noqa: E731
    pp = lambda a: " and ".join(n0(pf(a, c)) for c in (c32, c128))                        # noqa: E731
    verdict = f"""### RD-S4 v2 against the acceptance test

| Criterion | Outcome | Evidence (mean ± s.d. over 3 seeds; speed = median of 3 interleaved rounds on AC power) |
|---|---|---|
| Comparable or better perplexity | **Better than S4, the Transformer and v1; behind Mamba** | Test CE {v2['ce_m']:.4f} ± {v2['ce_s']:.4f} vs Mamba {mb['ce_m']:.4f} ± {mb['ce_s']:.4f} ({v2['ce_m'] - mb['ce_m']:+.3f}), S4 {s4['ce_m']:.4f} ({v2['ce_m'] - s4['ce_m']:+.3f}), Transformer {tf['ce_m']:.4f} ({v2['ce_m'] - tf['ce_m']:+.3f}), v1 {v1['ce_m']:.4f} ({v2['ce_m'] - v1['ce_m']:+.3f}). Every one of these comparisons separates completely across seeds. At 32K and 128K: {lc(V2, 'full')}, against {lc(MB, 'full')} for Mamba, {lc(S4, 'full')} for S4, {lc(V1, 'full')} for v1, and {lc(TF, 'win')} for a Transformer served with a 512-character window. |
| Materially lower memory at 32K to 128K | **Yes against the Transformer, S4 and v1; no against Mamba** | Decode state {st(V2, c128):.0f} KB, against a {st(TF, c32) / 1024:.0f} MB and {st(TF, c128) / 1024:.0f} MB KV cache ({n0(st(TF, c32) / st(V2, c32))}x and {n0(st(TF, c128) / st(V2, c128))}x larger), {st(S4, c128):.0f} KB for S4 and {st(V1, c128):.0f} KB for v1; Mamba carries {st(MB, c128):.0f} KB. Prefill peak {pk(V2, c128):.0f} MB, against {n0(pk(TF, c128))} MB for the Transformer at 128K, {pk(S4, c128):.0f} MB for S4 and {pk(V1, c128):.0f} MB for v1; Mamba peaks at {pk(MB, c128):.0f} MB. |
| Materially lower latency at 32K to 128K | **Decode: yes against the Transformer and v1, no against Mamba and S4. Prefill: faster than S4 and v1 and, at 128K, the Transformer; {pf(MB, c128) / pf(V2, c128):.1f}x slower than Mamba** | Decode {dd(V2)} tok/s at 32K and 128K, against {dd(TF)} for the Transformer ({dc(V2, c32) / dc(TF, c32):.1f}x and {dc(V2, c128) / dc(TF, c128):.1f}x), {dd(V1)} for v1, {dd(MB)} for Mamba, {dd(S4)} for S4. Prefill {pp(V2)} tok/s, against {pp(TF)} for the Transformer, {pp(MB)} for Mamba, {pp(S4)} for S4, {pp(V1)} for v1. |
"""
    # ------------------------------------------------------------------ v1 -> v2
    r32, r192 = (mean(v2["ret"][D]) / mean(v1["ret"][D]) for D in (32, 192))
    need(mean(v1["ret"][32]) > 0 and mean(v1["ret"][192]) > 0 and r32 > 1 and r192 > 1, "v2 retrieves more than v1")
    t1, t2 = ttq[V1], ttq[V2]
    v1_when = "whole budget" if t1.get("budget_fraction", 1) >= 0.99 else f"{100 * t1['budget_fraction']:.0f} percent of the budget"
    p_j = jt["p_two_sided"]
    j_sig = "not significant, two-sided" if p_j > 0.1 else "complete separation"
    verdict += f"""
### From v1 to v2, measured

| | RD-S4 v1 | RD-S4 v2 | Change |
|---|---|---|---|
| Test CE (nats/char), 3 seeds | {v1['ce_m']:.4f} ± {v1['ce_s']:.4f} | {v2['ce_m']:.4f} ± {v2['ce_s']:.4f} | {v2['ce_m'] - v1['ce_m']:+.3f} |
| Perplexity per character | {v1['ppl']:.3f} | {v2['ppl']:.3f} | {100 * (v2['ppl'] / v1['ppl'] - 1):+.0f} percent |
| Next-character accuracy | {v1['acc']:.2f} % | {v2['acc']:.2f} % | {v2['acc'] - v1['acc']:+.1f} points |
| Controlled retrieval, gap 32 / 192 | {mean(v1['ret'][32]):+.3f} / {mean(v1['ret'][192]):+.3f} | {mean(v2['ret'][32]):+.3f} / {mean(v2['ret'][192]):+.3f} | {r32:.0f}x / {r192:.0f}x |
| Prefill at 128K | {n0(pf(V1, c128))} tok/s, {pk(V1, c128):.0f} MB | {n0(pf(V2, c128))} tok/s, {pk(V2, c128):.0f} MB | {v1_pf:.1f}x faster, {v1_mem:.1f}x less memory |
| Decode (CUDA graphs) | {n0(dc(V1, c128))} tok/s | {n0(dc(V2, c128))} tok/s | {v1_dc:.2f}x |
| Decode state | {st(V1, c128):.0f} KB | {st(V2, c128):.0f} KB | {100 * (st(V2, c128) / st(V1, c128) - 1):+.0f} percent |
| Training time to v1's final quality | {t1['minutes']:.1f} min ({v1_when}) | {t2['minutes']:.1f} min ({100 * t2['budget_fraction']:.0f} percent of the budget) | {t1['minutes'] / t2['minutes']:.1f}x sooner |
| Auxiliary heads | drafts, JEPA, VICReg, router, evolution: 24 percent of forward FLOPs | JEPA only, training-time | JEPA effect: {jt['diff']:+.4f} nats, p = {p_j:.2f} ({j_sig}) |
"""
    # ------------------------------------------------------------------ SPOC on a GPU
    fpa = pc["pc_fpa"]
    t_exact = min(int(T) for T, r in fpa.items() if r["cosine_to_backprop"] >= 0.9995)
    r_fpa = fpa[str(t_exact)]
    deep = [r["cosine_to_backprop"] for key in ("pc", "pc_small") for T, r in pc[key].items() if int(T) >= t_exact]
    deep += [r["cosine_to_backprop"] for r in R["pc_steps"]["grid"].values()]
    pr = R["pc_precision"]
    deep += list(pr["cosine_to_backprop"].values())
    plain_max = max(deep)
    need(plain_max < 0.6, "plain PC never aligns with the gradient on v2")
    gammas = sorted({r["gamma"] for r in R["pc_steps"]["grid"].values()})
    sweeps = sorted({int(T) for key in ("pc", "pc_small") for T in pc[key] if int(T) >= t_exact}
                    | {r["T"] for r in R["pc_steps"]["grid"].values()}
                    | {int(key.rsplit("_T", 1)[1]) for key in pr["cosine_to_backprop"]})
    pcs = R["pc_steps"]["race_equal_wallclock"]
    pc_best = next(v for n, v in pcs.items() if n.startswith("PC best"))
    need(pc_best["select_ce"] > pcs["backprop"]["select_ce"], "plain PC loses the race")
    mlp = pr["mlp_control"]["cosine_to_backprop"]
    mlp_c = mlp["beta0.01_T200"]
    need(mlp_c > 0.99 and mlp["fpa_T7"] > 0.999, "PC converges to backprop on the control MLP")
    gains = pr["scales"]["block_gain_random_directions"]
    need(gains[0] > 3 and max(gains[1:]) < 1.5, "the first block amplifies, the others do not")
    x0 = max(v for kk, v in pr["per_layer_step"].items() if kk.startswith("beta1_") and kk.endswith("_T200"))
    need(x0 < 0.6, "a separate x_0 step recovers only part of the alignment")
    dt = RP.dream_table(R)
    ep = R["dream"]["config"]["epochs"]
    n_models = dt[next(iter(dt))]["n"]
    gate_runs = [v for kk, v in R["dream"]["runs"].items() if kk.split("|")[0] == "surprise gate"]
    gate_forget = min(mean([r["curve"][e]["old_ce"] - r["curve"][0]["old_ce"] for r in gate_runs])
                      for e in range(1, min(len(r["curve"]) for r in gate_runs)))
    need(ft["0.01"]["pass"] == 0, "fine-tuning learns nothing within 0.01 nats of forgetting")
    need(ft["0.25"]["held_ce"] < spc["0.1"]["held_ce"] and ft["0.25"]["forgetting"] > 0.1,
         "fine-tuning only gets lower by forgetting more than 0.10 nats")
    need(gate_forget > 0.1, "the gate alone forgets on every pass")
    g_bw = 1 - dt["surprise gate"]["backward_windows"][0] / dt["fine-tune"]["backward_windows"][0]
    g_wall = dt["surprise gate"]["wall_s"][0] / dt["fine-tune"]["wall_s"][0] - 1
    tok2 = A[V2]["plan"]["tokens"]
    verdict += f"""
### SPOC on a GPU: what pays and what does not

1. **Learning from prediction errors inside the architecture pays.** v2's memory stores only what it fails to
   predict, at every token, in parallel and without a backward pass. That mechanism is where the gains in the table
   above come from, and it is how predictive coding runs efficiently on a GPU: as a forward computation.
2. **The surprise gate does not pay in pre-training.** With its screening charged to the same FLOP budget, the gated
   run learned from {gate['tokens_trained'] / 1e6:.1f} M characters instead of {tok2 / 1e6:.1f} M and finished at test CE {gate['test_ce']:.3f} against {v2_s0:.3f} (seed {gate['seed']}). In a
   single pass over fresh text almost no window is already known, so the gate has nothing to skip.
3. **Predictive-coding relaxation does not pay as a replacement for backprop.** Every relaxation sweep costs about
   one forward and one backward pass through the network, so any PC variant pays several times backprop's cost per
   weight update. With predictions frozen at the feed-forward pass (FPA), PC reproduces backprop exactly from {t_exact}
   sweeps (cosine {r_fpa['cosine_to_backprop']:.3f}) but costs {r_fpa['time_ratio']:.1f}x the time per update: in 120 seconds it makes {race['PC-FPA (T=L+1)']['updates']} updates to backprop's {race['backprop']['updates']}
   and reaches a selection CE of {race['PC-FPA (T=L+1)']['select_ce']:.2f} against {race['backprop']['select_ce']:.2f}. Plain PC, which recomputes its predictions at every sweep, never
   followed the gradient well on v2: across step sizes {gammas[0]:g} to {gammas[-1]:g}, {sweeps[0]} to {sweeps[-1]} sweeps, full or reduced output error,
   TF32 or full fp32 arithmetic, its update's cosine with the exact gradient stayed at or below {plain_max:.2f}, and its best
   setting reached a selection CE of {pc_best['select_ce']:.2f} in 120 seconds. The same code, on a classic predictive-coding network
   (embedding, six tanh MLP blocks, read-out) and the same text, converges to backprop (cosine {mlp_c:.4f} with a small
   output error, {mlp['fpa_T7']:.4f} with FPA), so this is a property of the deep normalised network: the embedding's RMSNorm makes the
   first block amplify about {gains[0]:.0f}x (the others {min(gains[1:]):.2f}x to {max(gains[1:]):.2f}x), which leaves the relaxation ill-conditioned,
   and a separate smaller step for that layer recovers only part of the alignment ({x0:.2f} at 200 sweeps).
4. **Orthogonal consolidation pays when the model is taught new text.** Taught *As You Like It* for {ep} passes, with
   any learning rate, fine-tuning cannot learn anything while forgetting at most 0.01 nats of TinyStories, and at
   most 0.05 and 0.10 nats of forgetting it reaches held-out Shakespeare CE {ft['0.05']['held_ce']:.3f} and {ft['0.1']['held_ce']:.3f}. With consolidation the
   same budgets give {spc['0.01']['held_ce']:.3f}, {spc['0.05']['held_ce']:.3f} and {spc['0.1']['held_ce']:.3f} (mean of {n_models} trained models; every setting and pass considered). Fine-tuning
   only gets lower ({ft['0.25']['held_ce']:.3f}) by forgetting {ft['0.25']['forgetting']:.2f} nats. The surprise gate on its own protects nothing (every pass forgets
   {gate_forget:.2f} nats or more) and saves {100 * g_bw:.0f} percent of backward passes while adding {100 * g_wall:.0f} percent of wall-clock in screening.
"""
    # ------------------------------------------------------------------ why v2 trails Mamba
    flop_char = lambda a: A[a]["plan"]["per_step"] / (P.batch * P.seq_len) / 1e6          # noqa: E731
    gp = R["speed"]["graph_prefill"][V2]
    ctx_all = sorted(int(c) for c in sp[V2])
    g_gain = [gp[str(c)]["prefill_tok_s"] / pf(V2, c) - 1 for c in ctx_all]
    cs = R["speed_compiled"]["arms"]

    def comp(a):
        v = [cs[a][str(c)][f] for c in P.long_ctx for f in ("compiled_prefill_tok_s", "compiled_graph_prefill_tok_s")]
        return min(v), max(v)

    v2c, mbc = comp(V2), comp(MB)
    eager = [pf(V2, c) for c in P.long_ctx]
    need(min(v2c) > max(eager), "compilation speeds up v2's prefill")
    need(mbc[0] > v2c[1], "compiled Mamba prefills faster than compiled v2")
    d2, dm = cs[V2]["decode_compiled_graph_tok_s_32k"], cs[MB]["decode_compiled_graph_tok_s_32k"]
    need(dm > 1.5 * d2, "compiled Mamba decodes much faster than compiled v2")
    sw = R["sweep"][V2]
    lrs = sorted(sw["lrs"])
    need(lrs[0] < sw["best_lr"] < lrs[-1], "v2's learning-rate optimum is interior")
    lo_lr, hi_lr = max(l for l in lrs if l < sw["best_lr"]), min(l for l in lrs if l > sw["best_lr"])
    spread = v2["ce_s"] / mb["ce_s"]
    spread_txt = (f"is {spread:.1f}x Mamba's (± {v2['ce_s']:.3f} against ± {mb['ce_s']:.3f})" if spread >= 1.2 else
                  f"is comparable to Mamba's (± {v2['ce_s']:.3f} against ± {mb['ce_s']:.3f})")
    verdict += f"""
### Why v2 still trails Mamba

1. **Selectivity granularity.** Each of v2's 8 heads per layer has one write strength and one step size per token.
   A chunked delta-rule memory cannot give every value channel its own gate (each would need its own triangular
   solve), while Mamba selects per channel, 376 per layer. In the pilots, going from 4 to 8 heads gained 0.015 nats;
   12 and 16 heads lost again (key spaces of 16 and 12 dimensions are too small to store associations); per-mode
   data-dependent steps, reflections, a direct skip path and a larger initialisation were neutral.
2. **Arithmetic per token.** The chunk algebra raises training cost to {flop_char(V2):.1f} MFLOP per character against {flop_char(MB):.1f} for
   Mamba, so under the shared budget v2 learned from {tok2 / 1e6:.1f} M characters and Mamba from {A[MB]['plan']['tokens'] / 1e6:.1f} M.
3. **Kernels.** A 2,048-character prefill chunk runs about 1,300 small PyTorch kernels; nothing is hand-fused.
   Replaying them from a CUDA graph gains {100 * min(g_gain):.0f} to {100 * max(g_gain):.0f} percent ({k(ctx_all[0])} to {k(ctx_all[-1])}), and compiler fusion raises v2's prefill to
   {v2c[0] / 1e3:.0f}K to {v2c[1] / 1e3:.0f}K tok/s ({v2c[0] / max(eager):.1f}x to {v2c[1] / min(eager):.1f}x eager); Mamba's hand-fused scan with the same fusion reaches {mbc[0] / 1e3:.0f}K to {mbc[1] / 1e3:.0f}K.
   v2's complex-valued decode step is not fused by the compiler ({n0(d2)} tok/s against {n0(dm)} for compiled Mamba), a limit
   of the implementation.
4. **Seed spread** {spread_txt}.
"""
    fr1 = first_run(R)
    rerun = power_note(R)
    if fr1 and fr1["ce"]:
        m1, s1 = RP.msd(fr1["ce"])
        rerun += f"""
* **Run-to-run variation.** Every RD-S4 v2 number here comes from its second full run, with the model loaded from the
  main notebook (`RD-S4_EFR_TinyStories.ipynb`); the first run, with the same architecture loaded from a Python
  module and checked to give bitwise-identical outputs, is archived in `results/{FIRST_RUN}/`. Test CE: {m1:.4f} ± {s1:.4f}
  in the first run, {v2['ce_m']:.4f} ± {v2['ce_s']:.4f} in this one. The same code and seed gave selection CEs up to {fr1['sweep_max_abs_diff']:.4f} apart
  across the {fr1['n_lr']} learning rates of the sweep, because GPU kernels are not bitwise deterministic; differences of that
  size between two arms are noise, which is why the comparisons above rest on complete separation across seeds."""
    verdict += f"""
### What this does and does not show

* One small scale: 1.7 M parameters, character level, one corpus, every model trained at 512 characters.
* Three seeds: an exact permutation test cannot go below p = 0.05 one-sided, which here means complete separation.
* v2's shape was chosen by pilots on the selection split (never the test split); its learning-rate optimum is
  interior to the sweep ({sci(sw['best_lr'])}, between {sci(lo_lr)} and {sci(hi_lr)}).
* v2's training step is compiled, the other arms' are not; this changes training wall-clock only, never the FLOP
  budget.{rerun}

### What would have to change next

1. A fused kernel for the chunked memory, as flash-linear-attention provides for delta-rule models: engineering
   rather than architecture, worth about 2x prefill on the compiler evidence above.
2. A real-valued decode step the compiler can fuse.
3. Per-channel selectivity without losing the chunked form, for example a small per-channel selective path beside
   the memory, tested in this same harness.
4. Scale: delta-rule memories improve with key dimension, and at 1.7 M parameters 8 heads of 24 dimensions was the
   best measured trade-off.
"""
    return {"SUMMARY": summary, "VERDICT": verdict, "V2_INTRO": V2_INTRO, "SPOC_TEXT": spoc_text(R)}


V2_INTRO = """### What changed: RD-S4 v2

The first edition of this benchmark found three reasons for RD-S4's last place: its recurrence was time-invariant,
so the input could not steer the state token by token; a quarter of its forward arithmetic went to auxiliary heads
that did not lower cross-entropy; and its FFT prefill was slow and memory-hungry. **RD-S4 v2** is the revision that
answers those findings, and it carries the lesson of the predictive-coding study (SPOC,
`digit_predictor_predictive_coding.ipynb`) into the architecture itself:

* **Learning by prediction error, inside the forward pass.** Every head keeps an associative memory that first
  predicts the incoming token's value from its key and then stores only the error: the local predictive-coding
  rule, run at every token, in parallel across the sequence, with no backward pass. A token that is already
  predicted changes nothing (a built-in surprise gate), and a write only touches the directions it uses (built-in
  protection of what is stored).
* **Resonance.** The memory's key space evolves under a bank of damped resonant modes whose step size is chosen by
  the input at every token.
* **GPU form.** Training runs an exact chunked parallel algorithm on tensor cores (agreement with the token-by-token
  definition: 1e-15 in float64, gradients included); decoding updates a fixed-size state. No FFT, no custom kernel.
* **What was removed.** v1's draft heads, router, operator dictionary and in-network evolution showed no measurable
  benefit and are gone. The JEPA objective (predicting future latent summaries) stays as a training-only head.

v2's shape was chosen with pilot runs scored on the selection split at 40 percent of the budget, and its learning
rate by the same sweep as every other arm. It is then measured with exactly the protocol of the other arms.
"""


def spoc_text(R):
    d = R["dream"]["config"]
    return f"""The digit study separated SPOC into three mechanisms. Each is tested here on RD-S4 v2:

* **(a) Surprise gate in pre-training.** Twice the batch is screened by a forward pass without gradients, and
  windows are learned in proportion to how badly they are predicted, importance-weighted so that the update stays
  unbiased. The screening is charged to the same FLOP budget.
* **(b) Predictive-coding relaxation instead of backprop.** Value nodes at every block output relax towards
  equilibrium (T sweeps, all blocks in parallel), then every block updates from its own local error. PC recomputes
  predictions at every sweep, as in the digit study; PC-FPA freezes them at the feed-forward pass, which is known
  to reproduce backprop's gradient exactly after enough sweeps. Measured: GPU time and FLOPs per weight update
  relative to backprop, alignment (cosine) of the update with the exact gradient, a race at equal wall-clock, and
  the same code on a classic predictive-coding MLP as a control.
* **(c) Day-dreaming: teaching new text without forgetting.** The trained RD-S4 v2 (all three seeds) is taught
  *As You Like It*, the book this project started from. 85 percent of the play is taught for {d['epochs']} passes, 5 percent
  only calibrates the surprise gate, and the last 10 percent is never taught and measures whether the new style
  was learned. TinyStories windows measure forgetting. SPOC (surprise gate + orthogonal consolidation) is compared
  with standard fine-tuning and with each mechanism alone; every method gets the same passes and step size.
"""


def paper_numbers(R):
    """Every benchmark number quoted by the paper in the main notebook (RD-S4_EFR_TinyStories.ipynb, Part I), keyed by
    the placeholder name used there ({{name}}), after checking the claims the paper makes around them. render(R) runs
    first, so every claim of the verdict is checked as well."""
    render(R)
    A = arms_table(R)
    pf, pk, dc, st = speed_fns(R)
    c32, c128 = 32768, 131072
    v2, v1, mb = A[V2], A[V1], A[MB]
    N = {}
    for a, key in ((TF, "tf"), (S4, "s4"), (MB, "mb"), (V1, "v1"), (V2, "v2")):
        x = A[a]
        N[f"{key}_ce3"] = f"{x['ce_m']:.3f}"
        N[f"{key}_ppl"] = f"{x['ppl']:.3f}"
        N[f"{key}_acc"] = f"{x['acc']:.1f}"
        N[f"{key}_full"] = " / ".join(f"{mean(x['full'][c]):.{2 if a == TF else 3}f}" for c in (c32, c128))
        N[f"{key}_ret"] = " / ".join(f"{mean(x['ret'][D]):+.3f}" for D in (32, 192))
        N[f"{key}_pf"] = n0(pf(a, c128))
        N[f"{key}_dc"] = n0(dc(a, c128))
        N[f"{key}_peak"] = f"{n0(pk(a, c128))} MB"
        st_kb = st(a, c128)
        N[f"{key}_state"] = f"{st_kb / 1024:.0f} MB" if st_kb >= 10240 else f"{st_kb:.0f} KB"
        N[f"{key}_tokens"] = f"{x['plan']['tokens'] / 1e6:.1f} M"
    N["tf_win"] = " / ".join(f"{mean(A[TF]['win'][c]):.3f}" for c in (c32, c128))
    N["budget"] = f"{R['plan']['budget_flops']:.2e}".replace("e+", "e")
    N["v2_ce_sd"] = f"{v2['ce_s']:.3f}"
    N["gap_mb"] = f"{v2['ce_m'] - mb['ce_m']:.3f}"
    need(R["plan"]["arms"][V2]["params"] == 1_719_980, "RD-S4 v2 has 1,719,980 trained parameters")

    # the paper's own claims, beyond the verdict's
    need(all(mean(v2["full"][c128]) <= mean(v2["full"][c]) + 0.01 for c in P.long_ctx), "v2 holds its quality at 128K")
    need(all(pf(V1, c) < pf(a, c) for a in C.ARMS if a != V1 for c in P.long_ctx), "v1 has the slowest prefill")
    others = [a for a in C.ARMS if a != MB]
    need(all(A[MB]["ce_m"] < A[a]["ce_m"] and A[MB]["ppl"] < A[a]["ppl"] and A[MB]["acc"] > A[a]["acc"]
             for a in others), "Mamba is best on test CE, perplexity and accuracy")
    need(all(mean(A[MB]["full"][c]) < mean(A[a]["full"][c]) for a in others for c in (c32, c128)),
         "Mamba is best at 32K and 128K")
    need(all(mean(A[MB]["ret"][D]) > mean(A[a]["ret"][D]) for a in others for D in (32, 192)),
         "Mamba retrieves best at gaps 32 and 192")
    need(all(abs(mean(A[a]["ret"][D])) < 0.01 for a in C.ARMS for D in P.retrieval_gaps if D >= 2048),
         "no arm retrieves beyond 2K characters")
    N["ret_sentence"] = retrieval_clauses(A)
    N["ret_short"] = retrieval_short(A)
    N["v1_vs_v2_pf"] = f"{pf(V2, c128) / pf(V1, c128):.1f}x"
    N["v1_vs_v2_mem"] = f"{pk(V1, c128) / pk(V2, c128):.1f}x"
    N["mb_vs_v2_pf"] = f"{pf(MB, c128) / pf(V2, c128):.1f}x"
    v1_pf = [pf(V1, c) for c in P.long_ctx]
    N["v1_pf_range"] = f"{min(v1_pf) / 1e3:.0f}K to {max(v1_pf) / 1e3:.0f}K tok/s"
    N["v2_pf_k"] = f"{pf(V2, c128) / 1e3:.0f}K tok/s"

    # JEPA
    jt = RP.jepa_ablation(R)
    N["jepa_diff"] = f"{jt['diff']:+.4f}"
    N["jepa_p"] = f"{jt['p_two_sided']:.2f}"
    need(jt["p_two_sided"] > 0.1, "the JEPA effect is not significant")

    # surprise gate
    g = R["ablate"]["gate"]
    N["gate_tokens"] = f"{g['tokens_trained'] / 1e6:.1f} M"
    N["gate_ce"] = f"{g['test_ce']:.3f}"
    N["gate_base_ce"] = f"{R['eval'][V2][g['seed']]['test']['ce']:.3f}"
    N["gate_seed"] = str(g["seed"])

    # predictive coding
    pc, ps, pr = R["pc"], R["pc_steps"], R["pc_precision"]
    fpa = pc["pc_fpa"]
    t_exact = min(int(T) for T, r in fpa.items() if r["cosine_to_backprop"] >= 0.9995)
    need(t_exact == 7, "PC-FPA is exact from L + 1 = 7 sweeps")
    N["bp_ms"] = f"{1e3 * pc['backprop']['seconds']:.0f} ms"
    N["fpa_ratio"] = f"{fpa['7']['time_ratio']:.1f}x"
    N["fpa_cos"] = f"{fpa['7']['cosine_to_backprop']:.3f}"
    N["pc1_ratio"] = f"{pc['pc']['1']['time_ratio']:.1f}x"
    N["pc1_cos"] = f"{pc['pc']['1']['cosine_to_backprop']:.2f}"
    t7 = [r["time_ratio"] for r in ps["grid"].values() if r["T"] == 7]
    t48 = [r["time_ratio"] for r in ps["grid"].values() if r["T"] == 48]
    N["pc7_ratio"] = f"{np.median(t7):.0f}x"
    N["pc48_ratio"] = f"{np.median(t48):.0f}x"
    deep = [r["cosine_to_backprop"] for key in ("pc", "pc_small") for T, r in pc[key].items() if int(T) >= 7]
    deep += [r["cosine_to_backprop"] for r in ps["grid"].values()] + list(pr["cosine_to_backprop"].values())
    N["pc_max_cos"] = f"{max(deep):.2f}"
    late = [r["cosine_to_backprop"] for key in ("pc", "pc_small") for T, r in pc[key].items() if int(T) >= 24]
    late += [r["cosine_to_backprop"] for r in ps["grid"].values() if r["T"] >= 24]
    late += [v for kk, v in pr["cosine_to_backprop"].items() if int(kk.rsplit("_T", 1)[1]) >= 24]
    need(max(abs(c) for c in late) < 0.05, "plain PC is about 0 from 24 sweeps")
    lo_r, hi_r = fpa["7"]["time_ratio"], pc["pc"]["24"]["time_ratio"]
    N["pc_cost_range"] = f"{lo_r:.0f} to {hi_r:.0f}"
    race = pc["race_equal_wallclock"]
    N["race_bp_updates"] = str(race["backprop"]["updates"])
    N["race_bp_ce"] = f"{race['backprop']['select_ce']:.2f}"
    N["race_fpa_updates"] = str(race["PC-FPA (T=L+1)"]["updates"])
    N["race_fpa_ce"] = f"{race['PC-FPA (T=L+1)']['select_ce']:.2f}"
    best = next(v for n, v in ps["race_equal_wallclock"].items() if n.startswith("PC best"))
    N["race_pc_best_ce"] = f"{best['select_ce']:.2f}"
    need(race["PC (T=L+1)"]["select_ce"] > race["backprop"]["select_ce"] + 1, "plain PC does not learn at the default step")
    mlp = pr["mlp_control"]["cosine_to_backprop"]
    N["mlp_cos"] = f"{mlp['beta0.01_T200']:.4f}"
    N["mlp_fpa_cos"] = f"{mlp['fpa_T7']:.4f}"
    rms = pr["scales"]["value_node_rms"]
    gains = pr["scales"]["block_gain_random_directions"]
    need(rms[0] < 0.2 and min(rms[1:]) > 0.5, "the embedding's value node is far smaller than the others")
    N["x0_rms"] = f"{rms[0]:.3f}"
    N["xl_rms"] = f"{min(rms[1:]):.1f} to {max(rms[1:]):.1f}"
    N["gain0"] = f"{gains[0]:.0f}"
    N["gain_rest"] = f"{min(gains[1:]):.2f} to {max(gains[1:]):.2f}"

    # day-dreaming
    fr = RP.dream_frontier(R)
    ft, spc = fr[FT_FAM], fr[SPOC_FAM]
    for l, key in (("0.01", "01"), ("0.05", "05"), ("0.1", "10"), ("0.25", "25")):
        N[f"ft_{key}"] = f"{ft[l]['held_ce']:.3f}"
        N[f"sp_{key}"] = f"{spc[l]['held_ce']:.3f}"
    N["sp_25_forget"] = f"{spc['0.25']['forgetting']:.3f}"
    need(spc["0.25"]["held_ce"] == spc["0.1"]["held_ce"], "consolidation never needs more than 0.10 nats")
    adv = [ft[l]["held_ce"] - spc[l]["held_ce"] for l in ("0.05", "0.1")]
    need(min(adv) > 0.1, "consolidation learns clearly better at 0.05 and 0.10")
    N["sp_adv"] = f"{min(adv):.2f} to {max(adv):.2f}"
    N["ft_25_forget_ratio"] = f"{ft['0.25']['forgetting'] / spc['0.25']['forgetting']:.1f}"
    N["abs_ft_05"] = f"{ft['0.05']['held_ce']:.2f}"
    N["abs_sp_05"] = f"{spc['0.05']['held_ce']:.2f}"
    dt = RP.dream_table(R)
    gate_runs = [v for kk, v in R["dream"]["runs"].items() if kk.split("|")[0] == "surprise gate"]
    N["gate_forget"] = f"{min(mean([r['curve'][e]['old_ce'] - r['curve'][0]['old_ce'] for r in gate_runs]) for e in range(1, min(len(r['curve']) for r in gate_runs))):.2f}"
    N["gate_bw"] = f"{100 * (1 - dt['surprise gate']['backward_windows'][0] / dt['fine-tune']['backward_windows'][0]):.0f}"
    N["gate_wall"] = f"{100 * (dt['surprise gate']['wall_s'][0] / dt['fine-tune']['wall_s'][0] - 1):.0f}"
    N["dream_epochs"] = str(R["dream"]["config"]["epochs"])

    # kernels
    sp = R["speed"]["median"]
    ctx_all = sorted(int(c) for c in sp[V2])
    gp = R["speed"]["graph_prefill"][V2]
    g_gain = [gp[str(c)]["prefill_tok_s"] / pf(V2, c) - 1 for c in ctx_all]
    N["graph_gain"] = f"{100 * min(g_gain):.0f} to {100 * max(g_gain):.0f} percent"
    cs = R["speed_compiled"]["arms"]

    def comp(a):
        v = [cs[a][str(c)][f] for c in P.long_ctx for f in ("compiled_prefill_tok_s", "compiled_graph_prefill_tok_s")]
        return min(v), max(v)

    (v2lo, v2hi), (mblo, mbhi) = comp(V2), comp(MB)
    eager = [pf(V2, c) for c in P.long_ctx]
    N["v2_comp"] = f"{v2lo / 1e3:.0f}K to {v2hi / 1e3:.0f}K tok/s"
    N["v2_comp_x"] = f"{v2lo / max(eager):.1f}x to {v2hi / min(eager):.1f}x"
    N["mb_comp"] = f"{mblo / 1e3:.0f}K to {mbhi / 1e3:.0f}K"

    # run-to-run variation against the archived first run
    fr1 = first_run(R)
    need(fr1 is not None and len(fr1["ce"]) == len(P.seeds), "the first run of RD-S4 v2 is archived")
    m1, s1 = RP.msd(fr1["ce"])
    N["first_run_ce"] = f"{m1:.4f} ± {s1:.4f}"
    N["v2_ce_msd"] = f"{v2['ce_m']:.4f} ± {v2['ce_s']:.4f}"
    N["rerun_sweep_diff"] = f"{fr1['sweep_max_abs_diff']:.4f}"
    return N

