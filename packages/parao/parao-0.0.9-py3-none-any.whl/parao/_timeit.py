from timeit import timeit as _timeit


def bti(
    subject,
    r=5,
    n: int = None,
    n0: int = 100,
    nf: int = 10,
    tt: float = 0.3,
    p: int = 4,
):
    vs = []
    for i in range(r):
        v = _timeit(subject, number=n or n0)
        if not i and n is None:
            n = n0
            while v < tt:
                n *= nf
                v = _timeit(subject, number=n)
        vs.append(v)

    vn = len(vs)
    vm = sum(vs) / vn
    vv = sum(v * v for v in vs) / vn
    vd = (vv - vm * vm) ** 0.5
    vr = vd / vm
    print(f"{vm:.{p}f}+-{vd:.{p}f} ({100 * vr:5.3f}%)")
