from fastmcp import FastMCP
from .chess_logic import ChessGame

mcp = FastMCP("stockfish")

# Global game state will be initialized in the main entrypoint
game = None

@mcp.tool
def get_board_state() -> str:
    """Get the current board state in FEN and markdown format."""
    state = game.get_board_state()
    markdown = game.get_board_markdown()
    moves = game.get_moves()
    moves_str = ", ".join(moves)
    return f"FEN: {state['fen']}\n\n{markdown}\n\nMoves: {moves_str}"

@mcp.tool
def make_move(move_uci: str) -> str:
    """
    Make a move using UCI notation (e.g., e2e4).
    Returns the board state after your move and the engine's reply.
    """
    success, message = game.make_move(move_uci)
    if not success:
        return f"Error: {message}"
    
    after_player_move_state = game.get_board_state()
    after_player_move_md = game.get_board_markdown()
    
    # Engine makes a move in response
    game.make_engine_move_internal()
    after_engine_move_state = game.get_board_state()
    after_engine_move_md = game.get_board_markdown()

    moves = game.get_moves()
    moves_str = ", ".join(moves)
    return f"**Your move:**\nFEN: `{after_player_move_state['fen']}`\n{after_player_move_md}\n\n**Engine's reply:**\nFEN: `{after_engine_move_state['fen']}`\n{after_engine_move_md}\n\nMoves: {moves_str}"

@mcp.tool
def is_game_over() -> bool:
    """Check if the game is over."""
    return game.is_game_over()

@mcp.tool
def get_game_result() -> str:
    """Get the result of the game if it is over."""
    return game.get_game_result()

@mcp.tool
def reset_game(skill_level: int = 10) -> str:
    """
    Reset the game to the initial state with a given engine skill level (0-20).
    The engine will be randomly assigned White or Black.
    Returns the initial board state.
    """
    game.reset_game()
    game.stockfish.set_skill_level(skill_level)
    initial_state = game.get_board_state()
    initial_md = game.get_board_markdown()
    engine_color = "White" if game.engine_color == 1 else "Black"
    moves = game.get_moves()
    moves_str = ", ".join(moves)
    return f"Game reset with skill level {skill_level}. Engine is playing as {engine_color}.\n\n**Initial board:**\nFEN: `{initial_state['fen']}`\n{initial_md}\n\nMoves: {moves_str}"
