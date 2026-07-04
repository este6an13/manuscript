from math import sqrt

def euclidean_distance(p: tuple[float], q: tuple[float]) -> float:
    n = len(p)
    m = len(q)
    if m != n:
        raise ValueError("p, q must have the same dimension")
    if n == 0:  # m == 0
        raise ValueError("p, q dimension must be greater than zero")
    squares_sum = 0
    for i in range(n):
        squares_sum += (p[i] - q[i]) ** 2
    return sqrt(squares_sum)
