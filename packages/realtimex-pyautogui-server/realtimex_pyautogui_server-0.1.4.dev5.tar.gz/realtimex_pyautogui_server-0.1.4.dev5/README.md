# realtimex-pyautogui-server

RealTimeX’s MCP server for deterministic desktop control with PyAutoGUI. This fork adapts the reference implementation with production defaults, a dedicated wait tool, and safeguards that prevent accidental keystrokes during pauses.

## Features
- Mouse movement, clicks, and drag support
- Keyboard typing and hotkeys
- Screen size, pixel, and screenshot utilities
- **Dedicated `wait(seconds)` tool** for precise pauses without injecting keystrokes
- Automatically releases modifier keys before typing to prevent stuck-shift issues
- Global PyAutoGUI defaults tuned for automation (`PAUSE`, `FAILSAFE`)

## Configuration
- Set `REALTIMEX_FAILSAFE` to `0` or `1` (default `1`) to control PyAutoGUI’s failsafe corner abort.
- Set `REALTIMEX_PAUSE` to a float (seconds) to override the global pause between PyAutoGUI actions (default `0.3`).

## Usage
```bash
uvx realtimex-pyautogui-server
```

The server communicates over stdio and is compatible with MCP clients like Claude Desktop and the MCP Inspector.

## Development
```bash
uv sync
uv run ruff check
uv run pytest
```
