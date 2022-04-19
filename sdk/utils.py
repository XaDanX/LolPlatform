from dataclasses import dataclass


@dataclass
class Vec3:
    x: float
    y: float
    z: float


@dataclass
class Vec2:
    x: float
    y: float


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

    """
    z = pos.x * matrix[2] + pos.y * matrix[6] + pos.z * matrix[10] + matrix[14]
    if z < 0.1:
        return None

    x = pos.x * matrix[0] + pos.y * matrix[4] + pos.z * matrix[8] + matrix[12]
    y = pos.x * matrix[1] + pos.y * matrix[5] + pos.z * matrix[9] + matrix[13]

    xx = x / z
    yy = y / z

    _x = (1920 / 2 * xx) + (xx + 1920 / 2)  # capture screen width/height
    _y = -(1090 / 2 * yy) + (yy + 1080 / 2)

    return Vec2(_x, _y)
    """
