import pygame
from model import (
    input_mode, current_point, coord_index,
    current_line, line_step, current_delete,
    current_polygon, polygon_step,
    current_fill, point_index_input,
    current_curve, curve_step,
    points, lines, polygons, curves,
    angle_x, angle_y, d,
    mouse_dragging, last_mouse_pos, right_mouse_dragging,
    camera_pos, show_labels,
    coord_order, mouse_sensitivity, rotation_speed
)
from utils import save_to_json, load_from_json

def handle_input():
    global input_mode, current_point, coord_index
    global current_line, line_step, current_delete
    global current_polygon, polygon_step
    global current_fill, point_index_input
    global current_curve, curve_step
    global points, lines, polygons, curves
    global angle_x, angle_y, d
    global mouse_dragging, last_mouse_pos, right_mouse_dragging, camera_pos, show_labels

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
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
                                    raise ValueError("Координаты должны быть от -1000 до 1000")
                                points.append((x, y, z))
                            except ValueError as e:
                                print(f"Ошибка: {e}")
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
                    current_curve = []
                    curve_step = 1
                    point_index_input = ""
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
                elif event.key == pygame.K_c:
                    input_mode = "curve"
                    current_curve = []
                    curve_step = 1
                    point_index_input = ""
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
                elif event.key == pygame.K_c:
                    input_mode = "curve"
                    current_curve = []
                    curve_step = 1
                    point_index_input = ""
                else:
                    if event.unicode.isdigit():
                        idx = int(event.unicode) - 1
                        if 0 <= idx < len(points):
                            current_delete = idx

            elif input_mode == "polygon":
                if event.key == pygame.K_RETURN:
                    if point_index_input.strip():
                        if point_index_input.strip().isdigit():
                            idx = int(point_index_input.strip()) - 1
                            if 0 <= idx < len(points):
                                current_polygon.append(idx)
                        point_index_input = ""
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
                    if point_index_input:
                        point_index_input = point_index_input[:-1]
                    elif current_polygon:
                        current_polygon.pop()
                        polygon_step = max(1, polygon_step - 1)
                    else:
                        input_mode = "point"
                        polygon_step = 1
                        point_index_input = ""
                elif event.key == pygame.K_SPACE or event.unicode == ',':
                    if point_index_input.strip().isdigit():
                        idx = int(point_index_input.strip()) - 1
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
                elif event.key == pygame.K_c:
                    input_mode = "curve"
                    current_curve = []
                    curve_step = 1
                    point_index_input = ""
                else:
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
                elif event.key == pygame.K_c:
                    input_mode = "curve"
                    current_curve = []
                    curve_step = 1
                    point_index_input = ""
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