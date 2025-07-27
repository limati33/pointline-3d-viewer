from math import cos, sin
from model import camera_pos, d
from config import WIDTH, HEIGHT

def rotate_point(x, y, z, ax, ay):
    y2 = y * cos(ax) - z * sin(ax)
    z2 = y * sin(ax) + z * cos(ax)
    x2 = x * cos(ay) + z2 * sin(ay)
    z3 = -x * sin(ay) + z2 * cos(ay)
    return x2, y2, z3

def project_3d_to_2d(x, y, z):
    x -= camera_pos[0]
    y -= camera_pos[1]
    z -= camera_pos[2]
    factor = d / (d + z) if (d + z) != 0 else 1
    factor = min(max(factor, -10), 10)
    x2d = x * factor * WIDTH / 4 + WIDTH / 2
    y2d = -y * factor * HEIGHT / 4 + HEIGHT / 2
    x2d = max(min(x2d, 32767), -32768)
    y2d = max(min(y2d, 32767), -32768)
    return x2d, y2d

def interpolate(a, b, t):
    return (
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t,
        a[2] + (b[2] - a[2]) * t
    )

def quadratic_bezier(t, p0, p1, p2):
    """Вычисление точки на квадратичной Безье в 3D."""
    u = 1 - t
    u2 = u * u
    t2 = t * t
    x = u2 * p0[0] + 2 * u * t * p1[0] + t2 * p2[0]
    y = u2 * p0[1] + 2 * u * t * p1[1] + t2 * p2[1]
    z = u2 * p0[2] + 2 * u * t * p1[2] + t2 * p2[2]
    return x, y, z
