# mcp-design-system-server

A local [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server that lets
an LLM-powered chatbot query and analyze a Design System: colors, typography, spacing,
and components. It can flag design inconsistencies in a piece of UI code and check color
contrast against WCAG accessibility criteria.

## Features

| Feature | Tool | Description |
|---|---|---|
| Query the Design System | `list_tokens` | List the color, typography, spacing, and component tokens, to find out what to use for a given case. |
| Consistency checking | `check_consistency` | Paste a real piece of code (CSS, JSX, HTML, etc.) and get back every color, font size, or spacing value that doesn't match a token, each with a suggested replacement (the closest matching token). |
| Accessibility (contrast) checking | `check_contrast` | Compute the WCAG contrast ratio between two colors and see whether it passes AA/AAA for normal or large text. |
| Component compliance checking | `check_component_compliance` | Validate a component usage (variant, spacing, colors) against the rules defined for that component — allowed variants, allowed spacing, minimum contrast. |
| Accessible color suggestions | `suggest_accessible_color` | Given a background color, get back which colors from the palette pass WCAG contrast against it, ranked best first. |
| Component code generation | `generate_component_code` | Generate ready-to-use React or HTML code for a component variant, with the text color picked automatically so it's accessible by construction. |

The Design System itself is defined in [`data/design_tokens.json`](data/design_tokens.json),
a small but realistic token set (semantic color roles, a type scale, an 8pt spacing
grid, and component specs). It is an internal implementation detail, not part of the
public tool contract: consumers only ever call the tools below, they never read this file
directly.

## Installation

Requires Python 3.10+ and Node.js is **not** required for this server (only the official
Filesystem MCP server used elsewhere in this project needs it).

```bash
git clone <this-repo-url>
cd mcp-design-system-server
python3 -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Troubleshooting

**Windows + WSL**: pick one environment and stick to it for both installing and running.
If you `pip install` using Windows' Python but then run `python app/server.py` from a WSL
terminal (or vice versa), the `mcp` package won't be found — WSL and Windows have
completely separate Python installations and package directories, even though they share
the same filesystem. Run every command above from the same shell (all inside WSL, or all
inside Windows PowerShell/cmd) — don't mix.

## Usage

The server speaks MCP over stdio. Run it directly to confirm it starts:

```bash
python app/server.py
```

To use it from an MCP host (a chatbot, the official
[MCP Inspector](https://github.com/modelcontextprotocol/inspector), Claude Desktop, etc.),
configure it as a local stdio server with the command:

```bash
python /absolute/path/to/mcp-design-system-server/app/server.py
```

For example, with the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python app/server.py
```

## Tool specification

### `list_tokens(category: str | None = None) -> dict`

Lists the Design System tokens. Leave `category` empty to get all four categories at
once, or pass one of `"colors"`, `"typography"`, `"spacing"`, `"components"` to get just
that one.

**Example call:** `list_tokens(category="colors")`

**Example response:**

```json
{
  "colors": {
    "primary": { "500": "#2563eb", "600": "#1d4ed8" },
    "danger": { "500": "#dc2626", "600": "#b91c1c" },
    "success": { "500": "#16a34a" },
    "neutral": { "0": "#ffffff", "50": "#f9fafb", "200": "#e5e7eb", "700": "#374151", "900": "#111827" }
  }
}
```

### `check_consistency(code: str) -> dict`

Scans a raw code snippet for hex colors, `font-size`, and `padding`/`margin`/`gap` values,
and compares each one against the Design System tokens. Comments (`//...` and `/* ... */`)
are stripped before scanning, so text inside comments is never flagged.

**Example call:** `check_consistency(code="<contents of a .jsx/.css file>")`

**Example response** (using [`examples/button.jsx`](examples/button.jsx), which contains
intentional violations):

```json
{
  "findings": [
    {
      "type": "color",
      "found": "#ff6600",
      "nearest_token": "colors.danger.500",
      "nearest_value": "#dc2626",
      "suggestion": "Usar el token 'colors.danger.500' (#dc2626) en vez de #ff6600"
    },
    {
      "type": "font-size",
      "found": "14px",
      "nearest_token": "typography.body",
      "nearest_value": "16px",
      "suggestion": "Usar el token 'typography.body' (16px) en vez de 14px"
    },
    {
      "type": "spacing",
      "found": "10px",
      "nearest_token": "spacing.sm",
      "nearest_value": "8px",
      "suggestion": "Usar el token 'spacing.sm' (8px) en vez de 10px"
    }
  ],
  "is_consistent": false
}
```

### `check_contrast(foreground: str, background: str, text_size: str = "normal") -> dict`

Computes the WCAG relative-luminance contrast ratio between two hex colors and evaluates
it against the AA/AAA thresholds. `text_size` is `"normal"` (AA ≥ 4.5, AAA ≥ 7.0) or
`"large"` (AA ≥ 3.0, AAA ≥ 4.5).

**Example call:** `check_contrast(foreground="#ffffff", background="#ff6600")`

**Example response:**

```json
{
  "ratio": 2.94,
  "text_size": "normal",
  "passes_aa": false,
  "passes_aaa": false,
  "aa_threshold": 4.5,
  "aaa_threshold": 7.0
}
```

### `check_component_compliance(component: str, variant: str, spacing: str, foreground: str, background: str) -> dict`

Validates a component usage against the rules defined for it in
`data/design_tokens.json` (allowed variants, allowed spacing, minimum contrast ratio).

**Example call:** `check_component_compliance(component="Button", variant="danger", spacing="xl", foreground="#ffffff", background="#dc2626")`

**Example response:**

```json
{
  "component": "Button",
  "variant": "danger",
  "compliant": false,
  "violations": ["spacing 'xl' no está permitido para Button; opciones: ['sm', 'md']"],
  "contrast_ratio": 4.83
}
```

### `suggest_accessible_color(background: str, text_size: str = "normal", level: str = "AA") -> dict`

The inverse of `check_contrast`: given only a background color, ranks the colors already
in the palette by how well they pass WCAG contrast against it.

**Example call:** `suggest_accessible_color(background="#dc2626")`

**Example response:**

```json
{
  "background": "#dc2626",
  "text_size": "normal",
  "level": "AA",
  "threshold": 4.5,
  "suggestions": [
    { "token": "colors.neutral.0", "hex": "#ffffff", "ratio": 4.83, "passes": true },
    { "token": "colors.neutral.50", "hex": "#f9fafb", "ratio": 4.62, "passes": true }
  ]
}
```

### `generate_component_code(component: str, variant: str, framework: str = "react") -> dict`

Generates real React or HTML code for a component variant, using the exact token values.
The text color is not guessed — it's picked by calling `suggest_accessible_color`
internally, so the generated code always passes the component's minimum contrast
requirement.

**Example call:** `generate_component_code(component="Button", variant="danger", framework="react")`

**Example response:**

```json
{
  "component": "Button",
  "variant": "danger",
  "framework": "react",
  "code": "function Button({ children }) {\n  return (\n    <button style={{ backgroundColor: \"#dc2626\", color: \"#ffffff\", padding: \"8px\", border: \"none\", borderRadius: \"6px\" }}>\n      {children}\n    </button>\n  );\n}",
  "tokens_used": { "background": "#dc2626", "foreground": "#ffffff", "spacing": "8px" }
}
```

## Example walkthrough

1. Start the server with the MCP Inspector: `npx @modelcontextprotocol/inspector python app/server.py`.
2. Call `list_tokens()` to see the full Design System.
3. Paste the contents of `examples/button.jsx` into `check_consistency` it will report
   the hardcoded color, the off-scale font size, and the off-scale padding, each with a
   suggested token.
4. Call `check_contrast(foreground="#ffffff", background="#ff6600")`  the same color used
   in that example  and confirm it fails WCAG AA for normal text.
5. Call `generate_component_code(component="Button", variant="danger", framework="react")`
   and confirm it returns a real, ready-to-paste React component using the actual brand
   colors, with a text color that already passes accessibility.

## Changelog

- Added `check_component_compliance`, `suggest_accessible_color`, and
  `generate_component_code` — additive, no existing tool's name, parameters, or response
  shape changed.

## Project structure

```
mcp-design-system-server/
  data/design_tokens.json   # the Design System's source of truth (internal, not part of the tool contract)
  app/
    tokens.py                # loads tokens.json, exposes lookup + nearest-match helpers
    consistency.py           # extracts style values from raw code and diffs them against tokens
    accessibility.py         # WCAG relative-luminance contrast calculation + accessible-color suggestions
    components.py            # component compliance checking + code generation
    server.py                # the MCP server itself (FastMCP), registers the 6 tools above
  examples/button.jsx        # fixture with intentional Design System violations, for demos/testing
```
