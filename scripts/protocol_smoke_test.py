import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_PATH = REPO_ROOT / "examples" / "button.jsx"

def _print_result(label: str, result) -> None:
    text = "\n".join(block.text for block in result.content if block.type == "text")
    status = "ERROR" if result.isError else "ok"
    print(f"--- {label} [{status}] ---")
    print(text)
    print()

async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=["app/server.py"], cwd=str(REPO_ROOT))

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("--- tools/list ---")
            for tool in tools.tools:
                print(f"{tool.name}: {tool.description}")
            print()

            result = await session.call_tool("list_tokens", {"category": "colors"})
            _print_result("list_tokens(category='colors')", result)

            code = EXAMPLE_PATH.read_text(encoding="utf-8")
            result = await session.call_tool("check_consistency", {"code": code})
            _print_result("check_consistency(examples/button.jsx)", result)

            result = await session.call_tool(
                "check_contrast", {"foreground": "#ffffff", "background": "#ff6600"}
            )
            _print_result("check_contrast(#ffffff, #ff6600)", result)

            # Error paths — a stranger's chatbot won't always send valid input.
            result = await session.call_tool(
                "check_contrast", {"foreground": "no-es-un-color", "background": "#ffffff"}
            )
            _print_result("check_contrast(invalid hex) — expected error", result)

            result = await session.call_tool("list_tokens", {"category": "nope"})
            _print_result("list_tokens(category='nope') — expected error", result)

            result = await session.call_tool(
                "check_component_compliance",
                {"component": "Button", "variant": "danger", "spacing": "md", "foreground": "#ffffff", "background": "#dc2626"},
            )
            _print_result("check_component_compliance(compliant)", result)

            result = await session.call_tool(
                "check_component_compliance",
                {"component": "Button", "variant": "danger", "spacing": "xl", "foreground": "#ffffff", "background": "#dc2626"},
            )
            _print_result("check_component_compliance(spacing inválido)", result)

            result = await session.call_tool("suggest_accessible_color", {"background": "#dc2626"})
            _print_result("suggest_accessible_color(#dc2626)", result)

            result = await session.call_tool(
                "generate_component_code", {"component": "Button", "variant": "danger", "framework": "react"}
            )
            _print_result("generate_component_code(Button, danger, react)", result)

            result = await session.call_tool(
                "generate_component_code", {"component": "Button", "variant": "primary", "framework": "html"}
            )
            _print_result("generate_component_code(Button, primary, html)", result)

if __name__ == "__main__":
    asyncio.run(main())
