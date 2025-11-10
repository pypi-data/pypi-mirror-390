# Stockfish MCP Server

<!-- mcp-name: io.github.stepbot/stockfish-mcp -->

A Stockfish server for the Model Context Protocol. This package allows a Large Language Model to play chess against the Stockfish engine.

## Installation

Install the package from PyPI:

```bash
pip install stockfish-mcp
```

## Usage

Run the server from the command line:

```bash
stockfish-mcp
```

You can also provide a path to a custom Stockfish executable:

```bash
stockfish-mcp --stockfish-path /path/to/your/stockfish

## Example

An example of a game played against the Stockfish engine can be found in [`exampleGame.md`](./exampleGame.md).

## Available Tools

- `get_board_state()`: Get the current board state.
- `make_move(move_uci: str)`: Make a move (e.g., "e2e4").
- `is_game_over()`: Check if the game has ended.
- `get_game_result()`: Get the result if the game is over.
- `reset_game(skill_level: int = 10)`: Start a new game.