from math import sqrt


def dot(u, v):  # dot product
    dot_product = 0
    for uu, vv in zip(u, v):
        dot_product += uu * vv
    return dot_product


def outer(u, v):  # outer product
    M = len(u)  # rows
    N = len(v)  # columns
    A = [[0 for _ in range(N)] for _ in range(M)]
    for i in range(M):
        for j in range(N):
            A[i][j] = u[i] * v[j]
    return A


def norm(v):
    squares_sum = 0
    for vv in v:
        squares_sum += vv**2
    return sqrt(squares_sum)


def normalize(v):
    n = norm(v)
    return [vv / n for vv in v]


def t(A):  # transpose
    M = len(A)  # rows -> columns
    N = len(A[0])  # columns -> rows
    At = [[0 for _ in range(M)] for _ in range(N)]
    for i in range(M):
        for j in range(N):
            At[j][i] = A[i][j]
    return At


def scale(a, A):
    M = len(A)  # rows
    N = len(A[0])  # columns
    aA = [[0 for _ in range(N)] for _ in range(M)]
    for i in range(M):
        for j in range(N):
            aA[i][j] = a * A[i][j]
    return aA


def add(A, B):
    M = len(A)  # rows
    N = len(A[0])  # columns
    C = [[0 for _ in range(N)] for _ in range(M)]
    for i in range(M):
        for j in range(N):
            C[i][j] = A[i][j] + B[i][j]
    return C


def matmul(A, B):
    M_A = len(A)  # rows of new matrix
    N_A = len(A[0])
    M_B = len(B)
    N_B = len(B[0])  # columns of new matrix
    if N_A != M_B:
        raise ValueError(
            "Number of columns of A must be equal to number of columns of B"
        )
    AB = [[0 for _ in range(N_B)] for _ in range(M_A)]
    Bt = t(B)
    for i in range(M_A):
        for j in range(N_B):
            AB[i][j] = dot(A[i], Bt[j])
    return AB


def matmulv(A, v):
    return [dot(row, v) for row in A]


def scalev(a, v):
    return [a * vv for vv in v]


def diagonal(v):
    N = len(v)
    D = [[0 if i != j else v[i] for i in range(N)] for j in range(N)]
    return D
