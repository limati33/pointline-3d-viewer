# Параметры проекции и вращения
d = 4.0
angle_x = 0.0
angle_y = 0.0
rotation_speed = 0.05
mouse_sensitivity = 0.005

points = []
lines = []
polygons = []
curves = []

input_mode = "point"
current_point = {"x": "", "y": "", "z": ""}
coord_order = ["x", "y", "z"]
coord_index = 0

current_line = {"p1": "", "p2": ""}
line_step = 1

current_delete = None

current_polygon = []
polygon_step = 1

current_fill = ""
point_index_input = ""

current_curve = []
curve_step = 1
curve_color = (255, 128, 0)

mouse_dragging = False
last_mouse_pos = None
camera_pos = [0.0, 0.0, -5.0]
right_mouse_dragging = False

show_labels = True
