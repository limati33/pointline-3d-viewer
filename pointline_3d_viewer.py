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
WIDTH, HEIGHT = 800, 600
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

current_line = {"p1": None, "p2": None}
line_step = 1

current_delete = None  # индекс точки для удаления

font = pygame.font.SysFont("arial", 20)

# Переменные для управления мышью
mouse_dragging = False
last_mouse_pos = None

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
    """Project 3D coordinates to 2D with safeguards"""
    factor = d / (d + z) if (d + z) != 0 else 1
    factor = min(max(factor, -10), 10)  # Limit factor to prevent extreme scaling
    x2d = x * factor * WIDTH / 4 + WIDTH / 2
    y2d = -y * factor * HEIGHT / 4 + HEIGHT / 2
    x2d = max(min(x2d, 32767), -32768)  # Clamp to signed short integer range
    y2d = max(min(y2d, 32767), -32768)
    return x2d, y2d

def draw_text(text, x, y, color=(255,255,255)):
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))

def handle_input():
    """Обработка событий ввода: клавиши, мышь"""
    global input_mode, current_point, coord_index
    global current_line, line_step, angle_x, angle_y, d
    global mouse_dragging, last_mouse_pos, current_delete

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        elif event.type == pygame.KEYDOWN:
            # Вращение по стрелкам
            if event.key == pygame.K_LEFT:
                angle_y -= rotation_speed
            elif event.key == pygame.K_RIGHT:
                angle_y += rotation_speed
            elif event.key == pygame.K_UP:
                angle_x -= rotation_speed
            elif event.key == pygame.K_DOWN:
                angle_x += rotation_speed

            # Переключение режимов и ввод точек/линий/удаление
            if input_mode == "point":
                coord = coord_order[coord_index]
                if event.key == pygame.K_RETURN:
                    if current_point[coord] != "":
                        coord_index += 1
                        if coord_index >= 3:
                            # добавляем точку
                            try:
                                x = float(current_point['x'])
                                y = float(current_point['y'])
                                z = float(current_point['z'])
                                # Restrict coordinate range
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
                    # переключиться на ввод линии
                    input_mode = "line"
                    current_line = {"p1": None, "p2": None}
                    line_step = 1
                elif event.key == pygame.K_d:
                    # переключиться на режим удаления
                    input_mode = "delete"
                    current_delete = None
                else:
                    if event.unicode.isdigit() or event.unicode in '.-':
                        current_point[coord] += event.unicode

            elif input_mode == "line":
                if event.key == pygame.K_RETURN:
                    if current_line['p1'] is not None and current_line['p2'] is not None:
                        new_line = (current_line['p1'], current_line['p2'])
                        reverse_line = (current_line['p2'], current_line['p1'])
                        # Проверяем, существует ли линия
                        if new_line in lines or reverse_line in lines:
                            # Удаляем линию, если она уже существует
                            if new_line in lines:
                                lines.remove(new_line)
                            elif reverse_line in lines:
                                lines.remove(reverse_line)
                        else:
                            # Добавляем новую линию
                            lines.append(new_line)
                        input_mode = "point"
                        current_line = {"p1": None, "p2": None}
                        line_step = 1
                elif event.key == pygame.K_BACKSPACE:
                    if line_step == 2:
                        current_line['p2'] = None
                        line_step = 2
                    else:
                        current_line['p1'] = None
                        line_step = 1
                elif event.key == pygame.K_l:
                    # переключиться на ввод точек
                    input_mode = "point"
                    current_line = {"p1": None, "p2": None}
                    line_step = 1
                elif event.key == pygame.K_d:
                    # переключиться на режим удаления
                    input_mode = "delete"
                    current_line = {"p1": None, "p2": None}
                    line_step = 1
                    current_delete = None
                else:
                    if event.unicode.isdigit():
                        idx = int(event.unicode) - 1
                        if 0 <= idx < len(points):
                            if line_step == 1:
                                current_line['p1'] = idx
                                line_step = 2
                            elif line_step == 2:
                                current_line['p2'] = idx

            elif input_mode == "delete":
                if event.key == pygame.K_RETURN:
                    if current_delete is not None:
                        idx = current_delete
                        if 0 <= idx < len(points):
                            # Удаляем точку
                            points.pop(idx)
                            # Удаляем все линии, связанные с этой точкой
                            lines[:] = [(p1, p2) for p1, p2 in lines if p1 != idx and p2 != idx]
                            # Обновляем индексы линий для оставшихся точек
                            lines[:] = [(p1 - 1 if p1 > idx else p1, p2 - 1 if p2 > idx else p2) for p1, p2 in lines]
                        input_mode = "point"
                        current_delete = None
                elif event.key == pygame.K_BACKSPACE:
                    current_delete = None
                elif event.key == pygame.K_l:
                    # переключиться на ввод линии
                    input_mode = "line"
                    current_line = {"p1": None, "p2": None}
                    line_step = 1
                    current_delete = None
                elif event.key == pygame.K_d:
                    # переключиться на ввод точек
                    input_mode = "point"
                    current_delete = None
                else:
                    if event.unicode.isdigit():
                        idx = int(event.unicode) - 1
                        if 0 <= idx < len(points):
                            current_delete = idx

            # Сохранение / Загрузка
            if event.key == pygame.K_s:
                save_to_json()
            elif event.key == pygame.K_o:
                load_from_json()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                mouse_dragging = True
                last_mouse_pos = event.pos
            elif event.button == 4:  # Прокрутка вверх
                d = min(d + 0.5, 10)
            elif event.button == 5:  # Прокрутка вниз
                d = max(d - 0.5, 1)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Левая кнопка мыши отпущена
                mouse_dragging = False
                last_mouse_pos = None

        elif event.type == pygame.MOUSEMOTION and mouse_dragging:
            if last_mouse_pos is not None:
                dx, dy = event.pos[0] - last_mouse_pos[0], event.pos[1] - last_mouse_pos[1]
                angle_y += dx * mouse_sensitivity  # Горизонтальное движение -> вращение вокруг Y
                angle_x -= dy * mouse_sensitivity  # Вертикальное движение -> вращение вокруг X
                last_mouse_pos = event.pos

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
    pygame.draw.line(screen, (255,0,0), origin, ox, 2)
    pygame.draw.line(screen, (0,255,0), origin, oy, 2)
    pygame.draw.line(screen, (0,0,255), origin, oz, 2)

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
        # Показать номер точки и координаты
        draw_text(f"{i+1}", xp+6, yp-8)
        draw_text(f"({pt[0]:.2f}, {pt[1]:.2f}, {pt[2]:.2f})", xp+6, yp+8)

    # Подсказки ввода
    if input_mode == "point":
        coord = coord_order[coord_index]
        draw_text(f"[POINT] Enter {coord}: {current_point[coord]}", 10, 10)
        draw_text("Enter - next, Backspace - delete, L - line mode, D - delete mode", 10, 35)
    elif input_mode == "line":
        p1 = current_line['p1']
        p2 = current_line['p2']
        draw_text(f"[LINE] p1={p1+1 if p1 is not None else ''}, p2={p2+1 if p2 is not None else ''}", 10, 10)
        draw_text("Enter - toggle line, Backspace - cancel, L - point mode, D - delete mode", 10, 35)
    else:  # delete mode
        draw_text(f"[DELETE] Enter point: {current_delete+1 if current_delete is not None else ''}", 10, 10)
        draw_text("Enter - delete point, Backspace - cancel, L - line mode, D - point mode", 10, 35)

    # Инструкция по управлению
    draw_text("Arrow keys or mouse drag - rotate, Mouse wheel - zoom", 10, HEIGHT-30)
    draw_text("S - save to JSON, O - open JSON file", 10, HEIGHT - 55)
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