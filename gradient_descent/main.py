from linear_algebra.utils import addv, scalev

def gradient_descent(fn, params, lr, max_iters=1000):
    i = 0
    while True:
        new_params = addv(params, scalev(-lr, fn(params)))
        params = new_params
        i += 1
        if i >= max_iters:
            break
    return params


if __name__ == "__main__":
    def fn(params):
        x = params[0]
        return [2 * (x - 3)]
    params = [0.0]
    lr = 0.1
    params = gradient_descent(fn, params, lr)
    print(params) # [2.999999999999999]

    def fn(params):
        x = params[0]
        y = params[1]
        return [6 * x + 2 * y - 4, 2 * x + 2 * y + 6]

    params = [0.0, 0.0]
    lr = 0.1
    params = gradient_descent(fn, params, lr)
    print(params) # [2.4999999999999987, -5.4999999999999964]

