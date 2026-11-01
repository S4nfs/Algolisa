"""Supplementary speed measurement: the chunked recurrent arms with compiler fusion.

The protocol's speed stage (run.py speed) runs every arm's own eager code; Mamba's scan is a hand-fused Triton
kernel, the Transformer's attention is flash attention, S4 uses cuFFT, and RD-S4 v2 runs plain PyTorch operations.
Here every chunked recurrent arm (S4, Mamba, RD-S4 v2) gets the same treatment: its per-chunk prefill function
and its decode step are compiled by TorchInductor (fixed shapes), and measured with and without CUDA-graph replay.
Outputs are checked against the eager code. Writes results/speed_compiled.json.

    python speed_compiled.py
"""
import statistics
import time

import torch

import common as C
import run as RUN

P = C.P
ARMS = ("S4", "Mamba", "RD-S4 v2")
CTX = (8192, 32768, 131072)


def timed(fn, reps=3):
    out = []
    for _ in range(reps):
        torch.cuda.empty_cache()
        base = torch.cuda.memory_allocated()
        torch.cuda.reset_peak_memory_stats()
        C.sync()
        t0 = time.perf_counter()
        fn()
        C.sync()
        out.append((time.perf_counter() - t0, (torch.cuda.max_memory_allocated() - base) / 2**20))
    return statistics.median(t for t, _ in out), statistics.median(m for _, m in out)


def main():
    cx = RUN.Ctx()
    sweep = C.load_json("sweep.json")
    src = cx.cor.test[2_200_000:2_200_000 + max(CTX)].long().to(cx.dev)
    res = {"gpu_before": C.gpu_snapshot(), "chunk": P.speed_chunk, "arms": {}}
    for name in ARMS:
        arm = cx.build(name)
        arm.load_state_dict(torch.load(RUN.ckpt_path(name, sweep[name]["best_lr"], 0), map_location=cx.dev))
        arm.eval()
        rec = {}
        try:
            with torch.no_grad():
                lg_e, _ = arm.prefill(src[:8192].view(1, -1), chunk=P.speed_chunk)
            t0 = time.perf_counter()
            arm._chunk = torch.compile(arm._chunk, dynamic=False)     # instance attribute shadows the method
            with torch.no_grad():
                lg_c, _ = arm.prefill(src[:8192].view(1, -1), chunk=P.speed_chunk)
            C.sync()
            rec["compile_s"] = time.perf_counter() - t0
            rec["max_abs_logit_diff_vs_eager"] = (lg_e.float() - lg_c.float()).abs().max().item()
            gp = RUN.GraphPrefill(arm, P.speed_chunk, src[:P.speed_chunk].view(1, -1))
            for c in CTX:
                x = src[:c].view(1, -1)
                with torch.no_grad():
                    t, m = timed(lambda: arm.prefill(x, chunk=P.speed_chunk))
                    tg, mg = timed(lambda: gp(x))
                rec[str(c)] = {"compiled_prefill_tok_s": c / t, "compiled_peak_mb": m,
                               "compiled_graph_prefill_tok_s": c / tg, "compiled_graph_peak_mb": max(mg, gp.pool_mb)}
                RUN.log(f"compiled {name:9s} ctx {c:>7,}: prefill {c / t:>10,.0f} tok/s ({m:6.1f} MB)  "
                        f"+graph {c / tg:>10,.0f} tok/s ({max(mg, gp.pool_mb):6.1f} MB)")
            del gp
            # decode: compiled step captured in CUDA graphs, as the protocol's graph decode
            arm.step = torch.compile(arm.step, dynamic=False)
            x = src[:32768].view(1, -1)
            with torch.no_grad():
                RUN.measure_speed(arm, src[:4096].view(1, -1))
                ms = [RUN.measure_speed(arm, x) for _ in range(3)]
            rec["decode_compiled_graph_tok_s_32k"] = statistics.median(m["decode_graph_tok_s"] for m in ms)
            RUN.log(f"compiled {name:9s} decode (graphs) @32K: {rec['decode_compiled_graph_tok_s_32k']:,.0f} tok/s")
        except Exception as exc:                                       # noqa: BLE001
            rec["error"] = repr(exc)
            RUN.log(f"compiled {name}: failed ({exc!r})")
        res["arms"][name] = rec
        del arm
        torch.cuda.empty_cache()
        torch._dynamo.reset()
    res["gpu_after"] = C.gpu_snapshot()
    C.save_json("speed_compiled.json", res)


if __name__ == "__main__":
    main()
