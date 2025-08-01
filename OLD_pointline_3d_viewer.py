import asyncio
import platform
import pygame
import pygame.gfxdraw
import json
import os
from math import cos, sin
import tkinter as tk
from tkinter import filedialog

def interpolate(a, b, t):
    return (a[0] + (b[0]-a[0])*t,
            a[1] + (b[1]-a[1])*t,
            a[2] + (b[2]-a[2])*t)

def draw_poly_grid(poly_idx_list, steps=10):
    verts = [points[i] for i in poly_idx_list]
    A, B, C, D = verts
    for i in range(steps+1):
        t = i/steps
        p_start = rotate_point(*interpolate(A, B, t), angle_x, angle_y)
        p_end = rotate_point(*interpolate(D, C, t), angle_x, angle_y)
        x1, y1 = project_3d_to_2d(*p_start)
        x2, y2 = project_3d_to_2d(*p_end)
        pygame.draw.line(screen, (200,200,200), (x1, y1), (x2, y2), 1)
    for i in range(steps+1):
        t = i/steps
        p_start = rotate_point(*interpolate(A, D, t), angle_x, angle_y)
        p_end = rotate_point(*interpolate(B, C, t), angle_x, angle_y)
        x1, y1 = project_3d_to_2d(*p_start)
        x2, y2 = project_3d_to_2d(*p_end)
        pygame.draw.line(screen, (200,200,200), (x1, y1), (x2, y2), 1)

# Инициализация Pygame
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Projection with Rotation")
FPS = 60
font = pygame.font.SysFont("arial", 20)

# Параметры проекции и вращения
d = 4.0              # "расстояние" до экрана / коэффициент масштабирования
angle_x = 0.0        # угол вращения вокруг X (в радианах)
angle_y = 0.0        # угол вращения вокруг Y
rotation_speed = 0.05
mouse_sensitivity = 0.005  # чувствительность мыши для вращения

points = []  # список 3D-точек
lines = []   # список соединений (pairs of point indices)
polygons = []  # список полигонов: [{"indices": [0,1,2,3], "filled": False}, ...]
curves = []

# Режим ввода: 'point', 'line', 'delete', 'polygon', 'fill'
input_mode = "point"
current_point = {"x": "", "y": "", "z": ""}
coord_order = ["x", "y", "z"]
coord_index = 0

current_line = {"p1": "", "p2": ""}
line_step = 1

current_delete = None  # индекс точки для удаления

current_polygon = []  # список индексов для текущего полигона
polygon_step = 1

current_fill = ""  # строка для ввода индекса полигона в режиме fill
point_index_input = ""  # строка для ввода индекса точки в режиме polygon

current_curve = []
curve_step = 0
curve_input = ""               # буфер ввода для curve
curve_color = (255,128,0)

# Переменные для управления мышью
mouse_dragging = False
last_mouse_pos = None
camera_pos = [0.0, 0.0, -5.0]  # камера чуть "позади"
right_mouse_dragging = False

show_labels = True  # флаг для отображения текстовых меток

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

def draw_text(text, x, y, color=(255,255,255)):
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))

def handle_input():
    global input_mode, current_point, coord_index
    global current_line, line_step, angle_x, angle_y, d
    global mouse_dragging, last_mouse_pos, current_delete
    global right_mouse_dragging, camera_pos, show_labels
    global current_polygon, polygon_step, current_fill, point_index_input
    global curve_input, curve_step, current_curve

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                show_labels = not show_labels
                continue

            if input_mode == "point":
                coord = coord_order[coord_index]
                if event.key == pygame.K_RETURN:
                    if current_point[coord] != "":
                        coord_index += 1
                        if coord_index >= 3:
                            try:
                                x = float(current_point['x'])
                                y = float(current_point['y'])
                                z = float(current_point['z'])
                                if abs(x) > 1000 or abs(y) > 1000 or abs(z) > 1000:
                                    raise ValueError("Coordinates must be between -1000 and 1000")
                                points.append((x, y, z))
                            except ValueError as e:
                                print(f"Error: {e}")
                            current_point = {"x": "", "y": "", "z": ""}
                            coord_index = 0
                elif event.key == pygame.K_BACKSPACE:
                    current_point[coord] = current_point[coord][:-1]
                elif event.key == pygame.K_l:
                    input_mode = "line"
                    current_line = {"p1": "", "p2": ""}
                    line_step = 1
                elif event.key == pygame.K_d:
                    input_mode = "delete"
                    current_delete = None
                elif event.key == pygame.K_p:
                    input_mode = "polygon"
                    current_polygon = []
                    polygon_step = 1
                    point_index_input = ""
                elif event.key == pygame.K_f:
                    input_mode = "fill"
                    current_fill = ""
                elif event.key == pygame.K_c:
                    input_mode = "curve"
                    current_curve = {"p0": "", "p1": "", "p2": ""}  # словарь, а не список
                    curve_step = 1
                    curve_input = ""  # сброс буфера
                else:
                    if event.unicode.isdigit() or event.unicode in '.-':
                        current_point[coord] += event.unicode

            elif input_mode == "line":
                if event.key == pygame.K_RETURN:
                    if line_step == 1 and current_line['p1'].isdigit():
                        line_step = 2
                    elif line_step == 2 and current_line['p2'].isdigit():
                        p1 = int(current_line['p1']) - 1
                        p2 = int(current_line['p2']) - 1
                        if 0 <= p1 < len(points) and 0 <= p2 < len(points):
                            new_line = (p1, p2)
                            rev = (p2, p1)
                            if new_line in lines:
                                lines.remove(new_line)
                            elif rev in lines:
                                lines.remove(rev)
                            else:
                                lines.append(new_line)
                        current_line = {"p1": "", "p2": ""}
                        line_step = 1
                elif event.key == pygame.K_BACKSPACE:
                    if line_step == 1 and current_line['p1']:
                        current_line['p1'] = current_line['p1'][:-1]
                    elif line_step == 2 and current_line['p2']:
                        current_line['p2'] = current_line['p2'][:-1]
                    elif line_step == 2:
                        line_step = 1
                        current_line['p2'] = ""
                elif event.key == pygame.K_l:
                    input_mode = "point"
                    current_line = {"p1": "", "p2": ""}
                    line_step = 1
                elif event.key == pygame.K_d:
                    input_mode = "delete"
                    current_delete = None
                elif event.key == pygame.K_p:
                    input_mode = "polygon"
                    current_polygon = []
                    polygon_step = 1
                    point_index_input = ""
                elif event.key == pygame.K_f:
                    input_mode = "fill"
                    current_fill = ""
                else:
                    if event.unicode.isdigit():
                        if line_step == 1:
                            current_line['p1'] += event.unicode
                        elif line_step == 2:
                            current_line['p2'] += event.unicode

            elif input_mode == "delete":
                if event.key == pygame.K_RETURN:
                    if current_delete is not None:
                        idx = current_delete
                        if 0 <= idx < len(points):
                            points.pop(idx)
                            lines[:] = [(p1, p2) for p1, p2 in lines if p1 != idx and p2 != idx]
                            lines[:] = [(p1 - (1 if p1 > idx else 0), p2 - (1 if p2 > idx else 0)) for p1, p2 in lines]
                            polygons[:] = [{"indices": [i - (1 if i > idx else 0) for i in poly["indices"]], "filled": poly["filled"]} for poly in polygons if idx not in poly["indices"]]
                            curves[:] = [[i - (1 if i > idx else 0) for i in curve] for curve in curves if idx not in curve]
                        current_delete = None
                elif event.key == pygame.K_BACKSPACE:
                    current_delete = None
                elif event.key == pygame.K_l:
                    input_mode = "line"
                    current_line = {"p1": "", "p2": ""}
                    line_step = 1
                elif event.key == pygame.K_d:
                    input_mode = "point"
                    current_delete = None
                elif event.key == pygame.K_p:
                    input_mode = "polygon"
                    current_polygon = []
                    polygon_step = 1
                    point_index_input = ""
                elif event.key == pygame.K_f:
                    input_mode = "fill"
                    current_fill = ""
                else:
                    if event.unicode.isdigit():
                        idx = int(event.unicode) - 1
                        if 0 <= idx < len(points):
                            current_delete = idx

            elif input_mode == "polygon":
                if event.key == pygame.K_RETURN:
                    # Если в буфере ввода есть число — добавим его в текущий полигон
                    if point_index_input.strip():
                        if point_index_input.strip().isdigit():
                            idx = int(point_index_input.strip()) - 1  # -1 для индексации с 0
                            if 0 <= idx < len(points):
                                current_polygon.append(idx)
                        point_index_input = ""

                    # Если полигон достаточно большой — добавляем или удаляем
                    if len(current_polygon) >= 3:
                        new_poly = {"indices": current_polygon.copy(), "filled": False}
                        if tuple(current_polygon) in [tuple(p["indices"]) for p in polygons]:
                            polygons[:] = [p for p in polygons if tuple(p["indices"]) != tuple(current_polygon)]
                        else:
                            polygons.append(new_poly)
                        current_polygon = []
                        polygon_step = 1
                    elif current_polygon:
                        polygon_step += 1

                    point_index_input = ""

                elif event.key == pygame.K_BACKSPACE:
                    # Если в буфере есть что-то — удаляем последний символ
                    if point_index_input:
                        point_index_input = point_index_input[:-1]
                    # Иначе — удаляем последний индекс из полигона (откат)
                    elif current_polygon:
                        current_polygon.pop()
                        polygon_step = max(1, polygon_step - 1)
                    else:
                        input_mode = "point"
                        polygon_step = 1
                        point_index_input = ""

                # При пробеле или запятой — добавляем число в полигон и сбрасываем буфер
                elif event.key == pygame.K_SPACE or event.unicode == ',':
                    if point_index_input.strip().isdigit():
                        idx = int(point_index_input.strip()) - 1  # -1 для индексации с 0
                        if 0 <= idx < len(points):
                            current_polygon.append(idx)
                            polygon_step += 1
                    point_index_input = ""

                elif event.key == pygame.K_l:
                    input_mode = "line"
                    current_line = {"p1": "", "p2": ""}
                    line_step = 1
                    point_index_input = ""

                elif event.key == pygame.K_d:
                    input_mode = "delete"
                    current_delete = None
                    point_index_input = ""

                elif event.key == pygame.K_p:
                    input_mode = "point"
                    current_polygon = []
                    polygon_step = 1
                    point_index_input = ""

                elif event.key == pygame.K_f:
                    input_mode = "fill"
                    current_fill = ""
                    point_index_input = ""

                else:
                    # Накопление цифр в буфере ввода
                    if event.unicode.isdigit():
                        point_index_input += event.unicode

            elif input_mode == "fill":
                if event.key == pygame.K_RETURN:
                    if current_fill.isdigit():
                        idx = int(current_fill) - 1
                        if 0 <= idx < len(polygons):
                            polygons[idx]["filled"] = not polygons[idx]["filled"]
                    current_fill = ""
                elif event.key == pygame.K_BACKSPACE:
                    current_fill = current_fill[:-1]
                elif event.key == pygame.K_l:
                    input_mode = "line"
                    current_line = {"p1": "", "p2": ""}
                    line_step = 1
                elif event.key == pygame.K_d:
                    input_mode = "delete"
                    current_delete = None
                elif event.key == pygame.K_p:
                    input_mode = "polygon"
                    current_polygon = []
                    polygon_step = 1
                    point_index_input = ""
                elif event.key == pygame.K_f:
                    input_mode = "point"
                    current_fill = ""
                else:
                    if event.unicode.isdigit():
                        current_fill += event.unicode

            elif input_mode == "curve":
                if event.key == pygame.K_RETURN:
                    if point_index_input.strip().isdigit():
                        idx = int(point_index_input.strip()) - 1
                        if 0 <= idx < len(points):
                            current_curve.append(idx)
                    point_index_input = ""
                    if len(current_curve) == 3:
                        new_curve = current_curve.copy()
                        if new_curve in curves:
                            curves.remove(new_curve)
                        else:
                            curves.append(new_curve)
                        current_curve = []
                        curve_step = 1
                    elif current_curve:
                        curve_step = min(curve_step + 1, 3)
                elif event.key == pygame.K_BACKSPACE:
                    if point_index_input:
                        point_index_input = point_index_input[:-1]
                    elif current_curve:
                        current_curve.pop()
                        curve_step = max(1, curve_step - 1)
                    else:
                        input_mode = "point"
                        curve_step = 1
                        point_index_input = ""
                elif event.key == pygame.K_SPACE or event.unicode == ',':
                    if point_index_input.strip().isdigit():
                        idx = int(point_index_input.strip()) - 1
                        if 0 <= idx < len(points):
                            current_curve.append(idx)
                            curve_step = min(curve_step + 1, 3)
                    point_index_input = ""
                elif event.key == pygame.K_l:
                    input_mode = "line"
                    current_line = {"p1": "", "p2": ""}
                    line_step = 1
                    point_index_input = ""
                elif event.key == pygame.K_d:
                    input_mode = "delete"
                    current_delete = None
                    point_index_input = ""
                elif event.key == pygame.K_p:
                    input_mode = "polygon"
                    current_polygon = []
                    polygon_step = 1
                    point_index_input = ""
                elif event.key == pygame.K_f:
                    input_mode = "fill"
                    current_fill = ""
                    point_index_input = ""
                elif event.key == pygame.K_c:
                    input_mode = "point"
                    current_curve = []
                    curve_step = 1
                    point_index_input = ""
                else:
                    if event.unicode.isdigit():
                        point_index_input += event.unicode

            if event.key == pygame.K_LEFTBRACKET:
                save_to_json()
            elif event.key == pygame.K_RIGHTBRACKET:
                load_from_json()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_dragging = True
                last_mouse_pos = event.pos
            elif event.button == 3:
                right_mouse_dragging = True
                last_mouse_pos = event.pos
            elif event.button == 4:
                d = min(d + 0.5, 10)
            elif event.button == 5:
                d = max(d - 0.5, 1)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_dragging = False
                last_mouse_pos = None
            elif event.button == 3:
                right_mouse_dragging = False
                last_mouse_pos = None

        elif event.type == pygame.MOUSEMOTION:
            if mouse_dragging and last_mouse_pos:
                dx, dy = event.pos[0] - last_mouse_pos[0], event.pos[1] - last_mouse_pos[1]
                angle_y += dx * mouse_sensitivity
                angle_x -= dy * mouse_sensitivity
                last_mouse_pos = event.pos
            elif right_mouse_dragging and last_mouse_pos:
                dx, dy = event.pos[0] - last_mouse_pos[0], event.pos[1] - last_mouse_pos[1]
                camera_pos[0] -= dx * 0.01
                camera_pos[1] += dy * 0.01
                last_mouse_pos = event.pos

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        camera_pos[2] += 0.2
    if keys[pygame.K_s]:
        camera_pos[2] -= 0.2
    if keys[pygame.K_EQUALS] or keys[pygame.K_KP_PLUS]:
        d = min(d + 0.1, 10)
    if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS]:
        d = max(d - 0.1, 1)
    if keys[pygame.K_LEFT]:
        angle_y -= rotation_speed
    if keys[pygame.K_RIGHT]:
        angle_y += rotation_speed
    if keys[pygame.K_UP]:
        angle_x -= rotation_speed
    if keys[pygame.K_DOWN]:
        angle_x += rotation_speed

def save_to_json():
    try:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save as"
        )
        if not file_path:
            return
        data = {
            "points": points,
            "lines": lines,
            "polygons": polygons,   # каждый полигон — {"indices": [...], "filled": True/False}
            "curves": curves        # каждый curve — {"p0": int, "p1": int, "p2": int}
        }
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[✔] Saved to {file_path}")
    except Exception as e:
        print(f"[✖] Failed to save: {e}")

def load_from_json():
    global points, lines, polygons, curves
    try:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Open file"
        )
        if not file_path:
            return
        with open(file_path, "r") as f:
            data = json.load(f)

        # Точки и линии
        points[:] = [tuple(p) for p in data.get("points", [])]
        lines[:] = [tuple(l)   for l in data.get("lines",  [])]

        # Полигоны: индексы + состояние filled
        polygons[:] = [
            {
                "indices": list(poly.get("indices", [])),
                "filled": bool(poly.get("filled", False))
            }
            for poly in data.get("polygons", [])
        ]

        # Кривые: только валидные (три целых индекса в диапазоне)
        raw_curves = data.get("curves", [])
        curves[:] = []
        for c in raw_curves:
            if all(isinstance(c.get(k), int) and 0 <= c[k] < len(points)
                   for k in ("p0", "p1", "p2")):
                curves.append({"p0": c["p0"], "p1": c["p1"], "p2": c["p2"]})
            else:
                print(f"[!] Skipped invalid curve: {c}")

        print(f"[✔] Loaded from {file_path}")
    except Exception as e:
        print(f"[✖] Failed to load: {e}")

def draw_scene():
    screen.fill((0,0,0))

    # Оси
    origin = project_3d_to_2d(*rotate_point(0,0,0, angle_x, angle_y))
    ox = project_3d_to_2d(*rotate_point(100,0,0, angle_x, angle_y))
    oy = project_3d_to_2d(*rotate_point(0,100,0, angle_x, angle_y))
    oz = project_3d_to_2d(*rotate_point(0,0,100, angle_x, angle_y))
    ox_neg = project_3d_to_2d(*rotate_point(-100,0,0, angle_x, angle_y))
    oy_neg = project_3d_to_2d(*rotate_point(0,-100,0, angle_x, angle_y))
    oz_neg = project_3d_to_2d(*rotate_point(0,0,-100, angle_x, angle_y))

    pygame.draw.line(screen, (255,0,0), origin, ox, 2)
    pygame.draw.line(screen, (255,0,0), origin, ox_neg, 2)
    pygame.draw.line(screen, (0,255,0), origin, oy, 2)
    pygame.draw.line(screen, (0,255,0), origin, oy_neg, 2)
    pygame.draw.line(screen, (0,0,255), origin, oz, 2)
    pygame.draw.line(screen, (0,0,255), origin, oz_neg, 2)

    # Полигоны
    for i, poly in enumerate(polygons):
        if len(poly["indices"]) >= 3:
            verts = [points[j] for j in poly["indices"]]
            proj_verts = [project_3d_to_2d(*rotate_point(*v, angle_x, angle_y)) for v in verts]
            if poly["filled"]:
                pygame.draw.polygon(screen, (100, 100, 100), proj_verts)
            elif len(poly["indices"]) == 4:
                draw_poly_grid(poly["indices"], steps=10)

    # Линии
    for p1, p2 in lines:
        x1, y1, z1 = rotate_point(*points[p1], angle_x, angle_y)
        x2, y2, z2 = rotate_point(*points[p2], angle_x, angle_y)
        x1p, y1p = project_3d_to_2d(x1, y1, z1)
        x2p, y2p = project_3d_to_2d(x2, y2, z2)
        pygame.draw.line(screen, (255,255,255), (x1p, y1p), (x2p, y2p), 1)

    # Точки
    for i, pt in enumerate(points):
        xr, yr, zr = rotate_point(*pt, angle_x, angle_y)
        xp, yp = project_3d_to_2d(xr, yr, zr)
        pygame.gfxdraw.filled_circle(screen, int(xp), int(yp), 5, (255,255,255))
        if show_labels:
            number_text = font.render(f"{i+1}", True, (255, 255, 255), (0, 0, 0))
            screen.blit(number_text, (xp + 6, yp - 8))
            draw_text(f"({pt[0]:.2f}, {pt[1]:.2f}, {pt[2]:.2f})", xp+6, yp+8)

    # после точек и линий, до HUD
    for curve in curves:
        # получить Screen-координаты трёх точек
        P = []
        for key in ("p0","p1","p2"):
            pt = points[curve[key]]
            P.append(project_3d_to_2d(*rotate_point(*pt, angle_x, angle_y)))
        last = P[0]
        for t_step in range(1, 101):
            t = t_step / 100
            x = (1-t)**2*P[0][0] + 2*(1-t)*t*P[1][0] + t**2*P[2][0]
            y = (1-t)**2*P[0][1] + 2*(1-t)*t*P[1][1] + t**2*P[2][1]
            pygame.draw.line(screen, curve_color, last, (x,y), 2)
            last = (x,y)

    if show_labels:
        # Деления на осях
        for axis, color, vec in [
            ('x', (255, 0, 0), (1, 0, 0)),
            ('y', (0, 255, 0), (0, 1, 0)),
            ('z', (0, 0, 255), (0, 0, 1)),
        ]:
            for i in range(1, 21):
                for sign in [-1, 1]:
                    dx, dy, dz = [v * i * sign for v in vec]
                    p = project_3d_to_2d(*rotate_point(dx, dy, dz, angle_x, angle_y))
                    draw_text(f"{i*sign}", p[0], p[1], color=color)

        # Метки осей
        draw_text("X: Red", 10, 60, color=(255, 0, 0))
        draw_text("Y: Green", 10, 85, color=(0, 255, 0))
        draw_text("Z: Blue", 10, 110, color=(0, 0, 255))

        # Подсказки ввода
        if input_mode == "point":
            coord = coord_order[coord_index]
            draw_text(f"[POINT] Enter {coord}: {current_point[coord]}", 10, 10)
            draw_text("Enter - next, Backspace - delete, L - line, D - delete, P - polygon, F - fill", 10, 35)
        elif input_mode == "line":
            p1 = current_line['p1']
            p2 = current_line['p2']
            draw_text(f"[LINE] p1={p1}, p2={p2}", 10, 10)
            draw_text("Enter - confirm, Backspace - delete digit, L - point, D - delete, P - polygon, F - fill", 10, 35)
        elif input_mode == "delete":
            draw_text(f"[DELETE] Enter point: {current_delete+1 if current_delete is not None else ''}", 10, 10)
            draw_text("Enter - delete point, Backspace - cancel, L - line, D - point, P - polygon, F - fill", 10, 35)
        elif input_mode == "polygon":
            poly_str = ",".join(str(i+1) for i in current_polygon) if current_polygon else ""
            draw_text(f"[POLYGON] Points: {poly_str} Current: {point_index_input}", 10, 10)
            draw_text("Enter - finish (>=3), Space - add point, Backspace - remove, L - line, D - delete, P - point, F - fill", 10, 35)
        elif input_mode == "fill":
            draw_text(f"[FILL] Enter polygon: {current_fill}", 10, 10)
            draw_text("Enter - toggle fill, Backspace - delete digit, L - line, D - delete, P - polygon, F - point", 10, 35)
        elif input_mode == "curve":
            # Получаем текущую точку из буфера (аналогично другим)
            buf = curve_input
            current_point_index = ""
            if buf:
                current_point_index = buf
            elif curve_step == 0:
                current_point_index = ""
            elif curve_step == 1:
                current_point_index = ""
            elif curve_step == 2:
                current_point_index = ""

            # Формируем строку с уже выбранными точками
            point_labels = []
            for idx in (current_curve["p0"], current_curve["p1"], current_curve["p2"]):
                if isinstance(idx, int):
                    point_labels.append(str(idx + 1))
                else:
                    point_labels.append("")

            draw_text(f"[CURVE] Points: {','.join(point_labels)} Current: {buf}", 10, 10)
            draw_text("Enter - confirm, Backspace - delete digit, L - line, D - delete, P - point, F - fill", 10, 35)

        # Инструкция по управлению
        draw_text("Arrow keys/mouse drag - rotate, Mouse wheel/+/- - zoom, F1 - toggle labels", 10, HEIGHT-30)
        draw_text("[ - save to JSON, ] - open JSON file", 10, HEIGHT-55)

        # Список точек справа
        x0 = WIDTH - 220
        y0 = 10
        draw_text("Points:", x0, y0, color=(200, 200, 50))
        for i, pt in enumerate(points):
            line = f"{i+1}. {pt[0]:.2f}/{pt[1]:.2f}/{pt[2]:.2f}"
            draw_text(line, x0, y0 + 25 + i * 20, color=(180, 180, 180))

        # Список полигонов
        y0 = y0 + 25 + len(points) * 20 + 20
        draw_text("Polygons:", x0, y0, color=(200, 200, 50))
        for i, poly in enumerate(polygons):
            indices_str = f"({','.join(str(j+1) for j in poly['indices'])})"
            filled_str = "Yes" if poly["filled"] else "No"
            line = f"{i+1}. {indices_str} Filled: {filled_str}"
            draw_text(line, x0, y0 + 25 + i * 20, color=(180, 180, 180))

        # Список кривых
        y0 = y0 + 25 + len(polygons) * 20 + 20
        draw_text("Curves:", x0, y0, color=(200, 200, 50))
        for i, curve in enumerate(curves):
            line = f"{i+1}. ({curve['p0']+1},{curve['p1']+1},{curve['p2']+1})"
            draw_text(line, x0, y0 + 25 + i * 20, color=(180, 180, 180))

    pygame.display.flip()

async def main():
    while True:
        handle_input()
        draw_scene()
        await asyncio.sleep(1/FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
