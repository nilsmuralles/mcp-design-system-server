import re

from app.tokens import flat_colors, flat_font_sizes, flat_spacing, nearest_color, nearest_px_token

HEX_COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,6}\b")
FONT_SIZE_RE = re.compile(r"font-?[Ss]ize\s*[:=]\s*['\"]?(\d+(?:\.\d+)?)(px|rem)['\"]?")
SPACING_RE = re.compile(
    r"(?:padding|margin|gap)(?:-\w+)?\s*[:=]\s*['\"]?(\d+(?:\.\d+)?)(px|rem)['\"]?"
)
LINE_COMMENT_RE = re.compile(r"//.*")
BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)

PX_PER_REM = 16

def _to_px(value: str, unit: str) -> float:
    n = float(value)
    return n * PX_PER_REM if unit == "rem" else n

def _strip_comments(code: str) -> str:
    code = BLOCK_COMMENT_RE.sub("", code)
    code = LINE_COMMENT_RE.sub("", code)
    return code

def check_consistency(code: str) -> list[dict]:
    code = _strip_comments(code)
    findings: list[dict] = []
    known_colors = flat_colors()

    for match in HEX_COLOR_RE.finditer(code):
        hex_value = match.group(0).lower()
        if hex_value in known_colors:
            continue
        token_name, token_hex, _ = nearest_color(hex_value)
        findings.append(
            {
                "type": "color",
                "found": hex_value,
                "nearest_token": token_name,
                "nearest_value": token_hex,
                "suggestion": f"Usar el token '{token_name}' ({token_hex}) en vez de {hex_value}",
            }
        )

    font_sizes = flat_font_sizes()
    for match in FONT_SIZE_RE.finditer(code):
        px = _to_px(match.group(1), match.group(2))
        if px in font_sizes:
            continue
        token_name, token_raw, _ = nearest_px_token(font_sizes, px)
        findings.append(
            {
                "type": "font-size",
                "found": f"{match.group(1)}{match.group(2)}",
                "nearest_token": token_name,
                "nearest_value": token_raw,
                "suggestion": f"Usar el token '{token_name}' ({token_raw}) en vez de {match.group(1)}{match.group(2)}",
            }
        )

    spacing = flat_spacing()
    for match in SPACING_RE.finditer(code):
        px = _to_px(match.group(1), match.group(2))
        if px in spacing:
            continue
        token_name, token_raw, _ = nearest_px_token(spacing, px)
        findings.append(
            {
                "type": "spacing",
                "found": f"{match.group(1)}{match.group(2)}",
                "nearest_token": token_name,
                "nearest_value": token_raw,
                "suggestion": f"Usar el token '{token_name}' ({token_raw}) en vez de {match.group(1)}{match.group(2)}",
            }
        )

    return findings
