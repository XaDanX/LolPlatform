from dataclasses import dataclass
from functools import lru_cache
import functools

from utils.logger import Logger
from timeit import default_timer as timer


def benchmark(func):
    def inner(*args, **kwargs):
        start = timer()
        x = func(*args, **kwargs)
        elapsed_time = timer() - start
        Logger.log(f"{func} took: {elapsed_time}ms")
        return x

    return inner



def ignore_unhashable(func):
    uncached = func.__wrapped__
    attributes = functools.WRAPPER_ASSIGNMENTS + ('cache_info', 'cache_clear')
    @functools.wraps(func, assigned=attributes)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError as error:
            if 'unhashable type' in str(error):
                return uncached(*args, **kwargs)
            raise
    wrapper.__uncached__ = uncached
    return wrapper

@dataclass
class Vec3:
    x: float
    y: float
    z: float



@dataclass
class Vec2:
    x: float
    y: float


@ignore_unhashable
@lru_cache(maxsize=400)
def w2s(pos: Vec3, matrix):
    width = 1920
    height = 1080
    clip_coords_x = pos.x * matrix[0] + pos.y * matrix[4] + pos.z * matrix[8] + matrix[12]
    clip_coords_y = pos.x * matrix[1] + pos.y * matrix[5] + pos.z * matrix[9] + matrix[13]
    clip_coords_w = pos.x * matrix[3] + pos.y * matrix[7] + pos.z * matrix[11] + matrix[15]

    if clip_coords_w < 1.:
        clip_coords_w = 1.

    M_x = clip_coords_x / clip_coords_w
    M_y = clip_coords_y / clip_coords_w

    out_x = (width / 2. * M_x) + (M_x + width / 2.)
    out_y = -(height / 2. * M_y) + (M_y + height / 2.)

    if 0 <= out_x <= width and 0 <= out_y <= height:
        return Vec2(out_x, out_y)

    return Vec2(0, 0)


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
