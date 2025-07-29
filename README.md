# 3D Model Editor

A simple 3D editor for creating and manipulating points, lines, polygons, and quadratic Bezier curves in 3D space. Supports rotation, scaling, panning, saving/loading models in JSON, and a user-friendly interface with HUD.

## Controls

- **Arrows / Left Mouse Drag** — Rotate model (X and Y axes)
- **Middle Mouse Drag** — Rotate model around Z axis
- **Right Mouse Drag** — Pan camera
- **W / S** — Move camera forward/back
- **Mouse Wheel** or **+ / -** — Zoom in/out
- **Modes:**
  - `T` (Point): Input coordinates for a new point (x, y, z, range -1000 to 1000)
  - `L` (Line): Connect two points by index
  - `D` (Delete): Delete a point by index
  - `P` (Polygon): Create a polygon by selecting point indices
  - `F` (Fill): Toggle fill for a polygon
  - `C` (Curve): Create a quadratic Bezier curve by selecting three points
- **F1** — Toggle labels (axes, points, HUD)
- **R** — Reset camera to default position and orientation
- **[** — Save model to JSON
- **]** — Load model from JSON

## Dependencies

- `pygame` (for rendering and input handling)
- `tkinter` (built into Python, for file dialogs)

---

# 3D-редактор моделей

Простой 3D-редактор для создания и редактирования точек, линий, полигонов и квадратичных кривых Безье в трёхмерном пространстве. Поддерживает вращение, масштабирование, панорамирование, сохранение/загрузку моделей в JSON и удобный интерфейс с HUD.

## Управление

- **Стрелки / Перетягивание левой кнопкой мыши** — Вращение модели (по осям X и Y)
- **Перетягивание средней кнопкой мыши** — Вращение модели вокруг оси Z
- **Перетягивание правой кнопкой мыши** — Панорамирование камеры
- **W / S** — Перемещение камеры вперёд/назад
- **Колёсико мыши** или **+ / -** — Увеличение/уменьшение масштаба
- **Режимы:**
  - `T` (Точка): Ввод координат новой точки (x, y, z, диапазон от -1000 до 1000)
  - `L` (Линия): Соединение двух точек по индексам
  - `D` (Удаление): Удаление точки по индексу
  - `P` (Полигон): Создание полигона путём выбора индексов точек
  - `F` (Заливка): Переключение заливки полигона
  - `C` (Кривая): Создание квадратичной кривой Безье путём выбора трёх точек
- **F1** — Включение/выключение меток (оси, точки, HUD)
- **R** — Сброс камеры в начальное положение и ориентацию
- **[** — Сохранение модели в JSON
- **]** — Загрузка модели из JSON

## Зависимости

- `pygame` (для рендеринга и обработки ввода)
- `tkinter` (встроен в Python, для диалогов выбора файлов)