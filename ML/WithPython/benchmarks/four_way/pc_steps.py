"""Follow-up to pc_cost.py: plain predictive coding with stable relaxation step sizes.

pc_cost.py used one step size (gamma = 0.5) for every value node. Gradient descent on the PC energy is stable only
for gamma below about 2 / lambda_max of its Hessian, which for residual blocks with Jacobian norm 2-3 is about
0.1-0.2, so plain PC there may not have converged. Here gamma is swept, with up to 48 sweeps and both output-error
scales, and the best stable setting races backprop at equal wall-clock. Writes results/pc_steps.json.

    python pc_steps.py
"""
import time

import torch
import torch.nn.functional as F

import common as C
from pc_cost import bind, bp_grads, flat, lm_params, pc_grads, timed
from run import Ctx, eval_ce, log

P = C.P


def main():
    cx = Ctx()
    bind(cx.ns2)
    torch.manual_seed(0)
    arm = cx.build("RD-S4 v2")
    smp = C.Sampler(cx.train, seed=0)
    opt = arm.make_optimizer(3e-3)
    for _ in range(150):                                 # the same warm start as pc_cost.py
        x, y = smp()
        loss, _ = arm.train_loss(x, y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
    x, y = smp()
    params = lm_params(arm)
    g_bp, t_bp = timed(lambda: bp_grads(arm, x, y))
    v_bp = flat(g_bp, params)
    res = {"backprop_seconds": t_bp, "grid": {}}
    best = None
    for beta_out in (1.0, 1e-2):
        for gamma in (0.05, 0.1, 0.2):
            for T in (7, 24, 48):
                g, t = timed(lambda: pc_grads(arm, x, y, T, gamma, False, beta_out), reps=1)
                cos = float(F.cosine_similarity(flat(g, params), v_bp, dim=0))
                key = f"beta{beta_out:g}_gamma{gamma:g}_T{T}"
                res["grid"][key] = {"beta_out": beta_out, "gamma": gamma, "T": T, "seconds": t,
                                    "time_ratio": t / t_bp, "cosine_to_backprop": cos}
                log(f"pc_steps {key:24s}: {t / t_bp:5.1f}x backprop  cos {cos:+.3f}")
                if best is None or cos > best[0]:
                    best = (cos, dict(T=T, gamma=gamma, fpa=False, beta_out=beta_out), key)
    res["best"] = best[2]
    race = {}
    for name, kw in (("backprop", None), (f"PC best ({best[2]})", best[1])):
        C.seed_all(0)
        torch.manual_seed(0)
        m = cx.build("RD-S4 v2")
        o = m.make_optimizer(3e-3)
        s = C.Sampler(cx.train, seed=0)
        C.sync()
        t0 = time.perf_counter()
        n = 0
        while time.perf_counter() - t0 < 120.0:
            xb, yb = s()
            gs = bp_grads(m, xb, yb) if kw is None else pc_grads(m, xb, yb, **kw)
            ps = lm_params(m)
            for p, gr in zip(ps, gs):
                p.grad = None if gr is None else gr / (P.batch * P.seq_len)
            torch.nn.utils.clip_grad_norm_(ps, P.grad_clip)
            o.step()
            n += 1
        C.sync()
        ce, acc = eval_ce(m, *cx.sel)
        race[name] = {"updates": n, "seconds": time.perf_counter() - t0, "select_ce": ce, "select_acc": acc}
        log(f"pc_steps race {name}: {n} updates in 120s -> select CE {ce:.4f}")
        del m, o
        torch.cuda.empty_cache()
    res["race_equal_wallclock"] = race
    C.save_json("pc_steps.json", res)


if __name__ == "__main__":
    main()
