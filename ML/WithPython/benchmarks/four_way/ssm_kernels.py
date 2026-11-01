"""Selective scan (Mamba-1) as Triton kernels, plus a sequential PyTorch reference.

The official Mamba CUDA kernels cannot be compiled on this machine (nvcc 12.4 has no sm_120
target), and a pure-PyTorch selective scan materialises a (B, L, D, N) tensor several times
per layer, which would make Mamba roughly ten times slower than the architecture really is.
These kernels follow the same algorithm as the official ones: the state lives in registers,
one program walks the sequence for a block of channels, and nothing of size L*D*N is written
in the forward pass. The backward pass recomputes the states into a scratch buffer and then
runs the adjoint recurrence in reverse.

Recurrence, per channel d and state n:
    a_t = exp(dt_t * A),  h_t = a_t * h_{t-1} + dt_t * x_t * B_t,  y_t = <h_t, C_t> + D * x_t
"""
import glob
import os
import sysconfig

import torch
import triton
import triton.language as tl


def _ensure_python_headers():
    """Triton compiles a small C launcher against Python.h. This machine's system Python has
    no -dev headers, so fall back to an ABI-compatible CPython include tree of the same minor
    version that already ships inside the venv. Only this process's compiler search path changes."""
    if os.path.exists(os.path.join(sysconfig.get_paths()["include"], "Python.h")):
        return
    ver = sysconfig.get_python_version()
    site = sysconfig.get_paths()["purelib"]
    for h in sorted(glob.glob(os.path.join(site, "**", f"python{ver}", "Python.h"), recursive=True)):
        inc = os.path.dirname(h)
        if os.path.exists(os.path.join(inc, "pyconfig.h")):
            prev = os.environ.get("C_INCLUDE_PATH")
            os.environ["C_INCLUDE_PATH"] = inc + (os.pathsep + prev if prev else "")
            return


_ensure_python_headers()


@triton.jit
def _fwd_kernel(X, DT, A, Bm, Cm, Dv, H0, Y, HT, L, DI, sx_b, sx_l, sb_b, sb_l,
                N: tl.constexpr, BD: tl.constexpr, HAS_H0: tl.constexpr):
    pb = tl.program_id(0)
    pd = tl.program_id(1)
    od = pd * BD + tl.arange(0, BD)
    on = tl.arange(0, N)
    md = od < DI
    m2 = md[:, None]
    a_mat = tl.load(A + od[:, None] * N + on[None, :], mask=m2, other=0.0)
    dv = tl.load(Dv + od, mask=md, other=0.0)
    hoff = pb * DI * N + od[:, None] * N + on[None, :]
    if HAS_H0:
        h = tl.load(H0 + hoff, mask=m2, other=0.0)
    else:
        h = tl.zeros((BD, N), dtype=tl.float32)
    xp = X + pb * sx_b + od
    dp = DT + pb * sx_b + od
    yp = Y + pb * sx_b + od
    bp = Bm + pb * sb_b + on
    cp = Cm + pb * sb_b + on
    for t in range(L):
        x = tl.load(xp + t * sx_l, mask=md, other=0.0)
        dt = tl.load(dp + t * sx_l, mask=md, other=0.0)
        b = tl.load(bp + t * sb_l)
        c = tl.load(cp + t * sb_l)
        h = tl.exp(dt[:, None] * a_mat) * h + (dt * x)[:, None] * b[None, :]
        y = tl.sum(h * c[None, :], axis=1) + dv * x
        tl.store(yp + t * sx_l, y, mask=md)
    tl.store(HT + hoff, h, mask=m2)


@triton.jit
def _bwd_kernel(X, DT, A, Bm, Cm, Dv, DY, HS, DX, DDT, DA_P, DB_P, DC_P, DD_P,
                L, DI, ND, sx_b, sx_l, sb_b, sb_l,
                N: tl.constexpr, BD: tl.constexpr):
    pb = tl.program_id(0)
    pd = tl.program_id(1)
    od = pd * BD + tl.arange(0, BD)
    on = tl.arange(0, N)
    md = od < DI
    m2 = md[:, None]
    a_mat = tl.load(A + od[:, None] * N + on[None, :], mask=m2, other=0.0)
    dv = tl.load(Dv + od, mask=md, other=0.0)
    xp = X + pb * sx_b + od
    dp = DT + pb * sx_b + od
    gp = DY + pb * sx_b + od
    bp = Bm + pb * sb_b + on
    cp = Cm + pb * sb_b + on
    hs = HS + pb * L * DI * N + od[:, None] * N + on[None, :]

    # pass 1: recompute every state into the scratch buffer
    h = tl.zeros((BD, N), dtype=tl.float32)
    for t in range(L):
        x = tl.load(xp + t * sx_l, mask=md, other=0.0)
        dt = tl.load(dp + t * sx_l, mask=md, other=0.0)
        b = tl.load(bp + t * sb_l)
        h = tl.exp(dt[:, None] * a_mat) * h + (dt * x)[:, None] * b[None, :]
        tl.store(hs + t * DI * N, h, mask=m2)

    # pass 2: adjoint recurrence in reverse time.  g holds dL/dh_t.
    g = tl.zeros((BD, N), dtype=tl.float32)
    da_acc = tl.zeros((BD, N), dtype=tl.float32)
    dd_acc = tl.zeros((BD,), dtype=tl.float32)
    h_cur = tl.load(hs + (L - 1) * DI * N, mask=m2, other=0.0)
    pbase = (pb * ND + pd) * L * N
    for i in range(L):
        t = L - 1 - i
        x = tl.load(xp + t * sx_l, mask=md, other=0.0)
        dt = tl.load(dp + t * sx_l, mask=md, other=0.0)
        dy = tl.load(gp + t * sx_l, mask=md, other=0.0)
        b = tl.load(bp + t * sb_l)
        c = tl.load(cp + t * sb_l)
        a_t = tl.exp(dt[:, None] * a_mat)
        g = g + dy[:, None] * c[None, :]
        tl.store(DC_P + pbase + t * N + on, tl.sum(dy[:, None] * h_cur, axis=0))
        h_prev = tl.load(hs + (t - 1) * DI * N, mask=m2 & (t > 0), other=0.0)
        ga = g * h_prev * a_t                                   # dL/d(dt*A)
        gb = tl.sum(g * b[None, :], axis=1)                     # dL/d(dt*x)
        ddt = tl.sum(ga * a_mat, axis=1) + gb * x
        da_acc += ga * dt[:, None]
        dd_acc += dy * x
        tl.store(DX + pb * sx_b + t * sx_l + od, gb * dt + dy * dv, mask=md)
        tl.store(DDT + pb * sx_b + t * sx_l + od, ddt, mask=md)
        tl.store(DB_P + pbase + t * N + on, tl.sum(g * (dt * x)[:, None], axis=0))
        g = g * a_t
        h_cur = h_prev
    tl.store(DA_P + pb * DI * N + od[:, None] * N + on[None, :], da_acc, mask=m2)
    tl.store(DD_P + pb * DI + od, dd_acc, mask=md)


def _block(B, DI):
    # enough programs to occupy the GPU, without splitting channels finer than necessary
    return 32 if B * triton.cdiv(DI, 32) >= 40 else 16


def scan_fwd(x, dt, A, Bm, Cm, D, h0=None):
    """y (B,L,DI), h_T (B,DI,N). Inputs fp32 contiguous: x, dt (B,L,DI); Bm, Cm (B,L,N);
    A (DI,N) negative real; D (DI,); optional h0 (B,DI,N)."""
    Bsz, L, DI = x.shape
    N = A.shape[1]
    y = torch.empty_like(x)
    hT = torch.empty(Bsz, DI, N, device=x.device, dtype=torch.float32)
    BD = _block(Bsz, DI)
    grid = (Bsz, triton.cdiv(DI, BD))
    _fwd_kernel[grid](x, dt, A, Bm, Cm, D, h0 if h0 is not None else hT, y, hT, L, DI,
                      x.stride(0), x.stride(1), Bm.stride(0), Bm.stride(1),
                      N=N, BD=BD, HAS_H0=h0 is not None)
    return y, hT


def scan_bwd(x, dt, A, Bm, Cm, D, dy):
    Bsz, L, DI = x.shape
    N = A.shape[1]
    BD = _block(Bsz, DI)
    ND = triton.cdiv(DI, BD)
    hs = torch.empty(Bsz, L, DI, N, device=x.device, dtype=torch.float32)
    dx, ddt = torch.empty_like(x), torch.empty_like(x)
    da_p = torch.empty(Bsz, DI, N, device=x.device, dtype=torch.float32)
    db_p = torch.empty(Bsz, ND, L, N, device=x.device, dtype=torch.float32)
    dc_p = torch.empty(Bsz, ND, L, N, device=x.device, dtype=torch.float32)
    dd_p = torch.empty(Bsz, DI, device=x.device, dtype=torch.float32)
    _bwd_kernel[(Bsz, ND)](x, dt, A, Bm, Cm, D, dy, hs, dx, ddt, da_p, db_p, dc_p, dd_p,
                           L, DI, ND, x.stride(0), x.stride(1), Bm.stride(0), Bm.stride(1),
                           N=N, BD=BD)
    return dx, ddt, da_p.sum(0), db_p.sum(1), dc_p.sum(1), dd_p.sum(0)


class _SelectiveScan(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, dt, A, Bm, Cm, D):
        x, dt, Bm, Cm = (t.contiguous().float() for t in (x, dt, Bm, Cm))
        A, D = A.contiguous().float(), D.contiguous().float()
        y, _ = scan_fwd(x, dt, A, Bm, Cm, D)
        ctx.save_for_backward(x, dt, A, Bm, Cm, D)
        return y

    @staticmethod
    def backward(ctx, dy):
        x, dt, A, Bm, Cm, D = ctx.saved_tensors
        return scan_bwd(x, dt, A, Bm, Cm, D, dy.contiguous().float())


def selective_scan(x, dt, A, Bm, Cm, D):
    """Differentiable selective scan from a zero initial state."""
    return _SelectiveScan.apply(x, dt, A, Bm, Cm, D)


def selective_scan_ref(x, dt, A, Bm, Cm, D, h0=None):
    """Sequential reference: the definition, written as plainly as possible."""
    Bsz, L, DI = x.shape
    h = torch.zeros(Bsz, DI, A.shape[1], device=x.device, dtype=x.dtype) if h0 is None else h0
    ys = []
    for t in range(L):
        h = torch.exp(dt[:, t, :, None] * A) * h + (dt[:, t] * x[:, t])[..., None] * Bm[:, t, None, :]
        ys.append((h * Cm[:, t, None, :]).sum(-1) + D * x[:, t])
    return torch.stack(ys, 1), h
