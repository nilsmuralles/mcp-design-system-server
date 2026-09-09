import sys
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp.server.fastmcp import FastMCP
from app.accessibility import contrast_ratio, evaluate_contrast
from app.accessibility import suggest_accessible_color as _suggest_accessible_color
from app.components import check_component_compliance as _check_component_compliance
from app.components import generate_component_code as _generate_component_code
from app.consistency import check_consistency as _check_consistency
from app.tokens import get_category

mcp = FastMCP("design-system")

TokenCategory = Literal["colors", "typography", "spacing", "components"]

@mcp.tool()
def list_tokens(category: TokenCategory | None = None) -> dict:
    """List the Design System tokens (colors, typography, spacing, components).
    Leave category empty to get all of them."""
    if category is None:
        from app.tokens import TOKENS
        return TOKENS
    return {category: get_category(category)}

@mcp.tool()
def check_consistency(code: str) -> dict:
    """Check a piece of code (CSS, JSX, HTML, etc.) against the Design System.
    Finds colors, font sizes, and spacing that don't match any token, and
    suggests the closest token to use instead."""
    findings = _check_consistency(code)
    return {"findings": findings, "is_consistent": len(findings) == 0}

@mcp.tool()
def check_contrast(
    foreground: str, background: str, text_size: Literal["normal", "large"] = "normal"
) -> dict:
    """Check the WCAG contrast ratio between two hex colors (foreground and
    background) and whether it passes AA/AAA for 'normal' or 'large' text."""
    ratio = contrast_ratio(foreground, background)
    return evaluate_contrast(ratio, text_size)

@mcp.tool()
def check_component_compliance(
    component: str, variant: str, spacing: str, foreground: str, background: str
) -> dict:
    """Check whether a component usage follows the Design System's rules for it
    (allowed variants, allowed spacing, minimum contrast ratio). Returns a list
    of violations, if any."""
    return _check_component_compliance(component, variant, spacing, foreground, background)

@mcp.tool()
def suggest_accessible_color(
    background: str,
    text_size: Literal["normal", "large"] = "normal",
    level: Literal["AA", "AAA"] = "AA",
) -> dict:
    """Given a background hex color, suggest which colors from the Design
    System's own palette pass WCAG contrast against it, ranked best first."""
    return _suggest_accessible_color(background, text_size, level)

@mcp.tool()
def generate_component_code(
    component: str, variant: str, framework: Literal["react", "html"] = "react"
) -> dict:
    """Generate ready-to-use React or HTML code for a Design System component
    variant, using the real token values. The text color is picked automatically
    so the result always passes the component's minimum contrast requirement."""
    return _generate_component_code(component, variant, framework)

if __name__ == "__main__":
    mcp.run()
