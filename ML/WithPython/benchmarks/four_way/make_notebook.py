"""Build and execute RD-S4_FourWay_Benchmark.ipynb from the results of run.py.

The notebook only reads results/*.json (training and measurement live in run.py, which is
resumable), so executing it takes seconds and its outputs are exactly what was measured.
"""
import os
import sys

import nbformat
from nbclient import NotebookClient

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "RD-S4_FourWay_Benchmark.ipynb"))
sys.path.insert(0, HERE)
import report as RP  # noqa: E402
from verdict import render  # noqa: E402

# every number in the written conclusions is computed from results/, and every claim checked (verdict.py)
_T = render(RP.load_extra(RP.load_all()))
SUMMARY, VERDICT, V2_INTRO, SPOC_TEXT = (_T[k] for k in ("SUMMARY", "VERDICT", "V2_INTRO", "SPOC_TEXT"))

md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
TAG = "`[T | S4 | Mamba | RD-S4 | v2]`"

cells = [
    md("""<div align="center">

# Transformer vs S4 vs Mamba vs RD-S4 (v1 and v2)
### Four architectures and two RD-S4 generations, 1.7 M parameters, equal training FLOPs, one RTX 5050

</div>

""" + SUMMARY),
    md("""## 1. The question, and the bar it has to clear

> *If RD-S4 maintains comparable or better perplexity and materially lower memory and latency at 32K to 128K
> context, then the research starts becoming genuinely compelling rather than merely an interesting SSM variant.*

That sentence is the acceptance test. Every number below is measured on the same laptop RTX 5050 (8 GB), with the
GPU otherwise idle, by one harness that treats every arm identically. Nothing is reported from a single seed.

""" + V2_INTRO + """

## 2. Protocol

| | |
|---|---|
| **Data** | TinyStories, character level, one shared 75-symbol vocabulary. 80 M training characters; a 1 M-character *probe* split carved from training data (used only by RD-S4's in-network evolution); a 2 M-character *selection* split (learning-rate choice only); a disjoint *test* split from the official validation file (all reported numbers). |
| **Size** | Every arm matched to RD-S4's 1,721,760 parameters within 1 percent (RD-S4 v2: 1,719,980 trained, of which 1,710,536 are used at inference). |
| **Compute** | Equal **training FLOPs** for every arm: 4.34e14, set by 34 M tokens (about 20 per parameter) for the Transformer. Dense contractions are counted at the dispatcher, forward and backward, complex matmuls weighted 4x; attention, FFT convolutions and scans are added analytically (x3 for training). RD-S4's evolution forward passes are charged to its budget. Arms that are cheaper per token therefore see more tokens. |
| **Optimisation** | Shared AdamW recipe (betas 0.9/0.95, weight decay 0.05 on matrices only, clip 1.0, 4 percent warm-up, cosine to 10 percent), batch 32 x 512 characters, fp32 weights with TF32 matmuls. S4 keeps its published rule (A and dt at min(lr, 1e-3), no decay). RD-S4 keeps its own optimiser, full objective (CE + JEPA + VICReg + PTV drafts + router balance), EMA teacher, and evolution. |
| **Fairness** | A learning-rate sweep for **every** arm (1.5e-3, 3e-3, 6e-3, extended if the optimum sits on an edge), selected on the selection split, then 3 seeds at the selected rate. Final weights for everyone: no checkpoint picking. RD-S4 v2's design was fixed by pilots on the selection split at 40 percent of the budget, before any of its test-split numbers existed. |
| **Arms** | **Transformer**: pre-norm GPT, RoPE, d=192, 4 layers, 6 heads. **S4**: S4D-Lin with ZOH, 64 complex modes per channel, GLU, d=192, 4 layers. **Mamba**: Mamba-1, d=188, 7 layers, expand 2, d_state 16, reference initialisation. **RD-S4**: the notebook's `RDS4LM`, loaded from the notebook source and not modified. **RD-S4 v2**: the revised architecture (resonant predictive-coding memory, 6 layers, d=188); its source is proprietary and not part of this notebook. |
| **Kernels** | The Transformer uses PyTorch's flash attention for prefill and a bandwidth-bound matmul decode (measured 11x faster at 128K than the fused kernel, so the baseline gets its best case). Mamba's official CUDA kernels cannot be built here (nvcc 12.4 has no sm_120 target), so its selective scan runs in a fused Triton kernel written for this benchmark and verified against a float64 reference (relative error about 1e-7 on outputs, states and all six gradients). S4 and RD-S4 share the notebook's exact chunked long-context routine. RD-S4 v2 runs in plain PyTorch operations with no custom kernel (its training step is fused by `torch.compile`, which changes wall-clock only; its FLOPs are counted on the eager graph). Every arm uses the same fused RMSNorm kernel. |
| **Long context** | Trained at 512 characters, evaluated at 8K, 32K and 128K: 16x to 256x beyond the training length, for every arm, with full context and with a 512-character window on the same characters. |
"""),
    code("""import sys, os, json, math
sys.path.insert(0, os.path.join(os.getcwd(), "benchmarks", "four_way"))
import matplotlib
%matplotlib inline
import report as RP
R = RP.load_extra(RP.load_all())
plan = R["plan"]
print(f"device      : {plan['gpu']['gpu']}")
print(f"RD-S4 source: {plan['rds4_provenance']['notebook']}  sha256 {plan['rds4_provenance']['sha256'][:16]}...")
pv2 = plan.get('rds4_v2_provenance', {})
if pv2:
    print(f"RD-S4 v2    : {pv2['notebook']}  code sha256 {pv2['code_sha256'][:16]}... (source not included here)")
print(f"budget      : {plan['budget_flops']:.3e} training FLOPs per arm\\n")
print(f"{'arm':<12}{'params':>11}{'FLOPs/token':>14}{'steps':>8}{'tokens':>10}{'evolution share':>17}")
for a, r in plan["arms"].items():
    print(f"{a:<12}{r['params']:>11,}{r['per_step']/16384/1e6:>12.2f} M{r['steps']:>8,}{r['tokens']/1e6:>9.1f}M"
          f"{100*r['evolution_flops_total']/plan['budget_flops']:>16.1f}%")
print("\\nparity of every fast path against the parallel forward (random weights):")
for a, r in R["check"]["random_init"].items():
    print(f"  {a:<12} streamed NLL max |diff| {r['stream_vs_parallel_max_abs_nll']:.1e}   decode max rel {r['decode_vs_parallel_max_rel_logit']:.1e}")"""),
    md(f"### 3. 🧪 {TAG} Results ①: training at equal FLOPs\n\nLeft: held-out CE against compute "
       "for each arm at its selected learning rate (line = mean, band = min to max over 3 seeds). Right: the sweep "
       "that chose it. A head-to-head won by giving another architecture a bad learning rate is not a result."),
    code("RP.fig_training(R);\nprint(json.dumps({a: R['sweep'][a]['select_ce'] for a in RP.C.ARMS}, indent=1))"),
    md(f"### 4. 🧪 {TAG} Results ②: quality (cross-entropy, perplexity, accuracy)\n\nTest split, 4,096 windows "
       "of 512 characters (2.1 M characters). Perplexity is per character. p-values are exact permutation tests "
       "over all relabellings of the per-seed values; with 3 seeds a side the smallest attainable value is 0.05 "
       "one-sided (0.10 two-sided), which therefore means complete separation."),
    code("""RP.fig_quality(R)
sig = RP.significance(R)
print(f"{'model':<10}{'vs':<13}{'metric':<20}{'model':>9}{'other':>9}{'diff':>9}{'p(1-sided)':>12}{'p(2-sided)':>12}")
for s in sig:
    if s["metric"] in ("test CE", "CE@8K full", "CE@32K full", "CE@128K full", "retrieval@32", "retrieval@192"):
        print(f"{s['model']:<10}{s['baseline']:<13}{s['metric']:<20}{s['rd_s4']:>9.4f}{s['baseline_mean']:>9.4f}"
              f"{s['diff']:>+9.4f}{s['p_one_sided']:>12.3f}{s['p_two_sided']:>12.3f}")
print("(every metric, including retrieval at every gap, is in results/significance.json)")"""),
    md(f"### 5. 🧪 {TAG} Results ③: does quality survive 8K, 32K and 128K of context?\n\nFour 131,072-character "
       "test streams, scored at every position. **Full context**: the Transformer attends over everything before; "
       "the recurrent arms carry their state across 2,048-character chunks (verified exact). **512 window**: the "
       "same characters re-scored when every prediction may use at most the 512 characters a model was trained on. "
       "Panel (b) shows each arm in the configuration that can actually be deployed at that length (a Transformer "
       "trained at 512 would be served with a window). Panel (c) is the cleanest long-context number in this "
       "notebook: on identical characters, how much better (or worse) the model does when it also has everything "
       "beyond the last 512 characters."),
    code("""RP.fig_long(R)
print(f"{'arm':<12}{'':>4}" + "".join(f"{f'@{c//1024}K full':>13}{'window':>9}{'gain':>9}" for c in RP.P.long_ctx))
for a in RP.C.ARMS:
    es = RP.evals2(R, a)
    row = ""
    for c in RP.P.long_ctx:
        k = str(c)
        f = sum(e['context'][k]['ce_full'] for e in es) / len(es)
        w = sum(e['context'][k]['ce_window'] for e in es) / len(es)
        row += f"{f:>13.4f}{w:>9.4f}{w - f:>+9.4f}"
    print(f"{a:<12}{'':>4}" + row)"""),
    md(f"### 6. 🧪 {TAG} Results ④: long-range retrieval, as a controlled experiment\n\nTwo sequences are built "
       "for every trial and differ in exactly one 128-character slot near the start. In the *treated* sequence the "
       "slot holds a test passage; in the *control* it holds a different passage. Both continue with the same gap "
       "of unrelated text and then the same passage. The score is CE(control) minus CE(treated) on characters 17 "
       "to 128 of that final passage, so everything except the earlier copy is held fixed. 8 passages per gap, 3 "
       "seeds. Gaps of 32 and 192 fit inside the 512-character training window for every arm; the rest are 4x to "
       "256x beyond it. No arm was trained on this task.\n\n*Design note:* an earlier version of this test "
       "compared a passage's first appearance with its repeat. That confounds retrieval with position (the two "
       "copies sit at different depths with different text before them), and for the Transformer it mostly measured "
       "positions beyond 512. It was replaced by this controlled version before any conclusion was drawn; its raw "
       "output remains in `results/eval/` for transparency."),
    code("""RP.fig_retrieval(R)
print(f"{'arm':<12}" + "".join(f"{f'gap {D:,}':>13}" for D in RP.P.retrieval_gaps))
for a in RP.C.ARMS:
    es = RP.evals2(R, a)
    print(f"{a:<12}" + "".join(f"{sum(e['retrieval'][str(D)]['gain'] for e in es)/len(es):>+13.4f}" for D in RP.P.retrieval_gaps))
print("(Transformer values beyond gap 192 use positions it was never trained on; with a 512 window its gain there is 0 by construction.)")"""),
    md(f"### 7. 🧪 {TAG} Results ⑤: prefill, decode and memory at 2K to 128K\n\nBatch 1, seed-0 weights, real "
       "test text, median of 3 interleaved rounds after a warm-up. Prefill produces the decode-ready state (the "
       "Transformer writes its bf16 KV cache in one flash-attention pass; the recurrent arms process 2,048-character "
       "chunks, the setting the chunk sweep below shows to be fastest or within 3 percent of fastest for each of them, "
       "at a quarter of the memory of 8,192). Decode generates 128 tokens greedily, eagerly and with CUDA graphs (32 "
       "steps per graph, one RD-S4 routing window), which removes Python launch overhead equally for every arm. Peak "
       "memory is the working set above the weights."),
    code("""RP.fig_efficiency(R)
sp = R["speed"]
print("precision:", json.dumps(sp["precision"], indent=1))
print("\\nprefill chunk trade-off at 128K (recurrent arms):")
for a, d in sp["chunk_sweep_128k"].items():
    print(f"  {a:<8}" + "  ".join(f"chunk {k:>6}: {v['prefill_tok_s']:>9,.0f} tok/s {v['peak_mb']:>7.1f} MB" for k, v in d.items()))
print("\\nprefill replayed from one CUDA graph per 2,048-character chunk (same kernels, no launch overhead):")
for a, d in sp.get("graph_prefill", {}).items():
    if "error" in d:
        print(f"  {a:<9} not capturable: {d['error']}"); continue
    print(f"  {a:<9}" + "  ".join(f"{int(c)//1024:>3}K {v['prefill_tok_s']:>9,.0f} tok/s" for c, v in d.items() if c.isdigit())
          + f"   (|logit diff| vs eager {d['max_abs_logit_diff_vs_eager']:.1e})")
spc = R.get("speed_compiled")
if spc:
    print("\\nsupplementary: every chunked recurrent arm compiled by TorchInductor (fixed shapes), same weights:")
    for a, d in spc["arms"].items():
        if "error" in d:
            print(f"  {a:<9} failed: {d['error']}"); continue
        print(f"  {a:<9} prefill " + "  ".join(f"{int(c)//1024:>3}K {v['compiled_prefill_tok_s']:>9,.0f} (+graph {v['compiled_graph_prefill_tok_s']:>9,.0f}) tok/s"
              for c, v in d.items() if c.isdigit()) + f"   decode @32K {d['decode_compiled_graph_tok_s_32k']:,.0f} tok/s"
              + f"   |logit diff| {d['max_abs_logit_diff_vs_eager']:.1e}")
print("\\nGPU before:", sp["gpu_before"]["gpu"]); print("GPU after :", sp["gpu_after"]["gpu"])"""),
    md(f"### 8. 🧪 {TAG} Results ⑥: training time to a given quality\n\nThe same training runs as section 3, "
       "plotted against wall-clock on this GPU instead of FLOPs (one-off compilation excluded and reported "
       "separately). The marker on each curve is where that arm first reaches the final quality of RD-S4 v1."),
    code("""fig, ttq = RP.fig_time_to_quality(R)
print(f"target: final held-out curve CE of RD-S4 v1 = {ttq['target_curve_ce']:.4f}")
print(f"{'arm':<12}{'ms/step':>9}{'full run':>11}{'reaches it at step':>20}{'budget':>9}{'minutes':>9}")
for a, r in ttq["arms"].items():
    hit = f"{r['step']:>20,}{100*r['budget_fraction']:>8.0f}%{r['minutes']:>9.1f}" if "step" in r else f"{'never':>20}"
    print(f"{a:<12}{1e3*r['sec_per_step']:>9.0f}{r['full_run_minutes']:>9.1f} m{hit}")
v2 = [R["runs"][k] for k in R["runs"] if k[0] == "RD-S4 v2" and "first_step_s" in R["runs"][k]]
if v2:
    print(f"RD-S4 v2 one-off compilation per run: {min(r['first_step_s'] for r in v2):.0f} to {max(r['first_step_s'] for r in v2):.0f} s")"""),
    md("### 9. 🧪 SPOC on RD-S4 v2: what the brain-inspired learning rules do on a GPU\n\n" + SPOC_TEXT),
    code("""RP.fig_spoc(R)
ab = R.get("ablate") or {}
if ab.get("gate"):
    g = ab["gate"]; b = R["runs"][("RD-S4 v2", g["lr"], g["seed"])]
    print(f"(a) pre-training, seed 0, equal FLOPs: plain {b['select_ce']:.4f} ({b['tokens']/1e6:.1f} M chars learned)  "
          f"vs gated {g['select_ce']:.4f} ({g['tokens_trained']/1e6:.1f} M learned, {g['tokens_screened']/1e6:.1f} M screened)")
pc = R.get("pc")
if pc:
    print(f"(b) backprop: {1e3*pc['backprop']['seconds']:.0f} ms per update")
    for key in ("pc", "pc_small", "pc_fpa"):
        for T, r in pc.get(key, {}).items():
            print(f"    {key:7s} T={T:>2}: {r['time_ratio']:4.1f}x the time, {r['flop_ratio']:4.1f}x the FLOPs, "
                  f"cos to exact gradient {r['cosine_to_backprop']:+.3f}")
    for n, r in pc["race_equal_wallclock"].items():
        print(f"    equal wall-clock race, {n:<16}: {r['updates']:>4} updates -> selection CE {r['select_ce']:.4f}")
ps_ = R.get("pc_steps")
if ps_:
    print("(b') plain PC with smaller relaxation steps (stability), cosine to the exact gradient:")
    for k, r in ps_["grid"].items():
        print(f"    output-error scale {r['beta_out']:<5g} gamma {r['gamma']:<5g} T={r['T']:>2}: {r['time_ratio']:5.1f}x backprop  cos {r['cosine_to_backprop']:+.3f}")
    for n, r in ps_["race_equal_wallclock"].items():
        print(f"    equal wall-clock race, {n}: {r['updates']} updates -> selection CE {r['select_ce']:.4f}")
pp_ = R.get("pc_precision")
if pp_:
    print("(b'') plain PC on 8 windows, gamma 0.1: TF32 vs full fp32 arithmetic, and a separate stable step for x_0:")
    for k, c in pp_["cosine_to_backprop"].items():
        print(f"    {k:<28} cos {c:+.3f}")
    for k, c in pp_.get("per_layer_step", {}).items():
        print(f"    {k:<36} cos {c:+.3f}")
jt = RP.jepa_ablation(R)
if jt:
    print(f"JEPA ablation (3 seeds each, test CE): with {jt['with_jepa'][0]:.4f} ± {jt['with_jepa'][1]:.4f}, "
          f"without {jt['without_jepa'][0]:.4f} ± {jt['without_jepa'][1]:.4f}, diff {jt['diff']:+.4f}, "
          f"p two-sided {jt['p_two_sided']:.2f} (one-sided, JEPA better: {jt['p_one_sided']:.2f})")"""),
    code("""RP.fig_dream(R)
dt = RP.dream_table(R)
print(f"{'method':<30}{'held-out CE':>14}{'learned':>10}{'forgetting':>12}{'backward':>10}{'screened':>10}{'seconds':>9}")
for m, r in dt.items():
    print(f"{m:<30}{r['held_ce'][0]:>8.3f}±{r['held_ce'][1]:.3f}{r['learned'][0]:>+10.3f}{r['forgetting'][0]:>+12.4f}"
          f"{r['backward_windows'][0]:>10.0f}{r['screen_windows'][0]:>10.0f}{r['wall_s'][0]:>9.1f}")
fr = RP.dream_frontier(R)
print("\\nbest held-out Shakespeare CE reachable without forgetting more than a given amount of TinyStories "
      "(any setting, any pass; mean of 3 models):")
lims = sorted({float(k) for v in fr.values() for k in v})
print(f"{'family':<44}" + "".join(f"{f'forget <= {l:g}':>18}" for l in lims))
for f, v in fr.items():
    print(f"{f:<44}" + "".join(f"{(format(v[str(l)]['held_ce'], '.3f') if str(l) in v else 'n/a'):>18}" for l in lims))"""),
    md(f"### 10. 🧪 {TAG} Scorecard\n\nMean ± sample standard deviation over 3 seeds for quality; medians for "
       "speed. An asterisk marks the best value on each row."),
    code("print(RP.scorecard_text(R))"),
    md("## 11. Verdict\n\n" + VERDICT),
    md("""## 12. Reproduce

```bash
cd ML/WithPython/benchmarks/four_way
python run.py check     # parity of every fast path (random weights)
python run.py plan      # FLOPs per step -> equal-budget step counts
python run.py sweep     # learning-rate sweep, seed 0, all arms
python run.py seeds     # seeds 0-2 at each arm's selected rate
python run.py eval      # test CE/PPL (all seeds)
python run.py eval2     # full-context vs 512-window CE at 8K/32K/128K; controlled retrieval
python run.py speed     # prefill / decode / memory, 2K-128K (eager and CUDA-graph prefill)
python ablate_v2.py     # RD-S4 v2 without JEPA (3 seeds); RD-S4 v2 with the SPOC surprise gate
python dream_v2.py      # day-dreaming: teach Shakespeare, measure forgetting
python pc_cost.py       # predictive-coding relaxation vs backprop on RD-S4 v2
python pc_steps.py      # plain PC: relaxation step sizes, output-error scale, equal wall-clock race
python pc_checks.py     # PC: value-node scales, TF32 vs fp32, per-layer step, classic-MLP control
python speed_compiled.py  # supplementary: every chunked recurrent arm compiled by TorchInductor
python make_notebook.py # rebuild and execute this notebook from results/
```
Every stage is resumable; finished runs are skipped. Raw per-run histories, per-seed evaluations and every speed
repetition are in `benchmarks/four_way/results/`.
"""),
]

nb = nbformat.v4.new_notebook(cells=cells, metadata={
    "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
    "language_info": {"name": "python"}})
NotebookClient(nb, timeout=600, kernel_name="python3",
               resources={"metadata": {"path": os.path.dirname(OUT)}}).execute()
nbformat.write(nb, OUT)
print("wrote", OUT)
