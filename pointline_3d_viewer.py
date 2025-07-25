import asyncio
import platform
import pygame
import pygame.gfxdraw
import json
import os
from math import cos, sin
import tkinter as tk
from tkinter import filedialog

# Инициализация Pygame
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Projection with Rotation")
FPS = 60

# Параметры проекции и вращения
d = 4.0              # "расстояние" до экрана / коэффициент масштабирования
angle_x = 0.0        # угол вращения вокруг X (в радианах)
angle_y = 0.0        # угол вращения вокруг Y
rotation_speed = 0.05
mouse_sensitivity = 0.005  # чувствительность мыши для вращения

points = []  # список 3D-точек
lines = []   # список соединений (pairs of point indices)

# Режим ввода: 'point', 'line' или 'delete'
input_mode = "point"
current_point = {"x": "", "y": "", "z": ""}
coord_order = ["x", "y", "z"]
coord_index = 0

current_line = {"p1": "", "p2": ""}
line_step = 1

current_delete = None  # индекс точки для удаления

font = pygame.font.SysFont("arial", 20)

# Переменные для управления мышью
mouse_dragging = False
last_mouse_pos = None
camera_pos = [0.0, 0.0, -5.0]  # камера чуть "позади"
right_mouse_dragging = False

def rotate_point(x, y, z, ax, ay):
    """
    Вращение точки вокруг осей X и Y.
    Сначала вокруг X, потом вокруг Y.
    """
    # вращение вокруг X
    y2 = y * cos(ax) - z * sin(ax)
    z2 = y * sin(ax) + z * cos(ax)
    # вращение вокруг Y
    x2 = x * cos(ay) + z2 * sin(ay)
    z3 = -x * sin(ay) + z2 * cos(ay)
    return x2, y2, z3

def project_3d_to_2d(x, y, z):
    # сдвиг относительно камеры
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
    global right_mouse_dragging, camera_pos

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        elif event.type == pygame.KEYDOWN:
            # Режимы управления — одноразовые
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
                else:
                    if event.unicode.isdigit() or event.unicode in '.-':
                        current_point[coord] += event.unicode

            elif input_mode == "line":
                if event.key == pygame.K_RETURN:
                    if line_step == 1 and current_line['p1'].isdigit():
                        idx = int(current_line['p1']) - 1
                        if 0 <= idx < len(points):
                            current_line['p1'] = idx
                            line_step = 2
                    elif line_step == 2 and current_line['p2'].isdigit():
                        idx = int(current_line['p2']) - 1
                        if 0 <= idx < len(points):
                            current_line['p2'] = idx
                            p1 = current_line['p1']
                            p2 = current_line['p2']
                            new_line = (p1, p2)
                            rev_line = (p2, p1)
                            if new_line in lines:
                                lines.remove(new_line)
                            elif rev_line in lines:
                                lines.remove(rev_line)
                            else:
                                lines.append(new_line)
                            input_mode = "point"
                            current_line = {"p1": "", "p2": ""}
                            line_step = 1
                elif event.key == pygame.K_BACKSPACE:
                    if line_step == 1:
                        current_line['p1'] = current_line['p1'][:-1]
                    elif line_step == 2:
                        current_line['p2'] = current_line['p2'][:-1]
                elif event.key == pygame.K_l:
                    input_mode = "point"
                    current_line = {"p1": "", "p2": ""}
                    line_step = 1
                elif event.key == pygame.K_d:
                    input_mode = "delete"
                    current_delete = None
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
                        input_mode = "point"
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
                else:
                    if event.unicode.isdigit():
                        idx = int(event.unicode) - 1
                        if 0 <= idx < len(points):
                            current_delete = idx

            # Сохранение / загрузка
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

    # Обработка зажатых клавиш
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
            return  # пользователь отменил
        data = {
            "points": points,
            "lines": lines
        }
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[✔] Saved to {file_path}")
    except Exception as e:
        print(f"[✖] Failed to save: {e}")

def load_from_json():
    global points, lines
    try:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Open file"
        )
        if not file_path:
            return  # пользователь отменил
        with open(file_path, "r") as f:
            data = json.load(f)
        points = [tuple(p) for p in data.get("points", [])]
        lines = [tuple(l) for l in data.get("lines", [])]
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

    # Деления на осях
    for axis, color, vec in [
        ('x', (255, 0, 0), (1, 0, 0)),
        ('y', (0, 255, 0), (0, 1, 0)),
        ('z', (0, 0, 255), (0, 0, 1)),
    ]:
        for i in range(1, 101):
            for sign in [-1, 1]:
                dx, dy, dz = [v * i * sign for v in vec]
                p = project_3d_to_2d(*rotate_point(dx, dy, dz, angle_x, angle_y))
                draw_text(f"{i*sign}", p[0], p[1], color=color)

    # Метки осей
    draw_text("X: Red", 10, 60, color=(255, 0, 0))
    draw_text("Y: Green", 10, 85, color=(0, 255, 0))
    draw_text("Z: Blue", 10, 110, color=(0, 0, 255))

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
        # Номер точки с фоном (негатив)
        number_text = font.render(f"{i+1}", True, (255, 255, 255), (0, 0, 0))  # белый текст, чёрный фон
        screen.blit(number_text, (xp + 6, yp - 8))
        draw_text(f"({pt[0]:.2f}, {pt[1]:.2f}, {pt[2]:.2f})", xp+6, yp+8)

    # Подсказки ввода
    if input_mode == "point":
        coord = coord_order[coord_index]
        draw_text(f"[POINT] Enter {coord}: {current_point[coord]}", 10, 10)
        draw_text("Enter - next, Backspace - delete, L - line mode, D - delete mode", 10, 35)
    elif input_mode == "line":
        p1 = current_line['p1']
        p2 = current_line['p2']
        draw_text(f"[LINE] p1={p1}, p2={p2}", 10, 10)
        draw_text("Enter - confirm, Backspace - delete digit, L - point mode, D - delete mode", 10, 35)
    else:
        draw_text(f"[DELETE] Enter point: {current_delete+1 if current_delete is not None else ''}", 10, 10)
        draw_text("Enter - delete point, Backspace - cancel, L - line mode, D - point mode", 10, 35)

    draw_text("Arrow keys/mouse drag - rotate, Mouse wheel/+/- - zoom", 10, HEIGHT-30)
    draw_text("[ - save to JSON, ] - open JSON file", 10, HEIGHT - 55)

    # Список точек справа
    x0 = WIDTH - 220
    y0 = 10
    draw_text("Points:", x0, y0, color=(200, 200, 50))
    for i, pt in enumerate(points):
        line = f"{i+1}. {pt[0]:.2f}/{pt[1]:.2f}/{pt[2]:.2f}"
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
