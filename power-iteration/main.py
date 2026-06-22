from random import random

from linear_algebra.utils import dot, matmulv, normalize


def power_iteration(B, max_iter=100, tol=1e-9):
    N = len(B)
    v = normalize([random() for _ in range(N)])
    for _ in range(max_iter):
        v_new = normalize(matmulv(B, v))
        if 1 - abs(dot(v, v_new)) < tol:
            break
        v = v_new
    λ = dot(v, matmulv(B, v))  # eigenvalue
    return λ, v
