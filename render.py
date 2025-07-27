import pygame
import pygame.gfxdraw
from model import (
    points, lines, polygons, curves,
    input_mode, current_point, coord_order, coord_index,
    current_line, line_step, current_delete,
    current_polygon, point_index_input,
    current_fill, current_curve, curve_step,
    curve_color, show_labels
)
from transform import rotate_point, project_3d_to_2d, interpolate, quadratic_bezier
from config import WIDTH, HEIGHT

# в начале файла:
_FONT = None
_SCREEN = None

def draw_text(text, x, y, color=(255,255,255)):
    surf = _FONT.render(text, True, color)
    _SCREEN.blit(surf, (x, y))

def draw_poly_grid(poly_idx_list, steps=10):
    verts = [points[i] for i in poly_idx_list]
    A, B, C, D = verts
    for i in range(steps+1):
        t = i/steps
        s = rotate_point(*interpolate(A, B, t), angle_x, angle_y)
        e = rotate_point(*interpolate(D, C, t), angle_x, angle_y)
        x1,y1 = project_3d_to_2d(*s)
        x2,y2 = project_3d_to_2d(*e)
        pygame.draw.line(screen, (200,200,200), (x1,y1), (x2,y2), 1)
    for i in range(steps+1):
        t = i/steps
        s = rotate_point(*interpolate(A, D, t), angle_x, angle_y)
        e = rotate_point(*interpolate(B, C, t), angle_x, angle_y)
        x1,y1 = project_3d_to_2d(*s)
        x2,y2 = project_3d_to_2d(*e)
        pygame.draw.line(screen, (200,200,200), (x1,y1), (x2,y2), 1)

def draw_scene(screen, font):
    global _SCREEN, _FONT
    _SCREEN, _FONT = screen, font
    from model import angle_x, angle_y  # чтобы не было циклического импорта
    screen.fill((0,0,0))

    # Оси
    origin = project_3d_to_2d(*rotate_point(0,0,0, angle_x, angle_y))
    for vec, col in [((100,0,0),(255,0,0)), ((0,100,0),(0,255,0)), ((0,0,100),(0,0,255)),
                     ((-100,0,0),(255,0,0)),((0,-100,0),(0,255,0)),((0,0,-100),(0,0,255))]:
        end = project_3d_to_2d(*rotate_point(*vec, angle_x, angle_y))
        pygame.draw.line(screen, col, origin, end, 2)

    # Полигоны
    for poly in polygons:
        if len(poly["indices"]) >= 3:
            verts = [points[i] for i in poly["indices"]]
            proj = [project_3d_to_2d(*rotate_point(*v, angle_x, angle_y)) for v in verts]
            if poly["filled"]:
                pygame.draw.polygon(screen, (100,100,100), proj)
            elif len(poly["indices"]) == 4:
                draw_poly_grid(poly["indices"], steps=10)

    # Кривые
    for c in curves:
        if len(c) == 3:
            p0,p1,p2 = [points[i] for i in c]
            prev = None
            for i in range(21):
                t = i/20
                x,y,z = quadratic_bezier(t, p0,p1,p2)
                r = rotate_point(x,y,z, angle_x, angle_y)
                cur = project_3d_to_2d(*r)
                if prev: pygame.draw.line(screen, curve_color, prev, cur, 2)
                prev = cur

    # Линии
    for p1,p2 in lines:
        r1 = rotate_point(*points[p1], angle_x, angle_y)
        r2 = rotate_point(*points[p2], angle_x, angle_y)
        screen_p = (project_3d_to_2d(*r1), project_3d_to_2d(*r2))
        pygame.draw.line(screen, (255,255,255), *screen_p, 1)

    # Точки
    for i, pt in enumerate(points):
        xr,yr,zr = rotate_point(*pt, angle_x, angle_y)
        xp,yp = project_3d_to_2d(xr,yr,zr)
        pygame.gfxdraw.filled_circle(screen, int(xp), int(yp), 5, (255,255,255))
        if show_labels:
            txt = font.render(str(i+1), True, (255,255,255), (0,0,0))
            screen.blit(txt, (xp+6, yp-8))
            draw_text(font, screen, f"({pt[0]:.2f},{pt[1]:.2f},{pt[2]:.2f})", xp+6, yp+8)

    # HUD (метки, список примитивов, подсказки)
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
        draw_text("X: Красная", 10, 60, color=(255, 0, 0))
        draw_text("Y: Зелёная", 10, 85, color=(0, 255, 0))
        draw_text("Z: Синяя", 10, 110, color=(0, 0, 255))

        # Подсказки ввода
        if input_mode == "point":
            coord = coord_order[coord_index]
            draw_text(f"[ТОЧКА] Введите {coord}: {current_point[coord]}", 10, 10)
            draw_text("Ввод - далее, Backspace - удалить, L - линия, D - удаление, P - полигон, F - заливка, C - кривая", 10, 35)
        elif input_mode == "line":
            p1 = current_line['p1']
            p2 = current_line['p2']
            draw_text(f"[ЛИНИЯ] p1={p1}, p2={p2}", 10, 10)
            draw_text("Ввод - подтвердить, Backspace - удалить цифру, L - точка, D - удаление, P - полигон, F - заливка, C - кривая", 10, 35)
        elif input_mode == "delete":
            draw_text(f"[УДАЛЕНИЕ] Введите точку: {current_delete+1 if current_delete is not None else ''}", 10, 10)
            draw_text("Ввод - удалить точку, Backspace - отмена, L - линия, D - точка, P - полигон, F - заливка, C - кривая", 10, 35)
        elif input_mode == "polygon":
            poly_str = ",".join(str(i+1) for i in current_polygon) if current_polygon else ""
            draw_text(f"[ПОЛИГОН] Точки: {poly_str} Текущая: {point_index_input}", 10, 10)
            draw_text("Ввод - завершить (>=3), Пробел - добавить точку, Backspace - удалить, L - линия, D - удаление, P - точка, F - заливка, C - кривая", 10, 35)
        elif input_mode == "fill":
            draw_text(f"[ЗАЛИВКА] Введите полигон: {current_fill}", 10, 10)
            draw_text("Ввод - переключить заливку, Backspace - удалить цифру, L - линия, D - удаление, P - полигон, F - точка, C - кривая", 10, 35)
        elif input_mode == "curve":
            curve_str = ",".join(str(i+1) for i in current_curve) if current_curve else ""
            draw_text(f"[КРИВАЯ] Точки: {curve_str} Текущая: {point_index_input}", 10, 10)
            draw_text("Ввод - завершить (3 точки), Пробел - добавить точку, Backspace - удалить, L - линия, D - удаление, P - полигон, F - заливка, C - точка", 10, 35)

        # Инструкция по управлению
        draw_text("Стрелки/перетаскивание мышью - вращение, Колесо/+/- - масштаб, F1 - метки", 10, HEIGHT-30)
        draw_text("[ - сохранить в JSON, ] - открыть JSON", 10, HEIGHT-55)

        # Список точек справа
        x0 = WIDTH - 220
        y0 = 10
        draw_text("Точки:", x0, y0, color=(200, 200, 50))
        for i, pt in enumerate(points):
            line = f"{i+1}. {pt[0]:.2f}/{pt[1]:.2f}/{pt[2]:.2f}"
            draw_text(line, x0, y0 + 25 + i * 20, color=(180, 180, 180))

        # Список полигонов
        y0 = y0 + 25 + len(points) * 20 + 20
        draw_text("Полигоны:", x0, y0, color=(200, 200, 50))
        for i, poly in enumerate(polygons):
            indices_str = f"({','.join(str(j+1) for j in poly['indices'])})"
            filled_str = "Да" if poly["filled"] else "Нет"
            line = f"{i+1}. {indices_str} Заливка: {filled_str}"
            draw_text(line, x0, y0 + 25 + i * 20, color=(180, 180, 180))

        # Список кривых
        y0 = y0 + 25 + len(polygons) * 20 + 20
        draw_text("Кривые:", x0, y0, color=(200, 200, 50))
        for i, curve in enumerate(curves):
            indices_str = f"({','.join(str(j+1) for j in curve)})"
            line = f"{i+1}. {indices_str}"
            draw_text(line, x0, y0 + 25 + i * 20, color=(180, 180, 180))

    pygame.display.flip()