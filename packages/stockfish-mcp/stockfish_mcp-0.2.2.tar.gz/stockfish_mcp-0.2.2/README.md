# Stockfish MCP Server

<!-- mcp-name: io.github.stepbot/stockfish-mcp -->

A Stockfish server for the Model Context Protocol. This package allows a Large Language Model to play chess against the Stockfish engine.

## Installation

This package is a pure Python wrapper and requires you to provide your own Stockfish binary.

1.  **Download Stockfish:** Get the appropriate version for your system from the [official Stockfish website](https://stockfishchess.org/download/).

2.  **Install the MCP Server:** We recommend using `uv` to install the package. First, [install `uv`](https://github.com/astral-sh/uv). Then, run the following command to install `stockfish-mcp` as a globally available command-line tool in its own isolated environment:
    ```bash
    uv tool install stockfish-mcp
    ```

## Usage

There are two ways to run the server:

### 1. Command Line

You can run the server directly, providing the path to your downloaded Stockfish executable.

```bash
uv tool run stockfish-mcp --stockfish-path C:\path\to\your\stockfish.exe
```

### 2. MCP Configuration

Alternatively, you can add it to your MCP `settings.json` file. This is useful for integrating with clients like the MCP VS Code extension.

```json
{
    "mcpServers": {
        "stockfish": {
            "command": "uv",
            "args": ["tool", "run", "stockfish-mcp", "--stockfish-path", "C:\\path\\to\\your\\stockfish.exe"]
        }
    }
}
```

## Example

An example of a game played against the Stockfish engine can be found in [`exampleGame.md`](./exampleGame.md).

## Available Tools

- `get_board_state()`: Get the current board state.
- `make_move(move_uci: str)`: Make a move (e.g., "e2e4").
- `is_game_over()`: Check if the game has ended.
- `get_game_result()`: Get the result if the game is over.
- `reset_game(skill_level: int = 10)`: Start a new game.