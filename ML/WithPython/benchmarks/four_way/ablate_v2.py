"""Ablations of RD-S4 v2 at the full budget, after the main protocol (run.py) has selected its learning rate.

    no JEPA       the same model trained on next-character CE only (3 seeds, same learning rate and steps);
                  scored on the same test windows, so the JEPA objective's effect is measured, not assumed
    SPOC gate     the same model trained with the surprise gate (seed 0): 2B candidate windows are screened
                  without gradients, B are drawn by surprise and importance-weighted (unbiased); the screening
                  forward passes are charged to the FLOP budget

    python ablate_v2.py
Writes results/ablate_v2.json.
"""
import math
import time

import torch

import common as C
from run import Ctx, ckpt_path, eval_ce, log, train_run

P = C.P
V2 = "RD-S4 v2"
NOJEPA = "RD-S4 v2 (no JEPA)"
OUT = "ablate_v2.json"


def screen_flops(arm, sample, n, T):
    """Forward FLOPs of screening n candidate windows (no gradients), counted like every other forward."""
    x, _ = sample(n)
    arm.eval()
    with C.MatmulFlops() as f, torch.no_grad():
        arm.logits(x)
    arm.train()
    return f.flops + arm.mixing_flops(n, T, False)


def gate_run(cx, lr, seed, budget):
    SurpriseGate = cx.ns2["SurpriseGate"]             # the main notebook's SPOC surprise gate
    torch.manual_seed(0)
    arm = cx.build(V2)
    x, y = C.Sampler(cx.train, seed=12345)()
    with C.MatmulFlops() as fc:
        loss, _ = arm.train_loss(x, y)
        loss.backward()
    per_step = fc.flops + 3.0 * arm.mixing_flops(P.batch, P.seq_len, True)
    gate = SurpriseGate(arm, C.Sampler(cx.train, seed), P.batch, seed=seed)
    screen = screen_flops(arm, gate.sample, gate.N, P.seq_len)
    steps = int(budget // (per_step + screen))
    C.seed_all(seed)
    arm = cx.build(V2)                 # eager: the compiled weighted-loss path stalled on this machine; FLOPs are
    sg = SurpriseGate(arm, C.Sampler(cx.train, seed), P.batch, seed=seed)    # identical, only wall-clock differs
    opt = arm.make_optimizer(lr)
    log(f"gate run: {steps} steps ({per_step/1e12:.4f} + screen {screen/1e12:.4f} TFLOP/step)")
    C.sync()
    t0 = time.perf_counter()
    arm.train()
    for step in range(steps):
        lr_t = C.lr_at(step, steps, lr)
        for g in opt.param_groups:
            g["lr"] = lr_t * g.get("lr_scale", 1.0)
        xb, yb, w = sg()
        loss, _ = arm.train_loss(xb, yb, w)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(arm.parameters(), P.grad_clip)
        opt.step()
    C.sync()
    wall = time.perf_counter() - t0
    sel_ce, sel_acc = eval_ce(arm, *cx.sel)
    tx, ty = (t.long().to(cx.dev) for t in C.windows(cx.cor.test, P.test_windows))
    test_ce, test_acc = eval_ce(arm, tx, ty)
    return {"seed": seed, "lr": lr, "steps": steps, "per_step_flops": per_step, "screen_flops": screen,
            "tokens_trained": steps * P.batch * P.seq_len, "tokens_screened": steps * 2 * P.batch * P.seq_len,
            "select_ce": sel_ce, "select_acc": sel_acc, "test_ce": test_ce, "test_acc": test_acc, "wall_s": wall}


def main():
    cx = Ctx()
    plan, sweep = C.load_json("plan.json"), C.load_json("sweep.json")
    lr, steps = sweep[V2]["best_lr"], plan["arms"][V2]["steps"]
    res = C.load_json(OUT, {"lr": lr, "steps": steps, "no_jepa": {}, "gate": None})
    tx, ty = (t.long().to(cx.dev) for t in C.windows(cx.cor.test, P.test_windows))
    for seed in P.seeds:
        if str(seed) in res["no_jepa"]:
            continue
        rec = train_run(cx, NOJEPA, lr, seed, steps)
        arm = cx.build(NOJEPA)
        arm.load_state_dict(torch.load(ckpt_path(NOJEPA, lr, seed), map_location=cx.dev))
        ce, acc = eval_ce(arm, tx, ty)
        res["no_jepa"][str(seed)] = {"select_ce": rec["select_ce"], "test_ce": ce, "test_acc": acc,
                                     "wall_s": rec["wall_s"]}
        log(f"ablation no JEPA s{seed}: test CE {ce:.4f} (ppl {math.exp(ce):.3f})")
        C.save_json(OUT, res)
        del arm
        torch.cuda.empty_cache()
    if res["gate"] is None:
        res["gate"] = gate_run(cx, lr, 0, plan["budget_flops"])
        g = res["gate"]
        log(f"gate run s0: select CE {g['select_ce']:.4f}  test CE {g['test_ce']:.4f}  ({g['wall_s']/60:.1f} min)")
        C.save_json(OUT, res)


if __name__ == "__main__":
    main()
