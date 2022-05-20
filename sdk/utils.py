import math
import struct
import time
from dataclasses import dataclass
from functools import lru_cache
import functools

from utils.logger import Logger
from timeit import default_timer as timer


def int_from_buffer(data, offset):
    return int.from_bytes(data[offset:offset + 4], 'little')


def float_from_buffer(data, offset):
    f, = struct.unpack('f', data[offset:offset + 4])
    return f


def double_from_buffer(data, offset):
    d, = struct.unpack('d', data[offset:offset + 8])
    return d


def bool_from_buffer(data, offset):
    return data[offset:offset + 1] != b'\x00'


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

    def scale(self, s):
        return Vec3(self.x * s, self.y * s, self.z * s)

    def distance(self, o):
        return math.sqrt(pow(self.x - o.x, 2) + pow(self.y - o.y, 2) + pow(self.z - o.z, 2))

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalize(self):
        l = self.length()
        self.x = self.x / l
        self.y = self.y / l
        self.z = self.z / l
        return self

    def add(self, v):
        return Vec3(self.x + v.x, self.y + v.y, self.z + v.z)

    def add_d(self, v):
        return Vec3(self.x + v, self.y + v, self.z + v)

    def sub(self, v):
        return Vec3(self.x - v.x, self.y - v.y, self.z - v.z)


@dataclass
class Vec2:
    x: float
    y: float


# @ignore_unhashable
# @lru_cache(maxsize=400)

@ignore_unhashable
@lru_cache(maxsize=300)
def w2s(pos: Vec3, matrix):
    width = 1920
    height = 1080
    clip_coords_x = pos.x * matrix[0] + pos.y * matrix[4] + pos.z * matrix[8] + matrix[12]
    clip_coords_y = pos.x * matrix[1] + pos.y * matrix[5] + pos.z * matrix[9] + matrix[13]
    clip_coords_w = pos.x * matrix[3] + pos.y * matrix[7] + pos.z * matrix[11] + matrix[15]

    if clip_coords_w < 0.1:
        return None

    M_x = clip_coords_x / clip_coords_w
    M_y = clip_coords_y / clip_coords_w

    out_x = (width / 2 * M_x) + (M_x + width / 2)
    out_y = -(height / 2 * M_y) + (M_y + height / 2)

    return Vec2(out_x, out_y)


@ignore_unhashable
@lru_cache(maxsize=300)
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


@ignore_unhashable
@lru_cache(maxsize=3000)
def calculate_circle(world_pos: Vec3, view_proj_matrix, radius, points=100):
    lines = []
    step = math.pi * 2 / points
    theta = 0

    while theta <= math.pi * 2:
        world_space = Vec3(world_pos.x + radius * math.cos(theta), world_pos.y,
                           world_pos.z + radius * math.sin(theta))
        screen_space = w2s(world_space, view_proj_matrix)

        if screen_space:
            lines.append(Vec2(screen_space.x, screen_space.y))

        theta += step

    if len(lines) > 10:
        return lines
    else:
        return None


class Timer:
    timeStamp = 0

    def timer(self):
        _time = max(0, self.timeStamp - time.time())
        if 0 == _time:
            return 1
        return 0

    def set_timer(self, t):
        self.timeStamp = time.time() + t
