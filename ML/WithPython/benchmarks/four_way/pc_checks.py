"""Checks behind the predictive-coding conclusions (Sec. 9.4 of the main notebook), on RD-S4 v2 after the same
warm start as pc_cost.py (150 steps), 8 windows:

    scales        RMS of every value node and the gain |J v| / |v| of every block on random directions
    precision     plain PC with TF32 matmuls versus full fp32
    per-layer     plain PC with a separate, smaller relaxation step for the embedding's value node x_0
    control       the same PC code on a classic tanh MLP network (embedding, 6 blocks, read-out), fp32

    python pc_checks.py
Writes results/pc_precision.json.
"""
import torch
import torch.nn.functional as F
from torch.func import jvp

import common as C
from pc_cost import bind, bp_grads, flat, lm_params, pc_grads
from run import Ctx, log


def set_precision(prec):
    torch.backends.cuda.matmul.allow_tf32 = prec == "tf32"
    torch.backends.cudnn.allow_tf32 = prec == "tf32"
    torch.set_float32_matmul_precision("high" if prec == "tf32" else "highest")


def main():
    cx = Ctx()
    bind(cx.ns2)
    torch.manual_seed(0)
    arm = cx.build("RD-S4 v2")
    smp = C.Sampler(cx.train, seed=0)
    opt = arm.make_optimizer(3e-3)
    for _ in range(150):
        x, y = smp()
        loss, _ = arm.train_loss(x, y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
    x, y = smp()
    x, y = x[:8], y[:8]
    ps = lm_params(arm)
    out = {"batch": 8, "gamma": 0.1, "warm_steps": 150, "scales": {}, "cosine_to_backprop": {}, "per_layer_step": {}}

    with torch.no_grad():
        h = arm.emb(x)
        xs = [h]
        for b in arm.blocks:
            h = b(h)
            xs.append(h)
    out["scales"]["value_node_rms"] = [t.pow(2).mean().sqrt().item() for t in xs]
    gains = []
    for l, b in enumerate(arm.blocks):
        g = []
        for _ in range(4):
            v = torch.randn_like(xs[l])
            v = v / v.norm()
            g.append(jvp(lambda z: b(z), (xs[l],), (v,))[1].norm().item())
        gains.append(sum(g) / len(g))
    out["scales"]["block_gain_random_directions"] = gains
    log("pc_checks value-node RMS " + " ".join(f"{r:.3f}" for r in out["scales"]["value_node_rms"])
        + " | block gains " + " ".join(f"{g_:.2f}" for g_ in gains))

    for prec in ("tf32", "fp32"):
        set_precision(prec)
        vb = flat(bp_grads(arm, x, y), ps)
        for beta in (1.0, 1e-2):
            for T in (7, 48, 200):
                c = F.cosine_similarity(flat(pc_grads(arm, x, y, T, 0.1, False, beta), ps), vb, dim=0).item()
                out["cosine_to_backprop"][f"{prec}_beta{beta:g}_T{T}"] = c
                log(f"pc_checks {prec} beta {beta:g} T={T}: cos {c:+.3f}")
                torch.cuda.empty_cache()
    set_precision("tf32")
    vb = flat(bp_grads(arm, x, y), ps)
    for beta in (1.0, 1e-2):
        for g0 in (1e-3, 1e-4):
            for T in (7, 48, 200):
                c = F.cosine_similarity(flat(pc_grads(arm, x, y, T, 0.1, False, beta, gamma0=g0), ps), vb,
                                        dim=0).item()
                out["per_layer_step"][f"beta{beta:g}_gamma0.1_gamma0{g0:g}_T{T}"] = c
                log(f"pc_checks x_0 step {g0:g} beta {beta:g} T={T}: cos {c:+.3f}")
                torch.cuda.empty_cache()

    # Control: the same pc_grads on a classic PC network (embedding, 6 tanh MLP blocks without normalisation or
    # residuals, linear read-out), same windows, full fp32. If PC converges to backprop here, the misalignment
    # on RD-S4 v2 is a property of that network, not of the PC code.
    set_precision("fp32")
    torch.manual_seed(0)
    toy = ToyLM(arm.vocab).to(x.device)
    pt = lm_params(toy)
    vb = flat(bp_grads(toy, x, y), pt)
    out["mlp_control"] = {"model": "embedding + 6 x (Linear 64x64, tanh) + linear read-out", "precision": "fp32",
                          "gamma": 0.1, "cosine_to_backprop": {}}
    for beta in (1.0, 1e-2):
        for T in (7, 48, 200):
            c = F.cosine_similarity(flat(pc_grads(toy, x, y, T, 0.1, False, beta), pt), vb, dim=0).item()
            out["mlp_control"]["cosine_to_backprop"][f"beta{beta:g}_T{T}"] = c
            log(f"pc_checks MLP control beta {beta:g} T={T}: cos {c:+.4f}")
    c = F.cosine_similarity(flat(pc_grads(toy, x, y, len(toy.blocks) + 1, 1.0, True), pt), vb, dim=0).item()
    out["mlp_control"]["cosine_to_backprop"]["fpa_T7"] = c
    log(f"pc_checks MLP control PC-FPA T=7: cos {c:+.4f}")
    set_precision("tf32")
    C.save_json("pc_precision.json", out)


class ToyLM(torch.nn.Module):
    """The classic predictive-coding test network, with the interface pc_grads expects."""

    def __init__(self, vocab, d=64, n_blocks=6):
        super().__init__()
        self.vocab = vocab
        self.emb = torch.nn.Embedding(vocab, d)
        self.blocks = torch.nn.ModuleList([torch.nn.Sequential(torch.nn.Linear(d, d), torch.nn.Tanh())
                                           for _ in range(n_blocks)])
        self.norm_f = torch.nn.Identity()
        self.head = torch.nn.Linear(d, vocab, bias=False)

    def logits(self, x):
        h = self.emb(x)
        for b in self.blocks:
            h = b(h)
        return self.head(h)


if __name__ == "__main__":
    main()
