import pygame
from model import state
from utils import save_to_json, load_from_json

def handle_input():
    global state
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        elif event.type == pygame.KEYDOWN:
            print(f"Key pressed: {event.key}, unicode: '{event.unicode}', mode: {state.input_mode}")
            if event.key == pygame.K_F1:
                state.show_labels = not state.show_labels
                continue

            if state.input_mode == "point":
                coord = state.coord_order[state.coord_index]
                if event.key == pygame.K_RETURN:
                    if state.current_point[coord] != "":
                        state.coord_index += 1
                        if state.coord_index >= 3:
                            try:
                                x = float(state.current_point['x'])
                                y = float(state.current_point['y'])
                                z = float(state.current_point['z'])
                                if abs(x) > 1000 or abs(y) > 1000 or abs(z) > 1000:
                                    raise ValueError("Coordinates must be between -1000 and 1000")
                                state.points.append((x, y, z))
                            except ValueError as e:
                                print(f"Error: {e}")
                            state.current_point = {"x": "", "y": "", "z": ""}
                            state.coord_index = 0
                elif event.key == pygame.K_BACKSPACE:
                    state.current_point[coord] = state.current_point[coord][:-1]
                elif event.key == pygame.K_l:
                    state.input_mode = "line"
                    state.current_line = {"p1": "", "p2": ""}
                    state.line_step = 1
                elif event.key == pygame.K_d:
                    state.input_mode = "delete"
                    state.current_delete = None
                elif event.key == pygame.K_p:
                    state.input_mode = "polygon"
                    state.current_polygon = []
                    state.polygon_step = 1
                    state.point_index_input = ""
                elif event.key == pygame.K_f:
                    state.input_mode = "fill"
                    state.current_fill = ""
                elif event.key == pygame.K_c:
                    state.input_mode = "curve"
                    state.current_curve = []
                    state.curve_step = 1
                    state.curve_input = ""  # сброс буфера
                else:
                    if event.unicode.isdigit() or event.unicode in '.-':
                        state.current_point[coord] += event.unicode

            elif state.input_mode == "line":
                if event.key == pygame.K_RETURN:
                    if state.line_step == 1 and state.current_line['p1'].isdigit():
                        state.line_step = 2
                    elif state.line_step == 2 and state.current_line['p2'].isdigit():
                        p1 = int(state.current_line['p1']) - 1
                        p2 = int(state.current_line['p2']) - 1
                        if 0 <= p1 < len(state.points) and 0 <= p2 < len(state.points):
                            new_line = (p1, p2)
                            rev = (p2, p1)
                            if new_line in state.lines:
                                state.lines.remove(new_line)
                            elif rev in state.lines:
                                state.lines.remove(rev)
                            else:
                                state.lines.append(new_line)
                        state.current_line = {"p1": "", "p2": ""}
                        state.line_step = 1
                elif event.key == pygame.K_BACKSPACE:
                    if state.line_step == 1 and state.current_line['p1']:
                        state.current_line['p1'] = state.current_line['p1'][:-1]
                    elif state.line_step == 2 and state.current_line['p2']:
                        state.current_line['p2'] = state.current_line['p2'][:-1]
                    elif state.line_step == 2:
                        state.line_step = 1
                        state.current_line['p2'] = ""
                elif event.key == pygame.K_l:
                    state.input_mode = "point"
                    state.current_line = {"p1": "", "p2": ""}
                    state.line_step = 1
                elif event.key == pygame.K_d:
                    state.input_mode = "delete"
                    state.current_delete = None
                elif event.key == pygame.K_p:
                    state.input_mode = "polygon"
                    state.current_polygon = []
                    state.polygon_step = 1
                    state.point_index_input = ""
                elif event.key == pygame.K_f:
                    state.input_mode = "fill"
                    state.current_fill = ""
                else:
                    if event.unicode.isdigit():
                        if state.line_step == 1:
                            state.current_line['p1'] += event.unicode
                        elif state.line_step == 2:
                            state.current_line['p2'] += event.unicode

            elif state.input_mode == "delete":
                if event.key == pygame.K_RETURN:
                    if state.current_delete is not None:
                        idx = state.current_delete
                        if 0 <= idx < len(state.points):
                            state.points.pop(idx)
                            state.lines[:] = [(p1, p2) for p1, p2 in state.lines if p1 != idx and p2 != idx]
                            state.lines[:] = [(p1 - (1 if p1 > idx else 0), p2 - (1 if p2 > idx else 0)) for p1, p2 in state.lines]
                            state.polygons[:] = [{"indices": [i - (1 if i > idx else 0) for i in poly["indices"]], "filled": poly["filled"]} for poly in state.polygons if idx not in poly["indices"]]
                            state.curves[:] = [[i - (1 if i > idx else 0) for i in curve] for curve in state.curves if idx not in curve]
                        state.current_delete = None
                elif event.key == pygame.K_BACKSPACE:
                    state.current_delete = None
                elif event.key == pygame.K_l:
                    state.input_mode = "line"
                    state.current_line = {"p1": "", "p2": ""}
                    state.line_step = 1
                elif event.key == pygame.K_d:
                    state.input_mode = "point"
                    state.current_delete = None
                elif event.key == pygame.K_p:
                    state.input_mode = "polygon"
                    state.current_polygon = []
                    state.polygon_step = 1
                    state.point_index_input = ""
                elif event.key == pygame.K_f:
                    state.input_mode = "fill"
                    state.current_fill = ""
                else:
                    if event.unicode.isdigit():
                        idx = int(event.unicode) - 1
                        if 0 <= idx < len(state.points):
                            state.current_delete = idx

            elif state.input_mode == "polygon":
                if event.key == pygame.K_RETURN:
                    # Если в буфере ввода есть число — добавим его в текущий полигон
                    if state.point_index_input.strip():
                        if state.point_index_input.strip().isdigit():
                            idx = int(state.point_index_input.strip()) - 1  # -1 для индексации с 0
                            if 0 <= idx < len(state.points):
                                state.current_polygon.append(idx)
                        state.point_index_input = ""

                    # Если полигон достаточно большой — добавляем или удаляем
                    if len(state.current_polygon) >= 3:
                        new_poly = {"indices": state.current_polygon.copy(), "filled": False}
                        if tuple(state.current_polygon) in [tuple(p["indices"]) for p in state.polygons]:
                            state.polygons[:] = [p for p in state.polygons if tuple(p["indices"]) != tuple(state.current_polygon)]
                        else:
                            state.polygons.append(new_poly)
                        state.current_polygon = []
                        state.polygon_step = 1
                    elif state.current_polygon:
                        state.polygon_step += 1

                    state.point_index_input = ""

                elif event.key == pygame.K_BACKSPACE:
                    # Если в буфере есть что-то — удаляем последний символ
                    if state.point_index_input:
                        state.point_index_input = state.point_index_input[:-1]
                    # Иначе — удаляем последний индекс из полигона (откат)
                    elif state.current_polygon:
                        state.current_polygon.pop()
                        state.polygon_step = max(1, state.polygon_step - 1)
                    else:
                        state.input_mode = "point"
                        state.polygon_step = 1
                        state.point_index_input = ""

                # При пробеле или запятой — добавляем число в полигон и сбрасываем буфер
                elif event.key == pygame.K_SPACE or event.unicode == ',':
                    if state.point_index_input.strip().isdigit():
                        idx = int(state.point_index_input.strip()) - 1  # -1 для индексации с 0
                        if 0 <= idx < len(state.points):
                            state.current_polygon.append(idx)
                            state.polygon_step += 1
                    state.point_index_input = ""

                elif event.key == pygame.K_l:
                    state.input_mode = "line"
                    state.current_line = {"p1": "", "p2": ""}
                    state.line_step = 1
                    state.point_index_input = ""

                elif event.key == pygame.K_d:
                    state.input_mode = "delete"
                    state.current_delete = None
                    state.point_index_input = ""

                elif event.key == pygame.K_p:
                    state.input_mode = "point"
                    state.current_polygon = []
                    state.polygon_step = 1
                    state.point_index_input = ""

                elif event.key == pygame.K_f:
                    state.input_mode = "fill"
                    state.current_fill = ""
                    state.point_index_input = ""

                else:
                    # Накопление цифр в буфере ввода
                    if event.unicode.isdigit():
                        state.point_index_input += event.unicode

            elif state.input_mode == "fill":
                if event.key == pygame.K_RETURN:
                    if state.current_fill.isdigit():
                        idx = int(state.current_fill) - 1
                        if 0 <= idx < len(state.polygons):
                            state.polygons[idx]["filled"] = not state.polygons[idx]["filled"]
                    state.current_fill = ""
                elif event.key == pygame.K_BACKSPACE:
                    state.current_fill = state.current_fill[:-1]
                elif event.key == pygame.K_l:
                    state.input_mode = "line"
                    state.current_line = {"p1": "", "p2": ""}
                    state.line_step = 1
                elif event.key == pygame.K_d:
                    state.input_mode = "delete"
                    state.current_delete = None
                elif event.key == pygame.K_p:
                    state.input_mode = "polygon"
                    state.current_polygon = []
                    state.polygon_step = 1
                    state.point_index_input = ""
                elif event.key == pygame.K_f:
                    state.input_mode = "point"
                    state.current_fill = ""
                else:
                    if event.unicode.isdigit():
                        state.current_fill += event.unicode

            elif state.input_mode == "curve":
                if event.key == pygame.K_RETURN:
                    if state.point_index_input.strip().isdigit():
                        idx = int(state.point_index_input.strip()) - 1
                        if 0 <= idx < len(state.points):
                            state.current_curve.append(idx)
                    state.point_index_input = ""
                    if len(state.current_curve) == 3:
                        new_curve = state.current_curve.copy()
                        if new_curve in state.curves:
                            state.curves.remove(new_curve)
                        else:
                            state.curves.append(new_curve)
                        state.current_curve = []
                        state.curve_step = 1
                    elif state.current_curve:
                        state.curve_step = min(state.curve_step + 1, 3)
                elif event.key == pygame.K_BACKSPACE:
                    if state.point_index_input:
                        state.point_index_input = state.point_index_input[:-1]
                    elif state.current_curve:
                        state.current_curve.pop()
                        state.curve_step = max(1, state.curve_step - 1)
                    else:
                        state.input_mode = "point"
                        state.curve_step = 1
                        state.point_index_input = ""
                elif event.key == pygame.K_SPACE or event.unicode == ',':
                    if state.point_index_input.strip().isdigit():
                        idx = int(state.point_index_input.strip()) - 1
                        if 0 <= idx < len(state.points):
                            state.current_curve.append(idx)
                            state.curve_step = min(state.curve_step + 1, 3)
                    state.point_index_input = ""
                elif event.key == pygame.K_l:
                    state.input_mode = "line"
                    state.current_line = {"p1": "", "p2": ""}
                    state.line_step = 1
                    state.point_index_input = ""
                elif event.key == pygame.K_d:
                    state.input_mode = "delete"
                    state.current_delete = None
                    state.point_index_input = ""
                elif event.key == pygame.K_p:
                    state.input_mode = "polygon"
                    state.current_polygon = []
                    state.polygon_step = 1
                    state.point_index_input = ""
                elif event.key == pygame.K_f:
                    state.input_mode = "fill"
                    state.current_fill = ""
                    state.point_index_input = ""
                elif event.key == pygame.K_c:
                    state.input_mode = "point"
                    state.current_curve = []
                    state.curve_step = 1
                    state.point_index_input = ""
                else:
                    if event.unicode.isdigit():
                        state.point_index_input += event.unicode

            if event.key == pygame.K_LEFTBRACKET:
                save_to_json()
            elif event.key == pygame.K_RIGHTBRACKET:
                load_from_json()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                state.mouse_dragging = True
                state.last_mouse_pos = event.pos
            elif event.button == 3:
                state.right_mouse_dragging = True
                state.last_mouse_pos = event.pos
            elif event.button == 4:
                state.d = min(state.d + 0.5, 10)
            elif event.button == 5:
                state.d = max(state.d - 0.5, 1)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                state.mouse_dragging = False
                state.last_mouse_pos = None
            elif event.button == 3:
                state.right_mouse_dragging = False
                state.last_mouse_pos = None

        elif event.type == pygame.MOUSEMOTION:
            if state.mouse_dragging and state.last_mouse_pos:
                dx, dy = event.pos[0] - state.last_mouse_pos[0], event.pos[1] - state.last_mouse_pos[1]
                state.angle_y += dx * state.mouse_sensitivity
                state.angle_x -= dy * state.mouse_sensitivity
                state.last_mouse_pos = event.pos
            elif state.right_mouse_dragging and state.last_mouse_pos:
                dx, dy = event.pos[0] - state.last_mouse_pos[0], event.pos[1] - state.last_mouse_pos[1]
                state.camera_pos[0] -= dx * 0.01
                state.camera_pos[1] += dy * 0.01
                state.last_mouse_pos = event.pos

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        state.camera_pos[2] += 0.2
    if keys[pygame.K_s]:
        state.camera_pos[2] -= 0.2
    if keys[pygame.K_EQUALS] or keys[pygame.K_KP_PLUS]:
        state.d = min(state.d + 0.1, 10)
    if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS]:
        state.d = max(state.d - 0.1, 1)
    if keys[pygame.K_LEFT]:
        state.angle_y -= state.rotation_speed
    if keys[pygame.K_RIGHT]:
        state.angle_y += state.rotation_speed
    if keys[pygame.K_UP]:
        state.angle_x -= state.rotation_speed
    if keys[pygame.K_DOWN]:
        state.angle_x += state.rotation_speed