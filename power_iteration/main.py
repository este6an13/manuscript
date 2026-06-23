from random import random

from linear_algebra.utils import add, dot, matmulv, normalize, outer, scale


def power_iteration(B, max_iter=100, tol=1e-15):
    N = len(B)
    v = normalize([random() for _ in range(N)])
    for _ in range(max_iter):
        v_new = normalize(matmulv(B, v))
        if 1 - abs(dot(v, v_new)) < tol:
            break
        v = v_new
    λ = dot(v, matmulv(B, v))  # eigenvalue
    return λ, v


def deflate(B, λ, v):
    P = outer(v, v)
    S = scale(λ, P)
    B = add(B, scale(-1, S))
    return B


def eigen_decomposition(B, d):
    eigenvalues = []
    eigenvectors = []
    B_copy = B.copy()
    for _ in range(d):
        λ, v = power_iteration(B_copy)
        eigenvalues.append(λ)
        eigenvectors.append(v)
        B_copy = deflate(B_copy, λ, v)
    return eigenvalues, eigenvectors


if __name__ == "__main__":
    B = [[2.0, 1.0], [1.0, 2.0]]
    eigenvalues, eigenvectors = eigen_decomposition(B, d=2)
    print(eigenvalues, eigenvectors)
