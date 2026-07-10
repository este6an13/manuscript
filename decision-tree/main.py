from linear_algebra.utils import t

from collections import Counter


class Node:
    def __init__(
        self,
        left: "Node" | None = None,
        right: "Node" | None = None,
        threshold: float | None = None,
        feature: int | None = None,
        value: float | None = None,
    ):
        # internal nodes features
        self.left = left
        self.right = right
        self.threshold = threshold  # value that decides going left or right
        self.feature = feature  # the column to check when splitting and predicting
        # leaf nodes features
        self.value = value  # class assigned to the leaf

    # mutually exclusive: a node cannot be leaf and internal at the same time
    def is_leaf(self):
        return self.value is not None

    def is_internal(self):
        return self.value is None


class DecisionTree:
    def __init__(self, max_depth: int | None = None, min_samples_split: int | None = 2):
        self.root = None
        # hyperparameters
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split

    # metric we use to define the threshold
    # a lower threshold decides which threshold ot choose (where to split)
    # the thrshold that gives the lowest gini, is the best threshold
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

    # helper utility to compute a weighted average
    def _wavg(self, weights, values) -> float:
        N = sum(weights)
        return sum([w * v for w, v in zip(weights, values)]) / N

    # finds the threshold and feature (column) that decides where to split
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

    # performs the actual split of the dataset during training/fitting
    def _split(self, X, y, threshold, feature):
        Xt = t(X)
        column = Xt[feature]
        left_X, left_y, right_X, right_y = [], [], [], []
        for i, xx in enumerate(column):
            if xx <= threshold:
                left_X.append(X[i])
                left_y.append(y[i])
            else:
                right_X.append(X[i])
                right_y.append(y[i])
        return left_X, left_y, right_X, right_y

    # helper function to get the most frequent class (value) of a labels vector (y)
    def _top_class(self, y) -> int:
        return Counter(y).most_common(1)[0][0]  # ('class', freq)[0] -> 'class'

    # helper to organize stopping conditions: used by _build_tree (fitting/training procedure)
    def _stopping_conditions(self):
        f = lambda depth: self.max_depth is not None and depth >= self.max_depth  # noqa: E731
        g = lambda y: len(y) < self.min_samples_split  # noqa: E731
        h = lambda y: self._gini(y) == 00  # noqa: E731
        return f, g, h

    # constructs the tree recursively: this is the fitting/training procedure
    # note: we can see it's deterministic, not probabilistic, no gradient descent
    def _build_tree(self, X, y, depth=0):
        # recursion base case
        f, g, h = self._stopping_coditions
        if any([f(depth), g(y), h(y)]):
            return Node(value=self._top_class(y))

        best_threshold, best_feature = self.__best_split(X, y)
        if best_threshold is None or best_feature is None:
            return Node(value=self._top_class(y))

        left_X, left_y, right_X, right_y = self._split(
            X, y, best_threshold, best_feature
        )

        left_child = self._build_tree(left_X, left_y, depth + 1)
        right_child = self._build_tree(right_X, right_y, depth + 1)

        return Node(
            left=left_child,
            right=right_child,
            threshold=best_threshold,
            feature=best_feature,
        )

    # the fitting is just building our tree from our samples and gini metric results
    def fit(self, X, y):
        self.root = self._build_tree(X, y)
        return self

    # traverse the tree recursively to predict the class of a sample: the leaf value (class) is the predicted value
    def _predict_sample(self, x, node: Node):
        if node.is_leaf():
            return node.value
        xx = x[node.feature]
        if xx <= node.threshold:
            return self._predict_sample(x, node.left)
        return self._predict_sample(x, node.right)

    # predict is running the tree traversal (_predict_sample) on each sample of the dataset X
    def predict(self, X):
        preds = []
        for x in X:
            pred = self._predict_sample(x, self.root)
            preds.append(pred)
        return preds
