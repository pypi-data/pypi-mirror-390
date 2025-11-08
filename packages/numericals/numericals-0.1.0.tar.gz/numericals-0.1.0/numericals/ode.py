def euler(function, alpha, beta, y0, n):
    values = []
    h = (beta - alpha) / n
    x = alpha
    y = y0
    values.append((x, y))

    for i in range(n):
        y = y + h * function(x, y)
        x = x + h
        values.append((x, y))

    return values
