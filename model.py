class State:
    def __init__(self):
        # Параметры проекции и вращения
        self.d = 4.0
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0  # Исправлено с angel_z на angle_z
        self.zoom = 1.0
        self.rotation_speed = 0.05
        self.mouse_sensitivity = 0.005

        # Объекты
        self.points = []
        self.lines = []
        self.polygons = []
        self.curves = []

        # Состояния ввода
        self.input_mode = "point"
        self.current_point = {"x": "", "y": "", "z": ""}
        self.coord_order = ["x", "y", "z"]
        self.coord_index = 0

        self.current_line = {"p1": "", "p2": ""}
        self.line_step = 1
        self.current_delete = None

        self.current_polygon = []
        self.polygon_step = 1

        self.current_fill = ""
        self.point_index_input = ""

        self.current_curve = []
        self.curve_step = 1
        self.curve_color = (255, 128, 0)

        # Камера
        self.mouse_dragging = False
        self.middle_mouse_dragging = False
        self.right_mouse_dragging = False
        self.last_mouse_pos = None  # Изменено на None для соответствия input_handler.py
        self.camera_pos = [0.0, 0.0, 0.0]  # Начальная позиция камеры
        self.camera_distance = 5.0

        # UI
        self.show_labels = True

# Создание одного общего объекта состояния
state = State()