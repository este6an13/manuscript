from math import sqrt

from linear_algebra.utils import diagonal, matmul, matmulv, scalev, t
from power_iteration.main import eigen_decomposition


def compute_U(A, eigenvectors, SV):  # left singular vectors
    M = len(A)  # number of rows
    Ut = [
        (scalev(1 / sv, matmulv(A, v))) if sv > 1e-9 else [0.0] * M
        for sv, v in zip(SV, eigenvectors)
    ]
    return t(Ut)


def svd(A):
    B = matmul(t(A), A)  # B is squared and symmetric
    N = len(B)
    eigenvalues, eigenvectors = eigen_decomposition(B, d=N)
    Vt = [v for v in eigenvectors]
    SV = [sqrt(max(0.0, λ)) for λ in eigenvalues]  # singular values
    S = diagonal(SV)
    U = compute_U(A, eigenvectors, SV)
    return U, S, Vt, SV


if __name__ == "__main__":
    A = [
        [1.0, 2.0],
        [3.0, 4.0],
        [5.0, 6.0],
    ]

    U, S, Vt, SV = svd(A)

    print("Singular Values: ", [round(sv, 7) for sv in SV])
    print("U: ", U)
    print("S: ", S)
    print("Vt: ", Vt)
    print(f"U shape: {len(U)}x{len(U[0])}")
    print(f"S shape: {len(S)}x{len(S[0])}")
    print(f"Vt shape: {len(Vt)}x{len(Vt[0])}")
    print(f"A shape: {len(A)}x{len(A[0])}")

    reconstructed_A = matmul(matmul(U, S), Vt)
    print("Reconstructed A: ", reconstructed_A)
