"""Does predictive-coding learning speed up RD-S4 v2 on a GPU?  (measured, not argued)

Block-level predictive coding (Whittington and Bogacz 2017; Millidge, Tschantz, Buckley 2022):
value nodes x_l at every block output, energy

    F = sum_l 1/2 ||x_l - f_l(x_{l-1})||^2 + sum_tokens CE(head(x_L), y)

T relaxation sweeps move every x_l down dF/dx_l (all blocks at once: every block only needs its own
input and the error of the block above, so the sweep is layer-parallel), then each block updates its own
weights from its own error: dtheta_l = J_theta_l^T eps_l (local). Two variants:

    PC      predictions recomputed from the current value nodes every sweep (the digit study's rule)
    PC-FPA  fixed-prediction assumption: predictions and Jacobians frozen at the feed-forward pass;
            with step 1 the errors equal backprop's adjoints after L sweeps (exact)

Measured per weight update, against backprop (one forward + one backward): wall-clock, dense FLOPs,
and the cosine between the PC weight update and the backprop gradient. Then a short race at equal
wall-clock on the real data. Results: results/pc_cost.json.
"""
import time

import torch
import torch.nn.functional as F

import common as C
from run import Ctx, eval_ce, log

P = C.P


# The learning rules are the main notebook's (RD-S4_EFR_TinyStories.ipynb, Sec. 15.5); bind() attaches them.
_NS = {}


def bind(ns2):
    _NS.update(ns2)


def lm_params(model):
    return _NS["lm_params"](model)


def bp_grads(model, x, y):
    return _NS["bp_grads"](model, x, y)


def pc_grads(*args, **kw):
    return _NS["pc_grads"](*args, **kw)


def flat(gs, like):
    return _NS["flat"](gs, like)


def timed(fn, reps=5):
    fn()
    C.sync()
    t0 = time.perf_counter()
    for _ in range(reps):
        out = fn()
    C.sync()
    return out, (time.perf_counter() - t0) / reps


def main():
    cx = Ctx()
    bind(cx.ns2)
    torch.manual_seed(0)
    arm = cx.build("RD-S4 v2")
    smp = C.Sampler(cx.train, seed=0)
    # warm the model a little so gradients are not those of a random network
    opt = arm.make_optimizer(3e-3)
    for _ in range(150):
        x, y = smp()
        loss, _ = arm.train_loss(x, y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
    x, y = smp()
    params = lm_params(arm)
    L = len(arm.blocks)
    with C.MatmulFlops() as f:
        g_bp = bp_grads(arm, x, y)
    bp_flops = f.flops + 3 * arm.mixing_flops(P.batch, P.seq_len, True)
    g_bp, t_bp = timed(lambda: bp_grads(arm, x, y))
    v_bp = flat(g_bp, params)
    res = {"blocks": L, "backprop": {"seconds": t_bp, "flops": bp_flops}, "pc": {}, "pc_small": {}, "pc_fpa": {}}
    log(f"pc_cost: backprop {t_bp*1e3:.0f} ms/update, {bp_flops/1e12:.3f} TFLOP")
    for key, fpa, beta_out in (("pc", False, 1.0), ("pc_small", False, 1e-2), ("pc_fpa", True, 1.0)):
        for T in (1, 2, L, L + 1, 2 * L, 4 * L):
            gamma = 1.0 if fpa else 0.5
            with C.MatmulFlops() as f:
                g = pc_grads(arm, x, y, T, gamma, fpa, beta_out)
            fl = f.flops + arm.mixing_flops(P.batch, P.seq_len, True) * (3 * T + 3 if not fpa else T + 4)
            g, t = timed(lambda: pc_grads(arm, x, y, T, gamma, fpa, beta_out), reps=3)
            v = flat(g, params)
            cos = float(F.cosine_similarity(v, v_bp, dim=0))
            res[key][str(T)] = {"seconds": t, "flops": fl, "cosine_to_backprop": cos,
                                "time_ratio": t / t_bp, "flop_ratio": fl / bp_flops}
            log(f"   {key:6s} T={T:2d}: {t*1e3:6.0f} ms ({t/t_bp:4.1f}x backprop)  {fl/bp_flops:4.1f}x FLOPs  "
                f"cos(update, backprop grad) {cos:+.3f}")
    # equal wall-clock race on real data (eager, identical optimiser and schedule-free LR)
    race = {}
    budget_s = 120.0
    for name, kw in (("backprop", None), ("PC (T=L+1)", dict(T=L + 1, gamma=0.5, fpa=False)),
                     ("PC, small output error (T=L+1)", dict(T=L + 1, gamma=0.5, fpa=False, beta_out=1e-2)),
                     ("PC-FPA (T=L+1)", dict(T=L + 1, gamma=1.0, fpa=True))):
        C.seed_all(0)
        torch.manual_seed(0)
        m = cx.build("RD-S4 v2")
        o = m.make_optimizer(3e-3)
        s = C.Sampler(cx.train, seed=0)
        C.sync()
        t0 = time.perf_counter()
        n = 0
        curve = []
        while time.perf_counter() - t0 < budget_s:
            x, y = s()
            if kw is None:
                gs = bp_grads(m, x, y)
            else:
                gs = pc_grads(m, x, y, **kw)
            ps = lm_params(m)
            for p, g in zip(ps, gs):
                p.grad = None if g is None else g / (P.batch * P.seq_len)
            torch.nn.utils.clip_grad_norm_(ps, P.grad_clip)
            o.step()
            n += 1
            if n % 25 == 0:
                C.sync()
                curve.append((time.perf_counter() - t0, eval_ce(m, *cx.curve)[0]))
        C.sync()
        ce, acc = eval_ce(m, *cx.sel)
        race[name] = {"updates": n, "seconds": time.perf_counter() - t0, "select_ce": ce, "select_acc": acc,
                      "curve": curve}
        log(f"   race {name:14s}: {n:4d} updates in {budget_s:.0f}s -> select CE {ce:.4f}")
        del m, o
        torch.cuda.empty_cache()
    res["race_equal_wallclock"] = race
    res["gpu"] = C.gpu_snapshot()
    C.save_json("pc_cost.json", res)


if __name__ == "__main__":
    main()
