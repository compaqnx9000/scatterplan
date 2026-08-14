import numpy as np
from numba import njit, prange
import time
import platform
import numba


@njit(parallel=True, cache=True)
def heavy_compute(a):
    n = a.shape[0]
    out = np.zeros(n)
    for i in prange(n):
        s = 0.0
        for j in range(1000):
            s += np.sin(a[i]) * np.cos(a[i] + j)
        out[i] = s
    return out


print("CPU:", platform.processor())
print("Numba threads:", numba.get_num_threads())
a = np.linspace(0, 10, 1_000_000)

t0 = time.perf_counter()
res = heavy_compute(a)
t1 = time.perf_counter()

print(f"Time: {t1 - t0:.2f}s")
