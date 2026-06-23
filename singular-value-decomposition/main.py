from math import sqrt

from linear_algebra.utils import matmul, matmulv, scale, t
from power_iteration.main import eigen_decomposition


def compute_left_singular_vectors(A, eigenvectors, S):
    U = [scale(1 / sv, matmulv(A, v)) for sv, v in zip(S, eigenvectors)]
    return U


def svd(A):
    B = matmul(t(A), A)  # B is squared and symmetric
    N = len(B)
    eigenvalues, eigenvectors = eigen_decomposition(B, d=N)
    Vt = [v for v in eigenvectors]
    S = [sqrt(max(0.0, λ)) for λ in eigenvalues]  # singular values
    U = compute_left_singular_vectors(A, eigenvectors, S)
    return U, S, Vt
