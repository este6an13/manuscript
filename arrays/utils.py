# [1, 1, 1] -> [[1], [1], [1]]
def deepen(y):  # to me it feels like go deeper, so I chose this name
    res = []
    for yy in y:
        res.append([yy])
    return res


# [[1], [1], [1]] -> [1, 1, 1]
def ascend(y):  # just the opposite of deepen
    res = []
    for yy in y:
        res.append(yy[0])
    return res


def concat(A, B):
    M = len(A)
    N = len(B)
    if M != N:
        raise ValueError("A and B must be the same size")
    AB = [0 for _ in range(M)]
    for i in range(M):
        AB[i] = A[i] + B[i]
    return AB


def split(AB, idx):
    A = []
    B = []
    for ab in AB:
        A.append(ab[:idx])
        B.append(ab[idx:])
    return A, B
