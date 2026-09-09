from app.tokens import flat_colors, hex_to_rgb

AA_NORMAL = 4.5
AA_LARGE = 3.0
AAA_NORMAL = 7.0
AAA_LARGE = 4.5

def _channel_luminance(c: int) -> float:
    c_srgb = c / 255
    if c_srgb <= 0.03928:
        return c_srgb / 12.92
    return ((c_srgb + 0.055) / 1.055) ** 2.4

def relative_luminance(hex_color: str) -> float:
    r, g, b = hex_to_rgb(hex_color)
    return 0.2126 * _channel_luminance(r) + 0.7152 * _channel_luminance(g) + 0.0722 * _channel_luminance(b)

def contrast_ratio(foreground: str, background: str) -> float:
    l1 = relative_luminance(foreground)
    l2 = relative_luminance(background)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def suggest_accessible_color(
    background: str, text_size: str = "normal", level: str = "AA", limit: int = 3
) -> dict:
    is_large = text_size == "large"
    if level == "AAA":
        threshold = AAA_LARGE if is_large else AAA_NORMAL
    else:
        threshold = AA_LARGE if is_large else AA_NORMAL

    candidates = []
    for hex_value, name in flat_colors().items():
        ratio = contrast_ratio(hex_value, background)
        candidates.append((ratio, name, hex_value))
    candidates.sort(key=lambda c: c[0], reverse=True)

    passing = [c for c in candidates if c[0] >= threshold]
    chosen = passing[:limit] if passing else candidates[:limit]

    return {
        "background": background,
        "text_size": text_size,
        "level": level,
        "threshold": threshold,
        "suggestions": [
            {"token": name, "hex": hex_value, "ratio": round(ratio, 2), "passes": ratio >= threshold}
            for ratio, name, hex_value in chosen
        ],
    }

def evaluate_contrast(ratio: float, text_size: str = "normal") -> dict:
    is_large = text_size == "large"
    aa_threshold = AA_LARGE if is_large else AA_NORMAL
    aaa_threshold = AAA_LARGE if is_large else AAA_NORMAL
    return {
        "ratio": round(ratio, 2),
        "text_size": text_size,
        "passes_aa": ratio >= aa_threshold,
        "passes_aaa": ratio >= aaa_threshold,
        "aa_threshold": aa_threshold,
        "aaa_threshold": aaa_threshold,
    }
