import argparse
import os
import platform
import sys
from importlib import resources
import shutil
from .mcp_server import mcp, game
from .chess_logic import ChessGame

def main():
    parser = argparse.ArgumentParser(description="Run the Chess MCP server.")
    parser.add_argument("--stockfish-path", help="Path to the Stockfish executable.")
    args = parser.parse_args()

    stockfish_path = args.stockfish_path

    if not stockfish_path:
        # If the user doesn't provide a path, search for "stockfish" in the system's PATH
        stockfish_path = shutil.which("stockfish")

    if not stockfish_path:
        parser.error("Stockfish executable not found. Please install Stockfish and ensure it is in your PATH, or provide the path using the --stockfish-path argument.")

    global game
    game = ChessGame(stockfish_path=stockfish_path, skill_level=10)
    mcp.run()

if __name__ == "__main__":
    main()