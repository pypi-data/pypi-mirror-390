import math


def golden(function, alpha, beta, tolerance=1e-10, max_iterations=10_000):

    reciprocal_phi = (math.sqrt(5) - 1) * 0.5

    a = min(alpha, beta)
    b = max(alpha, beta)
    h = b - a

    for _ in range(max_iterations):
        if b - a <= tolerance:
            return (b + a) * 0.5

        c = b - (b - a) * reciprocal_phi
        d = a + (b - a) * reciprocal_phi

        if function(c) < function(d):
            b = d

        else:
            a = c

    return (a + b) * 0.5
