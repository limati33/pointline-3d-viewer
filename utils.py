import json
import tkinter as tk
from tkinter import filedialog
from model import points, lines, polygons, curves

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
            "points": points,
            "lines": lines,
            "polygons": polygons,
            "curves": curves
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
        points[:] = [tuple(p) for p in data.get("points", [])]
        lines[:] = [tuple(l) for l in data.get("lines", [])]
        polygons[:] = [{"indices": list(p["indices"]), "filled": p.get("filled", False)} for p in data.get("polygons", [])]
        curves[:] = [list(c) for c in data.get("curves", [])]
        print(f"[✔] Загружено из {file_path}")
    except Exception as e:
        print(f"[✖] Ошибка загрузки: {e}")
