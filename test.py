def multiple_square_matrix(a, b, size: int):
    if len(a) != size * size or len(b) != size * size:
        raise Exception("input error")

    result = []
    for i in range(size):
        for j in range(size):
            c = 0
            for k in range(size):
                c += a[(i * size) + k] * b[(k * size) + j]
            result.append(c)

    return result


a = (1.0, 0.0, 0.0, 0.0, 0.0, 0.5591928958892822, -0.829037606716156, 0.0, -0.0, 0.829037606716156, 0.5591928958892822, 0.0, -941.1969604492188, -791.4107055664062, 1772.2921142578125, 1.0)
b = (1.545456051826477, 0.0, 0.0, 0.0, 0.0, 2.7474775314331055, 0.0, 0.0, 0.0, 0.0, 1.0020661354064941, 1.0, 0.0, 0.0, -50.10330581665039, 0.0)

print(multiple_square_matrix(a, b, 4))