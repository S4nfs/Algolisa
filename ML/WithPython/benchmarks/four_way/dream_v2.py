"""Day-dreaming test: teach a trained model new text without forgetting what it knew.

The model learned TinyStories in the four-way benchmark. It is now taught Shakespeare (As You Like It, the
book the project started from): the first 85 % of the play is taught for several passes, the next 5 % only
calibrates the surprise gate, and the last 10 % is held out (does it learn the new style, not only the taught
lines?). TinyStories windows measure forgetting.

Methods, all from the same trained checkpoint, same passes, same AdamW step size:
    fine-tune                     the standard way: every weight, plain gradient steps
    fine-tune, linear layers      the same, restricted to the layers consolidation can protect
    surprise gate                 SPOC's gate: window i is learned with probability p_i = clip(s_i / tau, p_min, 1)
                                  and weight 1 / p_i (unbiased), s_i its mean token error and tau the error on
                                  calibration text of the same play that is never taught. A window the model already
                                  predicts better than unseen text (it is being memorised) stops costing backward
                                  passes. Screening and calibration forwards are counted.
    orthogonal consolidation      SPOC's protection: every update of a linear layer is projected away from the
                                  inputs that layer sees on TinyStories, P = alpha (R + alpha I)^-1 (OWM)
    SPOC                          gate + consolidation

    python dream_v2.py [--arm "RD-S4 v2"]
"""
import argparse
import math
import os
import time

import torch

import common as C
from run import Ctx, ckpt_path, eval_ce, log

P = C.P
BOOK = os.path.normpath(os.path.join(C.HERE, "..", "..", "..", "WithJavascript", "Building-GPT2",
                                     "As-You-Like-It.txt"))
W, BATCH, EPOCHS, LR = 512, 8, 8, 1e-3
P_MIN = 0.05
OLD_WINDOWS, PROTECT_WINDOWS = 256, 64

METHODS = {
    # name: (trainable, gate, consolidation alpha or None, lr)
    "fine-tune":                   ("all", False, None, LR),
    "fine-tune, lr/3":             ("all", False, None, LR / 3),
    "fine-tune, linear layers":    ("linear", False, None, LR),
    "surprise gate":               ("all", True, None, LR),
    "orthogonal consolidation":    ("linear", False, 1e-2, LR),
    "SPOC (gate + consolidation)": ("linear", True, 1e-2, LR),
    "SPOC, alpha 0.1":             ("linear", True, 1e-1, LR),
    # added after the first seed, to trace both stability-plasticity curves (not to pick a winner)
    "fine-tune, lr/10":            ("all", False, None, LR / 10),
    "SPOC, alpha 0.03":            ("linear", True, 3e-2, LR),
    "SPOC, alpha 0.3":             ("linear", True, 3e-1, LR),
}


def encode(cor, text):
    unk = cor.stoi[C.UNK]
    return torch.tensor([cor.stoi.get(ch, unk) for ch in text], dtype=torch.long), unk


def windows_of(ids, dev):
    n = (len(ids) - 1) // W
    return ids[:n * W].view(n, W).to(dev), ids[1:n * W + 1].view(n, W).to(dev)


def book(cx):
    text = open(BOOK, encoding="utf-8", errors="replace").read().replace("\r", "")
    ids, unk = encode(cx.cor, text)
    c1, c2 = int(len(ids) * 0.85), int(len(ids) * 0.90)
    meta = {"file": os.path.relpath(BOOK, C.HERE), "chars": len(ids), "teach_chars": c1, "calib_chars": c2 - c1,
            "held_chars": len(ids) - c2, "unk_chars": int((ids == unk).sum())}
    return windows_of(ids[:c1], cx.dev), windows_of(ids[c1:c2], cx.dev), windows_of(ids[c2:], cx.dev), meta


def teach(cx, arm_name, seed, method, data):
    """One day-dreaming run with the main notebook's spoc_teach (gate, consolidation, projected AdamW)."""
    trainable, gate, alpha, lr = METHODS[method]
    (tx, ty), (cx_, cy_), (hx, hy), (ox, oy), (px, _) = data
    arm = cx.build(arm_name)
    sweep = C.load_json("sweep.json")
    arm.load_state_dict(torch.load(ckpt_path(arm_name, sweep[arm_name]["best_lr"], seed), map_location=cx.dev))
    curve = []

    def measure(epoch, st):
        curve.append({**st, "teach_ce": eval_ce(arm, tx, ty)[0], "held_ce": eval_ce(arm, hx, hy)[0],
                      "old_ce": eval_ce(arm, ox, oy)[0]})

    cx.ns2["spoc_teach"](arm, (tx, ty), epochs=EPOCHS, lr=lr, batch=BATCH, gate=gate, alpha=alpha,
                         calib=(cx_, cy_), protect=px, trainable=trainable, p_min=P_MIN, seed=seed,
                         grad_clip=P.grad_clip, on_epoch=measure)
    first, last = curve[0], curve[-1]
    log(f"dream {arm_name} s{seed} {method:28s}: held CE {first['held_ce']:.3f}->{last['held_ce']:.3f}  "
        f"teach {first['teach_ce']:.3f}->{last['teach_ce']:.3f}  old {first['old_ce']:.4f}->{last['old_ce']:.4f}"
        f"  backward windows {last['backward_windows']} (+{last['screen_windows']} screened)  {last['wall_s']:.1f}s")
    del arm
    torch.cuda.empty_cache()
    return {"curve": curve, "protect_s": first["wall_s"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="RD-S4 v2")
    a = ap.parse_args()
    cx = Ctx()
    teach_w, calib_w, held_w, meta = book(cx)
    ox, oy = (t.long().to(cx.dev) for t in C.windows(cx.cor.select, OLD_WINDOWS))
    px, py = (t.long().to(cx.dev) for t in C.windows(cx.cor.probe, PROTECT_WINDOWS))
    data = (teach_w, calib_w, held_w, (ox, oy), (px, py))
    out_name = f"dream_{a.arm.replace(' ', '_')}.json"
    res = C.load_json(out_name, {"book": meta, "config": {"window": W, "batch": BATCH, "epochs": EPOCHS, "lr": LR,
                                                          "p_min": P_MIN, "old_windows": OLD_WINDOWS,
                                                          "protect_windows": PROTECT_WINDOWS},
                                 "methods": {k: list(v) for k, v in METHODS.items()}, "runs": {}})
    res["methods"] = {k: list(v) for k, v in METHODS.items()}
    log(f"dream: {meta}")
    for seed in P.seeds:
        for method in METHODS:
            key = f"{method}|{seed}"
            if key in res["runs"]:
                continue
            C.seed_all(seed)
            res["runs"][key] = teach(cx, a.arm, seed, method, data)
            C.save_json(out_name, res)


if __name__ == "__main__":
    main()
