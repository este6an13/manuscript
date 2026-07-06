from linear_algebra.utils import t


class Node:
    def __init__(
        self,
        left: "Node" | None = None,
        right: "Node" | None = None,
        threshold: float | None = None,
        feature: int | None = None,
        value: float | None = None,
    ):
        self.left = left
        self.right = right
        self.threshold = threshold
        self.feature = feature
        self.value = value

    def is_leaf(self):
        return self.value is not None

    def is_internal(self):
        return self.value is None


class DecisionTree:
    def __init__(self):
        self.root = None

    def _gini(self, y) -> float:
        n = len(y)
        if n == 0:
            return 0.0

        frequencies = {}
        for yy in y:
            frequencies[yy] = 1 if yy not in frequencies else frequencies[yy] + 1

        proportions = {}
        for yy in frequencies:
            proportions[yy] = frequencies[yy] / n

        G = 1 - sum([p**2 for p in proportions.values()])

        return G

    def _wavg(self, weights, values) -> float:
        N = sum(weights)
        return sum([w * v for w, v in zip(weights, values)]) / N

    def __best_split(self, X, y):
        best_gini = 1.0
        best_feature = None  # idx of the feature
        best_threshold = None  # picked threshold: feature value

        Xt = t(X)  # columns are rows now for easier iteration

        # we iterate over each feature (column)
        for idx, feature_column in enumerate(Xt):
            # feature_value_i is our threshold in this iteration
            for feature_value_i in feature_column:
                # our split
                y_left = []
                y_right = []
                # we check each feature value in the column and compare against the selected threshold
                for feature_value_j, label in zip(feature_column, y):
                    if feature_value_j <= feature_value_i:
                        y_left.append(label)
                    else:
                        y_right.append(label)

                # we have our partition, we now compute a weighted average gini
                W1, W2 = len(y_left), len(y_right)
                G_left, G_right = self._gini(y_left), self._gini(y_right)
                wavg_gini = self._wavg([W1, W2], [G_left, G_right])

                # we update our best values
                if wavg_gini <= best_gini:
                    best_gini = wavg_gini
                    best_feature = idx
                    best_threshold = feature_value_i

        # found (row, col) feature value (threshold) that best splits the data
        # threshold (actual i, j value), feature (j column): we don't need i (row)
        return best_threshold, best_feature
