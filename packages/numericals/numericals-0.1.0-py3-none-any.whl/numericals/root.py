def bisection(function, alpha, beta, tolerance=1e-10, max_iterations=10_000):
    if function(alpha) == 0:
        return alpha
    if function(beta) == 0:
        return beta
    if function(alpha) * function(beta) > 0:
        raise ValueError

    for _ in range(max_iterations):
        midpoint = (alpha + beta) * 0.5
        fm = function(midpoint)
        if (abs(beta - alpha) * 0.5 < tolerance) or (fm == 0):
            return midpoint
        if fm * function(alpha) < 0:
            beta = midpoint
        else:
            alpha = midpoint

    return (alpha + beta) * 0.5


def secant(function, x0, x1, tolerance=1e-10, max_iterations=10_000):
    for _ in range(max_iterations):
        x2 = x1 - function(x1) * (x1 - x0) / (function(x1) - function(x0))

        x0 = x1
        x1 = x2

        if abs(x0 - x1) < tolerance:
            return x2

    return x2
