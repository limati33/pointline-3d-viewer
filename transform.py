import math
from config import WIDTH, HEIGHT
from model import state  # импортируем объект состояния

def rotate_point(x, y, z, angle_x, angle_y):
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)

    # Вращение вокруг оси X
    y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x

    # Вращение вокруг оси Y
    x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y

    return x, y, z

def project_point(x, y, z):
    # Отнимаем позицию камеры из координат точки
    x -= state.camera_pos[0]
    y -= state.camera_pos[1]
    z -= state.camera_pos[2]

    if state.d + z == 0:
        z += 0.01

    factor = state.d / (state.d + z)
    factor = max(min(factor, 10), -10)

    x2d = x * factor * WIDTH / 4 + WIDTH / 2
    y2d = -y * factor * HEIGHT / 4 + HEIGHT / 2

    return int(x2d), int(y2d)

def interpolate(p1, p2, t):
    return [p1[i] * (1 - t) + p2[i] * t for i in range(3)]

def quadratic_bezier(p0, p1, p2, t):
    a = interpolate(p0, p1, t)
    b = interpolate(p1, p2, t)
    return interpolate(a, b, t)
