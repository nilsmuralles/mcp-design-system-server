from mcp.server.fastmcp import FastMCP
from app.accessibility import contrast_ratio, evaluate_contrast
from app.consistency import check_consistency as _check_consistency
from app.tokens import get_category

mcp = FastMCP("design-system")

@mcp.tool()
def list_tokens(category: str | None = None) -> dict:
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
def check_contrast(foreground: str, background: str, text_size: str = "normal") -> dict:
    """Check the WCAG contrast ratio between two hex colors (foreground and
    background) and whether it passes AA/AAA for 'normal' or 'large' text."""
    ratio = contrast_ratio(foreground, background)
    return evaluate_contrast(ratio, text_size)

if __name__ == "__main__":
    mcp.run()
