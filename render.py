import pygame
import pygame.gfxdraw
import math
from model import state
from transform import rotate_point, interpolate, quadratic_bezier
from config import WIDTH, HEIGHT
from modification import modification_state

_SCREEN = None
_FONT = None
_FONT_LARGE = None
_FONT_SMALL = None

def set_render_context(screen, font):
    global _SCREEN, _FONT, _FONT_LARGE, _FONT_SMALL
    _SCREEN = screen
    _FONT = font
    _FONT_LARGE = pygame.font.SysFont("arial", 28, bold=True)
    _FONT_SMALL = pygame.font.SysFont("arial", 20)

def project_point(x, y, z):
    x -= state.camera_pos[0]
    y -= state.camera_pos[1]
    z -= state.camera_pos[2]
    cos_x = math.cos(state.angle_x)
    sin_x = math.sin(state.angle_x)
    y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
    cos_y = math.cos(state.angle_y)
    sin_y = math.sin(state.angle_y)
    x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
    cos_z = math.cos(state.angle_z)
    sin_z = math.sin(state.angle_z)
    x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z
    z += state.camera_distance
    if z < 0.1:
        z = 0.1
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

def draw_panel(x, y, width, height, color=(50, 50, 50, 180)):
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    s.fill(color)
    _SCREEN.blit(s, (x, y))

def draw_poly_grid(poly_idx_list, steps=10):
    verts = [state.points[i] for i in poly_idx_list]
    n = len(verts)
    if n < 3:
        return
    for i in range(n):
        a = verts[i]
        b = verts[(i + 1) % n]
        for j in range(steps + 1):
            t = j / steps
            x, y, z = interpolate(a, b, t)
            px, py = project_point(*rotate_point(x, y, z, state.angle_x, state.angle_y))
            pygame.draw.circle(_SCREEN, (180,180,180), (px, py), 1)
    cx = sum(v[0] for v in verts) / n
    cy = sum(v[1] for v in verts) / n
    cz = sum(v[2] for v in verts) / n
    for v in verts:
        for j in range(steps + 1):
            t = j / steps
            x, y, z = interpolate((cx, cy, cz), v, t)
            px, py = project_point(*rotate_point(x, y, z, state.angle_x, state.angle_y))
            pygame.draw.circle(_SCREEN, (220,220,220), (px, py), 1)

def draw_quadratic_bezier(p0, p1, p2, color=(255, 255, 255), steps=10):
    """Оптимизированная функция рендеринга Безье с кэшированием."""
    points = []
    steps = min(steps, 10)  # Ограничиваем для производительности
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t)**2 * p0[0] + 2*(1 - t)*t * p1[0] + t**2 * p2[0]
        y = (1 - t)**2 * p0[1] + 2*(1 - t)*t * p1[1] + t**2 * p2[1]
        points.append((x, y))
    for i in range(len(points) - 1):
        pygame.draw.line(_SCREEN, color, points[i], points[i + 1], 2)

def draw_scene(screen, font):
    global _SCREEN, _FONT, _FONT_SMALL
    _SCREEN = screen
    _FONT = font
    _FONT_SMALL = pygame.font.SysFont("arial", 20)
    screen.fill((0, 0, 0))

    # Оси
    origin = project_point(0, 0, 0)
    for axis, color, vec in [
        ('X', (255, 0, 0), (1, 0, 0)),
        ('Y', (0, 255, 0), (0, 1, 0)),
        ('Z', (0, 128, 255), (0, 0, 1)),
    ]:
        for sign in (-1, 1):
            for i in range(1, 21):
                dx, dy, dz = [v * i * sign for v in vec]
                p = project_point(*rotate_point(dx, dy, dz, state.angle_x, state.angle_y))
                pygame.draw.line(_SCREEN, color, origin, p, 2 if i == 10 else 1)
                if state.show_labels:
                    draw_text(f"{i*sign}", p[0], p[1], font=_FONT_SMALL, color=color)

    if state.show_labels:
        draw_panel(5, 105, 140, 85, (50, 50, 50, 180))
        draw_text("Оси:", 10, 110, font=_FONT_LARGE, color=(255, 255, 255))
        draw_text("X: Красная", 10, 135, font=_FONT_SMALL, color=(255, 0, 0))
        draw_text("Y: Зелёная", 10, 150, font=_FONT_SMALL, color=(0, 255, 0))
        draw_text("Z: Синяя", 10, 165, font=_FONT_SMALL, color=(0, 128, 255))

    # Линии
    for p1_idx, p2_idx in state.lines:
        r1 = rotate_point(*state.points[p1_idx], state.angle_x, state.angle_y)
        r2 = rotate_point(*state.points[p2_idx], state.angle_x, state.angle_y)
        p1 = project_point(*r1)
        p2 = project_point(*r2)
        pygame.draw.line(_SCREEN, (255, 255, 255), p1, p2, 2)

    # Полигоны
    for poly in state.polygons:
        idxs = poly["indices"]
        proj = [project_point(*rotate_point(*state.points[i], state.angle_x, state.angle_y)) for i in idxs]
        if len(proj) >= 3 and poly.get("filled"):
            pygame.draw.polygon(_SCREEN, (60, 60, 100), proj)
        if poly.get("rounded"):
            steps = poly.get("round_steps", 10)
            for i in range(len(idxs)):
                p0 = state.points[idxs[i]]
                p2 = state.points[idxs[(i + 1) % len(idxs)]]
                cx = sum(state.points[j][0] for j in idxs) / len(idxs)
                cy = sum(state.points[j][1] for j in idxs) / len(idxs)
                cz = sum(state.points[j][2] for j in idxs) / len(idxs)
                mx = (p0[0] + p2[0]) / 2
                my = (p0[1] + p2[1]) / 2
                mz = (p0[2] + p2[2]) / 2
                # Сдвиг контрольной точки внутрь полигона
                dist = math.sqrt((mx - cx)**2 + (my - cy)**2 + (mz - cz)**2)
                if dist > 0:
                    factor = 0.6  # Внутреннее округление
                    p1 = (mx + (cx - mx) * factor, my + (cy - my) * factor, mz + (cz - mz) * factor)
                else:
                    p1 = (mx, my, mz)
                p0_proj = project_point(*rotate_point(*p0, state.angle_x, state.angle_y))
                p1_proj = project_point(*rotate_point(*p1, state.angle_x, state.angle_y))
                p2_proj = project_point(*rotate_point(*p2, state.angle_x, state.angle_y))
                draw_quadratic_bezier(p0_proj, p1_proj, p2_proj, color=(255, 255, 255), steps=steps)
        else:
            pygame.draw.polygon(_SCREEN, (200, 200, 255), proj, 1)
            if len(idxs) == 4 and not poly.get("filled"):
                draw_poly_grid(idxs, steps=10)

    # Кривые Безье
    for curve in state.curves:
        if len(curve) == 3:
            p0, p1, p2 = [project_point(*rotate_point(*state.points[i], state.angle_x, state.angle_y)) for i in curve]
            draw_quadratic_bezier(p0, p1, p2, state.curve_color, steps=state.curve_step * 5)

    # Точки
    for i, pt in enumerate(state.points):
        xr, yr, zr = rotate_point(*pt, state.angle_x, state.angle_y)
        xp, yp = project_point(xr, yr, zr)
        pygame.gfxdraw.filled_circle(_SCREEN, xp, yp, 5, (255, 255, 0))
        if state.show_labels:
            draw_text(str(i+1), xp + 6, yp - 8, font=_FONT_SMALL)
            draw_text(f"({pt[0]:.2f},{pt[1]:.2f},{pt[2]:.2f})", xp + 6, yp + 8, font=_FONT_SMALL)

    # HUD
    if state.show_labels:
        if modification_state.active:
            draw_panel(5, 5, 400, 120, (50, 50, 50, 180))
            draw_text("Режим: Модификация", 10, 10, font=_FONT_LARGE, color=(255, 200, 0))
            if modification_state.current_modification is None:
                draw_text("Выберите модификацию:", 10, 35, font=_FONT_SMALL)
                draw_text("1 — Округлить полигон (внутренние кривые)", 10, 55, font=_FONT_SMALL, color=(180, 180, 180))
                draw_text("2 — Снять округление", 10, 75, font=_FONT_SMALL, color=(180, 180, 180))
            elif modification_state.current_modification == "round_polygon":
                draw_text(f"[ОКРУГЛИТЬ ПОЛИГОН] Полигон: {modification_state.polygon_index} (1..{len(state.polygons)})", 10, 35, font=_FONT_SMALL)
                draw_text(f"Гладкость (1..20): {modification_state.steps}", 10, 55, font=_FONT_SMALL)
                draw_text("Введите индекс полигона и гладкость", 10, 75, font=_FONT_SMALL, color=(180, 180, 180))
            elif modification_state.current_modification == "unround_polygon":
                draw_text(f"[СНЯТЬ ОКРУГЛЕНИЕ] Полигон: {modification_state.polygon_index} (1..{len(state.polygons)})", 10, 35, font=_FONT_SMALL)
                draw_text("Введите индекс полигона", 10, 55, font=_FONT_SMALL, color=(180, 180, 180))
        else:
            mode_colors = {
                "point": (0, 200, 0),
                "line": (0, 128, 255),
                "delete": (200, 0, 0),
                "polygon": (200, 200, 0),
                "fill": (128, 0, 128),
                "curve": (255, 128, 0)
            }
            mode_color = mode_colors.get(state.input_mode, (255, 255, 255))
            draw_panel(5, 5, 400, 80, (50, 50, 50, 180))
            draw_text(f"Режим: {state.input_mode.title() if state.input_mode else 'None'}", 10, 10, font=_FONT_LARGE, color=mode_color)
            if state.input_mode == "point":
                coord = state.coord_order[state.coord_index]
                draw_text(f"[ТОЧКА] Введите {coord} (-1000..1000): {state.current_point[coord]}", 10, 35, font=_FONT_SMALL)
                draw_text(f"Пример: 3.14, -5.2", 10, 55, font=_FONT_SMALL, color=(180, 180, 180))
            elif state.input_mode == "line":
                draw_text(f"[ЛИНИЯ] p1={state.current_line['p1']}, p2={state.current_line['p2']} (1..{len(state.points)})", 10, 35, font=_FONT_SMALL)
                draw_text(f"Введите индексы точек", 10, 55, font=_FONT_SMALL, color=(180, 180, 180))
            elif state.input_mode == "delete":
                idx = state.current_delete + 1 if state.current_delete is not None else ''
                draw_text(f"[УДАЛЕНИЕ] Точка: {idx} (1..{len(state.points)})", 10, 35, font=_FONT_SMALL)
                draw_text(f"Введите индекс точки", 10, 55, font=_FONT_SMALL, color=(180, 180, 180))
            elif state.input_mode == "polygon":
                poly_str = ",".join(str(i+1) for i in state.current_polygon) if state.current_polygon else ""
                draw_text(f"[ПОЛИГОН] Точки: {poly_str} Текущая: {state.point_index_input} (1..{len(state.points)})", 10, 35, font=_FONT_SMALL)
                draw_text(f"Введите индексы точек", 10, 55, font=_FONT_SMALL, color=(180, 180, 180))
            elif state.input_mode == "fill":
                draw_text(f"[ЗАЛИВКА] Полигон: {state.current_fill} (1..{len(state.polygons)})", 10, 35, font=_FONT_SMALL)
                draw_text(f"Введите индекс полигона", 10, 55, font=_FONT_SMALL, color=(180, 180, 180))
            elif state.input_mode == "curve":
                curve_str = ",".join(str(i+1) for i in state.current_curve) if state.current_curve else ""
                draw_text(f"[КРИВАЯ] Точки: {curve_str} Текущая: {state.point_index_input} (1..{len(state.points)})", 10, 35, font=_FONT_SMALL)
                draw_text(f"Введите индексы точек", 10, 55, font=_FONT_SMALL, color=(180, 180, 180))

        draw_panel(5, HEIGHT - 100, 450, 90, (50, 50, 50, 180))
        draw_text("Управление:", 10, HEIGHT - 95, font=_FONT_LARGE, color=(255, 255, 255))
        draw_text("Enter: Подтвердить | Backspace: Удалить | Space: Добавить", 10, HEIGHT - 65, font=_FONT_SMALL, color=(200, 200, 200))
        draw_text("T: Точка | L: Линия | D: Удаление | P: Полигон | F: Заливка | C: Кривая", 10, HEIGHT - 45, font=_FONT_SMALL, color=(200, 200, 200))
        draw_text("F1: Метки | R: Сброс камеры | Tab: Модификации | Стрелки/Мышь: Вращение", 10, HEIGHT - 25, font=_FONT_SMALL, color=(200, 200, 200))

        x0 = WIDTH - 300
        y0 = 10
        list_height = 30 + max(len(state.points) * 22 + 30 + len(state.polygons) * 22 + 30 + len(state.curves) * 22, 120)
        draw_panel(x0 - 10, y0, 290, list_height, (50, 50, 50, 180))
        draw_text("Точки:", x0, y0, font=_FONT_LARGE, color=(255, 255, 100))
        for i, pt in enumerate(state.points):
            line = f"{i+1}. ({pt[0]:.2f}, {pt[1]:.2f}, {pt[2]:.2f})"
            draw_text(line, x0, y0 + 30 + i * 22, font=_FONT_SMALL, color=(200, 200, 200))
        y1 = y0 + 30 + len(state.points) * 22 + 30
        draw_text("Полигоны:", x0, y1, font=_FONT_LARGE, color=(255, 255, 100))
        for i, poly in enumerate(state.polygons):
            inds = ",".join(str(j+1) for j in poly["indices"])
            filled = "Да" if poly.get("filled") else "Нет"
            rounded = "Округлён" if poly.get("rounded") else ""
            draw_text(f"{i+1}. ({inds}) Заливка: {filled} {rounded}", x0, y1 + 30 + i * 22, font=_FONT_SMALL, color=(200, 200, 200))
        y2 = y1 + 30 + len(state.polygons) * 22 + 30
        draw_text("Кривые:", x0, y2, font=_FONT_LARGE, color=(255, 255, 100))
        for i, curve in enumerate(state.curves):
            inds = ",".join(str(j+1) for j in curve)
            draw_text(f"{i+1}. ({inds})", x0, y2 + 30 + i * 22, font=_FONT_SMALL, color=(200, 200, 200))

    pygame.display.flip()