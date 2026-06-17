from math import sqrt
from random import sample


def calculate_euclidean_distance(p: tuple[float], q: tuple[float]) -> float:
    n = len(p)
    m = len(q)
    if m != n:
        raise ValueError("p, q must have the same dimension")
    squares_sum = 0
    for i in range(n):
        squares_sum += (p[i] - q[i]) ** 2
    return sqrt(squares_sum)


def compute_centroid(points: list[tuple[float]]) -> tuple[float]:
    N = len(points)
    if N == 0:
        raise ValueError("points must not be empty")
    n = len(points[0])  # number of components (dimension)
    centroid = []
    for i in range(n):
        component_sum = 0
        for p in points:
            component_sum += p[i]
        centroid.append(component_sum / len(points))
    return tuple(centroid)


def stopping_condition(P, Q):
    n = len(P)
    m = len(Q)
    if n != m:
        raise ValueError("P, Q must have the same number of points")
    stop = True
    for p, q in zip(P, Q):
        distance = calculate_euclidean_distance(p, q)
        if distance >= 0.001:
            stop = False
            break
    return stop


def find_nearest_centroid(point: tuple[float], centroids: list[tuple[float]]) -> int:
    min_distance = float("inf")
    nearest_centroid = -1
    K = len(centroids)
    for k in range(K):
        distance = calculate_euclidean_distance(point, centroids[k])
        if distance < min_distance:
            min_distance = distance
            nearest_centroid = k
    return nearest_centroid


def compute_new_centroids(
    points: list[tuple[float]], clusters_tags: list[int], K: int
) -> list[tuple[float]]:
    new_centroids = []
    # for each cluster, get all points assigned and compute their centroid
    for i in range(K):
        cluster_points = [p for p, k in zip(points, clusters_tags) if k == i]
        if len(cluster_points) == 0:
            random_point = sample(points, 1)[0]
            new_centroids.append(random_point)  # set a random point as centroid
            continue
        new_centroid = compute_centroid(cluster_points)
        new_centroids.append(new_centroid)
    return new_centroids


def kmeans_clustering(K: int, points: list[tuple[float]]):
    # dynamic K adjustment: Number of unique points must be at least K
    unique_points = len(set(points))
    if K > unique_points:
        print(f"Number of unique points must be at least K: setting K={unique_points}")
        K = unique_points

    centroids = sample(points, K)  # chosen at random from the datapoints (deliberatr)
    N = len(points)
    clusters_tags = [-1] * N  # the cluster assigned to each point

    while True:
        # find nearest centroid for each point
        for i in range(N):
            # assigned nearest centroid to point i
            clusters_tags[i] = find_nearest_centroid(points[i], centroids)
        # compute new centroids
        new_centroids = compute_new_centroids(points, clusters_tags, K)
        # check stopping condition
        if stopping_condition(centroids, new_centroids):
            break
        # prepare next iteration
        centroids = new_centroids

    return points, clusters_tags


points, clusters_tags = kmeans_clustering(
    3,
    [(1, 0), (1, 0), (1, 0), (100, 200)],
)

print(points, clusters_tags)
