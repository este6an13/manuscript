from linear_algebra.utils import addv, scalev
from geometry.utils import euclidean_distance

f = lambda params, new_params, tol : euclidean_distance(params, new_params) < tol  # noqa: E731
g = lambda i, max_iters : i > max_iters # noqa: E731

def stopping_condition(f, g):
    if any([f, g]):
        return True
    return False


def gradient_descent(fn, params, lr, max_iters=1000, tol=1e-12):
    i = 0
    while True:
        i += 1
        new_params = addv(params, scalev(-lr, fn(params)))
        if stopping_condition(f(params, new_params, tol), g(i, max_iters)):
            return new_params
        # next iteration
        params = new_params


if __name__ == "__main__":
    def fn(params):
        x = params[0]
        return [2 * (x - 3)]
    params = [0.0]
    lr = 0.1
    params = gradient_descent(fn, params, lr)
    print(params) #  [2.9999999999963927]

    def fn(params):
        x = params[0]
        y = params[1]
        return [6 * x + 2 * y - 4, 2 * x + 2 * y + 6]

    params = [0.0, 0.0]
    lr = 0.1
    params = gradient_descent(fn, params, lr)
    print(params) #  [2.499999999997129, -5.499999999993069]

