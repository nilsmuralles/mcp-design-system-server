import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "design_tokens.json"

with DATA_PATH.open(encoding="utf-8") as f:
    TOKENS: dict = json.load(f)

def get_category(category: str) -> dict:
    if category not in TOKENS:
        raise ValueError(f"Categoría desconocida: '{category}'. Válidas: {list(TOKENS)}")
    return TOKENS[category]

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def flat_colors() -> dict[str, str]:
    flat = {}
    for role, scale in TOKENS["colors"].items():
        for step, hex_value in scale.items():
            flat[hex_value.lower()] = f"colors.{role}.{step}"
    return flat

def nearest_color(hex_color: str) -> tuple[str, str, float]:
    target = hex_to_rgb(hex_color)
    candidates = flat_colors()
    assert candidates, "design_tokens.json no tiene colores definidos"
    best_name, best_hex, best_dist = "", "", float("inf")
    for hex_value, name in candidates.items():
        r, g, b = hex_to_rgb(hex_value)
        dist = ((r - target[0]) ** 2 + (g - target[1]) ** 2 + (b - target[2]) ** 2) ** 0.5
        if dist < best_dist:
            best_name, best_hex, best_dist = name, hex_value, dist
    return best_name, best_hex, best_dist

def _px(value: str) -> float | None:
    value = value.strip()
    if value.endswith("px"):
        return float(value[:-2])
    if value.endswith("rem"):
        return float(value[:-3]) * 16
    return None

def flat_spacing() -> dict[float, tuple[str, str]]:
    flat = {}
    for name, raw in TOKENS["spacing"].items():
        px = _px(raw)
        if px is not None:
            flat[px] = (f"spacing.{name}", raw)
    return flat

def flat_font_sizes() -> dict[float, tuple[str, str]]:
    flat = {}
    for name, spec in TOKENS["typography"].items():
        px = _px(spec["fontSize"])
        if px is not None:
            flat[px] = (f"typography.{name}", spec["fontSize"])
    return flat

def nearest_px_token(flat: dict[float, tuple[str, str]], px_value: float) -> tuple[str, str, float]:
    assert flat, "no hay tokens numéricos en esta categoría"
    best_name, best_raw, best_dist = "", "", float("inf")
    for value, (name, raw) in flat.items():
        dist = abs(value - px_value)
        if dist < best_dist:
            best_name, best_raw, best_dist = name, raw, dist
    return best_name, best_raw, best_dist
