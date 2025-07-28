import pygame
import pygame.gfxdraw
import math
from model import state
from transform import rotate_point, interpolate, quadratic_bezier
from config import WIDTH, HEIGHT

_SCREEN = None
_FONT = None
_FONT_LARGE = None
_FONT_SMALL = None

def set_render_context(screen, font):
    global _SCREEN, _FONT, _FONT_LARGE, _FONT_SMALL
    _SCREEN = screen
    _FONT = font
    _FONT_LARGE = pygame.font.SysFont("arial", 24, bold=True)
    _FONT_SMALL = pygame.font.SysFont("arial", 16)

def project_point(x, y, z):
    # Смещение по позиции камеры
    x -= state.camera_pos[0]
    y -= state.camera_pos[1]
    z -= state.camera_pos[2]

    # Вращение вокруг X
    cos_x = math.cos(state.angle_x)
    sin_x = math.sin(state.angle_x)
    y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x

    # Вращение вокруг Y
    cos_y = math.cos(state.angle_y)
    sin_y = math.sin(state.angle_y)
    x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y

    # Проекция
    if z == 0:
        z = 0.0001
    f = state.d / z
    xp = int(_SCREEN.get_width() / 2 + x * f * 100)
    yp = int(_SCREEN.get_height() / 2 - y * f * 100)
    xp = max(-32768, min(32767, xp))
    yp = max(-32768, min(32767, yp))
    return xp, yp

def draw_text(text, x, y, font=None, color=(255,255,255)):
    if font is None:
        font = _FONT
    surf = font.render(text, True, color)
    _SCREEN.blit(surf, (x, y))

def draw_panel(x, y, width, height, color=(50, 50, 50, 128)):
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    s.fill(color)
    _SCREEN.blit(s, (x, y))

def draw_poly_grid(poly_idx_list, steps=10):
    verts = [state.points[i] for i in poly_idx_list]
    n = len(verts)
    if n < 3:
        return

    # Идём по каждой грани полигона
    for i in range(n):
        a = verts[i]
        b = verts[(i + 1) % n]
        for j in range(steps + 1):
            t = j / steps
            x, y, z = interpolate(a, b, t)
            px, py = project_point(*rotate_point(x, y, z, state.angle_x, state.angle_y))
            pygame.draw.circle(_SCREEN, (180,180,180), (px, py), 1)

    # От центра к каждой точке (радиальные лучи)
    cx = sum(v[0] for v in verts) / n
    cy = sum(v[1] for v in verts) / n
    cz = sum(v[2] for v in verts) / n
    for v in verts:
        for j in range(steps + 1):
            t = j / steps
            x, y, z = interpolate((cx, cy, cz), v, t)
            px, py = project_point(*rotate_point(x, y, z, state.angle_x, state.angle_y))
            pygame.draw.circle(_SCREEN, (220,220,220), (px, py), 1)

def draw_quadratic_bezier(p0, p1, p2, color=(255, 128, 0), steps=30):
    for i in range(steps):
        t1 = i / steps
        t2 = (i + 1) / steps
        x1 = (1 - t1)**2 * p0[0] + 2*(1 - t1)*t1 * p1[0] + t1**2 * p2[0]
        y1 = (1 - t1)**2 * p0[1] + 2*(1 - t1)*t1 * p1[1] + t1**2 * p2[1]
        x2 = (1 - t2)**2 * p0[0] + 2*(1 - t2)*t2 * p1[0] + t2**2 * p2[0]
        y2 = (1 - t2)**2 * p0[1] + 2*(1 - t2)*t2 * p1[1] + t2**2 * p2[1]
        pygame.draw.line(_SCREEN, color, (x1, y1), (x2, y2), 2)

def draw_scene(screen, font):
    global _SCREEN, _FONT, _FONT_SMALL
    _SCREEN = screen
    _FONT = font
    _FONT_SMALL = pygame.font.SysFont("arial", 12)

    screen.fill((0, 0, 0))

    # Оси с делениями и метками
    origin = project_point(0, 0, 0)
    for axis, color, vec in [
        ('X', (255, 0, 0), (1, 0, 0)),
        ('Y', (0, 255, 0), (0, 1, 0)),
        ('Z', (0, 128, 255), (0, 0, 1)),
    ]:
        # линии осей
        for sign in (-1, 1):
            for i in range(1, 21):
                dx, dy, dz = [v * i * sign for v in vec]
                p = project_point(*rotate_point(dx, dy, dz, state.angle_x, state.angle_y))
                pygame.draw.line(_SCREEN, color, origin, p, 2 if i == 10 else 1)
                if state.show_labels:
                    draw_text(f"{i*sign}", p[0], p[1], font=_FONT_SMALL, color=color)
    # Названия осей
    if state.show_labels:
        draw_panel(5, 55, 120, 75, (50, 50, 50, 128))
        draw_text("Оси:", 10, 60, font=_FONT_LARGE, color=(255, 255, 255))
        draw_text("X: Красная", 10, 85, font=_FONT_SMALL, color=(255, 0, 0))
        draw_text("Y: Зелёная", 10, 100, font=_FONT_SMALL, color=(0, 255, 0))
        draw_text("Z: Синяя", 10, 115, font=_FONT_SMALL, color=(0, 128, 255))

    # Линии
    for p1_idx, p2_idx in state.lines:
        r1 = rotate_point(*state.points[p1_idx], state.angle_x, state.angle_y)
        r2 = rotate_point(*state.points[p2_idx], state.angle_x, state.angle_y)
        p1 = project_point(*r1)
        p2 = project_point(*r2)
        pygame.draw.line(_SCREEN, (255, 255, 255), p1, p2, 2)

    # Полигоны (+ сетка для четырёхугольников)
    for poly in state.polygons:
        idxs = poly["indices"]
        proj = [project_point(*rotate_point(*state.points[i], state.angle_x, state.angle_y)) for i in idxs]
        if len(proj) >= 3 and poly.get("filled"):
            pygame.draw.polygon(_SCREEN, (60, 60, 100), proj)
        else:
            # если не заполнен и четырёхугольник — рисуем сетку
            if len(idxs) == 4 and not poly.get("filled"):
                draw_poly_grid(idxs, steps=10)
        pygame.draw.polygon(_SCREEN, (200, 200, 255), proj, 1)

    # Кривые Безье
    for curve in state.curves:
        if len(curve) == 3:
            p0, p1, p2 = [project_point(*rotate_point(*state.points[i], state.angle_x, state.angle_y)) for i in curve]
            draw_quadratic_bezier(p0, p1, p2, state.curve_color, steps=state.curve_step * 10)

    # Точки (с сглаженным кругом)
    for i, pt in enumerate(state.points):
        xr, yr, zr = rotate_point(*pt, state.angle_x, state.angle_y)
        xp, yp = project_point(xr, yr, zr)
        pygame.gfxdraw.filled_circle(_SCREEN, xp, yp, 5, (255, 255, 0))
        if state.show_labels:
            draw_text(str(i+1), xp + 6, yp - 8, font=_FONT_SMALL)
            draw_text(f"({pt[0]:.2f},{pt[1]:.2f},{pt[2]:.2f})", xp + 6, yp + 8, font=_FONT_SMALL)

    # HUD: режим, параметры ввода, списки
    if state.show_labels:
        # Цвета для режимов
        mode_colors = {
            "point": (0, 200, 0),
            "line": (0, 128, 255),
            "delete": (200, 0, 0),
            "polygon": (200, 200, 0),
            "fill": (128, 0, 128),
            "curve": (255, 128, 0)
        }
        mode_color = mode_colors.get(state.input_mode, (255, 255, 255))

        # Панель статуса ввода
        draw_panel(5, 5, 400, 50, (50, 50, 50, 128))
        draw_text(f"Режим: {state.input_mode.title()}", 10, 10, font=_FONT_LARGE, color=mode_color)
        if state.input_mode == "point":
            coord = state.coord_order[state.coord_index]
            draw_text(f"[ТОЧКА] Введите {coord}: {state.current_point[coord]}", 10, 35, font=_FONT_SMALL)
        elif state.input_mode == "line":
            draw_text(f"[ЛИНИЯ] p1={state.current_line['p1']}, p2={state.current_line['p2']}", 10, 35, font=_FONT_SMALL)
        elif state.input_mode == "delete":
            idx = state.current_delete + 1 if state.current_delete is not None else ''
            draw_text(f"[УДАЛЕНИЕ] Точка: {idx}", 10, 35, font=_FONT_SMALL)
        elif state.input_mode == "polygon":
            poly_str = ",".join(str(i+1) for i in state.current_polygon) if state.current_polygon else ""
            draw_text(f"[ПОЛИГОН] Точки: {poly_str} Текущая: {state.point_index_input}", 10, 35, font=_FONT_SMALL)
        elif state.input_mode == "fill":
            draw_text(f"[ЗАЛИВКА] Полигон: {state.current_fill}", 10, 35, font=_FONT_SMALL)
        elif state.input_mode == "curve":
            curve_str = ",".join(str(i+1) for i in state.current_curve) if state.current_curve else ""
            draw_text(f"[КРИВАЯ] Точки: {curve_str} Текущая: {state.point_index_input}", 10, 35, font=_FONT_SMALL)

        # Панель управления
        draw_panel(5, HEIGHT - 80, 400, 75, (50, 50, 50, 128))
        draw_text("Управление:", 10, HEIGHT - 75, font=_FONT_LARGE, color=(255, 255, 255))
        draw_text("Enter: Подтвердить, Backspace: Удалить, Space: Добавить", 10, HEIGHT - 50, font=_FONT_SMALL)
        draw_text("L: Линия, D: Удаление, P: Полигон, F: Заливка, C: Кривая, F1: Метки", 10, HEIGHT - 35, font=_FONT_SMALL)
        draw_text("Стрелки/Мышь: Вращение, Колесо/+/-: Масштаб, [: Сохранить, ]: Загрузить", 10, HEIGHT - 20, font=_FONT_SMALL)

        # Списки справа: точки, полигоны, кривые
        x0 = WIDTH - 260
        y0 = 10
        list_height = 20 + max(len(state.points) * 18 + 20 + len(state.polygons) * 18 + 20 + len(state.curves) * 18, 100)
        draw_panel(x0 - 10, y0, 250, list_height, (50, 50, 50, 128))
        # Точки
        draw_text("Точки:", x0, y0, font=_FONT_LARGE, color=(200, 200, 50))
        for i, pt in enumerate(state.points):
            line = f"{i+1}. {pt[0]:.2f}/{pt[1]:.2f}/{pt[2]:.2f}"
            draw_text(line, x0, y0 + 25 + i * 18, font=_FONT_SMALL, color=(180, 180, 180))
        # Полигоны
        y1 = y0 + 25 + len(state.points) * 18 + 20
        draw_text("Полигоны:", x0, y1, font=_FONT_LARGE, color=(200, 200, 50))
        for i, poly in enumerate(state.polygons):
            inds = ",".join(str(j+1) for j in poly["indices"])
            filled = "Да" if poly.get("filled") else "Нет"
            draw_text(f"{i+1}. ({inds}) Заливка: {filled}", x0, y1 + 25 + i * 18, font=_FONT_SMALL, color=(180, 180, 180))
        # Кривые
        y2 = y1 + 25 + len(state.polygons) * 18 + 20
        draw_text("Кривые:", x0, y2, font=_FONT_LARGE, color=(200, 200, 50))
        for i, curve in enumerate(state.curves):
            inds = ",".join(str(j+1) for j in curve)
            draw_text(f"{i+1}. ({inds})", x0, y2 + 25 + i * 18, font=_FONT_SMALL, color=(180, 180, 180))

    pygame.display.flip()