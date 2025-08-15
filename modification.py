import pygame
from model import state
import math

class ModificationState:
    def __init__(self):
        self.active = False  # Флаг режима модификаций
        self.current_modification = None  # Текущая модификация (например, "round_polygon")
        self.polygon_index = ""  # Вводимый индекс полигона
        self.steps = ""  # Количество шагов для модификаций (гладкость кривых)

modification_state = ModificationState()

def is_valid_index_input(current_input, unicode_char, max_index):
    """Проверяет, является ли ввод допустимым индексом."""
    if not unicode_char.isdigit():
        return False
    new_input = current_input + unicode_char
    if new_input == '0' or (new_input.isdigit() and int(new_input) > max_index):
        return False
    return True

def is_valid_steps_input(current_input, unicode_char):
    """Проверяет, является ли ввод допустимым числом шагов (1-100)."""
    if not unicode_char.isdigit():
        return False
    new_input = current_input + unicode_char
    if new_input.isdigit() and (int(new_input) < 1 or int(new_input) > 100):
        return False
    return True

def round_polygon(polygon_idx, steps):
    """Округляет полигон, заменяя стороны квадратичными кривыми Безье."""
    if not (0 <= polygon_idx < len(state.polygons)):
        return

    poly = state.polygons[polygon_idx]
    indices = poly["indices"]
    if len(indices) < 3:
        return

    # Сохраняем исходные индексы и помечаем полигон как округлённый
    poly["rounded"] = True
    poly["round_steps"] = steps

def handle_modification_input():
    """Обрабатывает ввод в режиме модификаций."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                modification_state.active = False
                state.input_mode = "point"  # Возвращаемся в режим по умолчанию
                modification_state.current_modification = None
                modification_state.polygon_index = ""
                modification_state.steps = ""
                continue

            if modification_state.current_modification is None:
                if event.unicode == '1':
                    modification_state.current_modification = "round_polygon"
                    modification_state.polygon_index = ""
                    modification_state.steps = ""
            elif modification_state.current_modification == "round_polygon":
                if event.key == pygame.K_RETURN:
                    if modification_state.polygon_index.isdigit():
                        if modification_state.steps.isdigit():
                            idx = int(modification_state.polygon_index) - 1
                            steps = int(modification_state.steps)
                            round_polygon(idx, steps)
                            modification_state.current_modification = None
                            modification_state.polygon_index = ""
                            modification_state.steps = ""
                        else:
                            modification_state.steps = ""
                    else:
                        modification_state.polygon_index = ""
                elif event.key == pygame.K_BACKSPACE:
                    if modification_state.steps:
                        modification_state.steps = modification_state.steps[:-1]
                    elif modification_state.polygon_index:
                        modification_state.polygon_index = modification_state.polygon_index[:-1]
                    else:
                        modification_state.current_modification = None
                elif is_valid_index_input(modification_state.polygon_index, event.unicode, len(state.polygons)) and not modification_state.steps:
                    modification_state.polygon_index += event.unicode
                elif is_valid_steps_input(modification_state.steps, event.unicode) and modification_state.polygon_index.isdigit():
                    modification_state.steps += event.unicode