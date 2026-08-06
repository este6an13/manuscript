from collections import Counter
from random import choices

from decision_tree.main import DecisionTree
from linear_algebra.utils import t


# X : population; k : sample size
def bootstrap(X, k):
    return choices(X, k=k)  # "choices" for sampling with replacement


# repeat bootstrap sampling n times
def repeat_bootstrap(X, k, n):
    reps = []
    for _ in range(n):
        reps.append(bootstrap(X, k=k))
    return reps


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


def most_frequent(y) -> int:
    # sorting to deterministically pick lowest class if ties
    return Counter(sorted(y)).most_common(1)[0][0]


def split(AB, idx):
    A = []
    B = []
    for ab in AB:
        A.append(ab[:idx])
        B.append(ab[idx:])
    return A, B


class Bagging:
    def __init__(self, k, n):
        self.k = k
        self.n = n
        self.trees = [DecisionTree() for _ in range(n)]

    def fit(self, X, y):
        idx = len(X[0])  # f: features
        Xy = concat(X, deepen(y))  # concat for convenience, sampling over 1 population
        reps = repeat_bootstrap(Xy, self.k, self.n)
        for i in range(self.n):
            X, y = split(reps[i], idx)  # idx is f + 1 - 1 = f
            self.trees[i].fit(X, ascend(y))

    def predict(self, X):
        # z : array: each element is preds of a tree
        # zz : one element of z: preds of a tree
        # tz : transposed z, each element is preds of a sample accross trees
        # tzz: one element of tz: preds of a sample accorss trees
        # y : final preds after voting: each element is the pred of a single sample
        # yy : one element of y: the pred of a single sample
        y = []
        z = []
        for i in range(self.n):
            zz = self.trees[i].predict(X)
            z.append(zz)

        # votings
        tz = t(z)  # transpose to iterate column-wise
        for tzz in tz:
            yy = most_frequent(tzz)
            y.append(yy)
        return y


if __name__ == "__main__":
    bagging = Bagging(k=4, n=5)

    # temperature (celsius), humidity (%)
    X = [
        [15, 40],
        [20, 35],
        [32, 85],
        [35, 90],
    ]

    # play outside?
    y = [1, 1, 0, 0]

    bagging.fit(X, y)

    yy = bagging.predict([[25, 30], [35, 55], [30, 60]])
    print(yy)  # [1, 0, 0]
