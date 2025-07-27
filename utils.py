import json
import tkinter as tk
from tkinter import filedialog
from model import state  # Импортируем объект состояния

def save_to_json():
    try:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Сохранить как"
        )
        if not file_path:
            return
        data = {
            "points": state.points,
            "lines": state.lines,
            "polygons": state.polygons,
            "curves": state.curves
        }
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[✔] Сохранено в {file_path}")
    except Exception as e:
        print(f"[✖] Ошибка сохранения: {e}")

def load_from_json():
    try:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Открыть файл"
        )
        if not file_path:
            return
        with open(file_path, "r") as f:
            data = json.load(f)
        # Обновляем списки в state, модифицируя существующие списки через срезы
        state.points[:] = [tuple(p) for p in data.get("points", [])]
        state.lines[:] = [tuple(l) for l in data.get("lines", [])]
        state.polygons[:] = [{"indices": list(p["indices"]), "filled": p.get("filled", False)} for p in data.get("polygons", [])]
        state.curves[:] = [list(c) for c in data.get("curves", [])]
        print(f"[✔] Загружено из {file_path}")
    except Exception as e:
        print(f"[✖] Ошибка загрузки: {e}")
