from app.accessibility import contrast_ratio, suggest_accessible_color
from app.tokens import TOKENS, get_component, resolve_token_path

def check_component_compliance(
    component: str, variant: str, spacing: str, foreground: str, background: str
) -> dict:
    spec = get_component(component)
    violations = []

    if variant not in spec["variants"]:
        violations.append(
            f"variant '{variant}' no está permitida para {component}; opciones: {spec['variants']}"
        )

    allowed_spacing = spec.get("allowedSpacing")
    if allowed_spacing and spacing not in allowed_spacing:
        violations.append(
            f"spacing '{spacing}' no está permitido para {component}; opciones: {allowed_spacing}"
        )

    ratio = contrast_ratio(foreground, background)
    min_ratio = spec.get("minContrastRatio")
    if min_ratio and ratio < min_ratio:
        violations.append(
            f"contraste {round(ratio, 2)} por debajo del mínimo requerido {min_ratio}"
        )

    return {
        "component": component,
        "variant": variant,
        "compliant": len(violations) == 0,
        "violations": violations,
        "contrast_ratio": round(ratio, 2),
    }


def generate_component_code(component: str, variant: str, framework: str = "react") -> dict:
    spec = get_component(component)
    if variant not in spec["variants"]:
        raise ValueError(f"variant '{variant}' no está permitida para {component}; opciones: {spec['variants']}")

    variant_colors = spec.get("variantColors", {})
    if variant not in variant_colors:
        raise ValueError(f"No hay un color definido para la variante '{variant}' de {component}")

    background = resolve_token_path(variant_colors[variant])
    accessible = suggest_accessible_color(background=background)
    foreground = accessible["suggestions"][0]["hex"]

    allowed_spacing = spec.get("allowedSpacing", [])
    spacing_name = allowed_spacing[0] if allowed_spacing else "md"
    spacing_px = TOKENS["spacing"].get(spacing_name, "16px")

    if framework == "react":
        code = (
            f'function {component}({{ children }}) {{\n'
            f'  return (\n'
            f'    <button\n'
            f'      style={{{{\n'
            f'        backgroundColor: "{background}",\n'
            f'        color: "{foreground}",\n'
            f'        padding: "{spacing_px}",\n'
            f'        border: "none",\n'
            f'        borderRadius: "6px",\n'
            f'      }}}}\n'
            f'    >\n'
            f'      {{children}}\n'
            f'    </button>\n'
            f'  );\n'
            f'}}'
        )
    elif framework == "html":
        code = (
            f'<button style="background-color: {background}; color: {foreground}; '
            f'padding: {spacing_px}; border: none; border-radius: 6px;">\n'
            f"  {variant.capitalize()} {component}\n"
            f"</button>"
        )
    else:
        raise ValueError(f"framework desconocido: '{framework}'. Válidos: react, html")

    return {
        "component": component,
        "variant": variant,
        "framework": framework,
        "code": code,
        "tokens_used": {
            "background": background,
            "foreground": foreground,
            "spacing": spacing_px,
        },
    }
