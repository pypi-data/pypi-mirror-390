import chess
import random
from stockfish import Stockfish

class ChessGame:
    def __init__(self, stockfish_path, skill_level=10):
        self.board = chess.Board()
        self.stockfish_path = stockfish_path
        self.skill_level = skill_level
        self.engine_color = random.choice([chess.WHITE, chess.BLACK])
        self.moves = []
        try:
            self.stockfish = Stockfish(path=stockfish_path)
            self.stockfish.set_skill_level(self.skill_level)
        except (FileNotFoundError, OSError):
            self.stockfish = None

        if self.engine_color == chess.WHITE:
            self.make_engine_move_internal()


    def get_board_state(self):
        """Returns the FEN and a simple text visualization of the board."""
        fen = self.board.fen()
        board_str = str(self.board)
        return {"fen": fen, "board": board_str}

    def get_board_markdown(self):
        """Returns a markdown table representation of the board."""
        piece_map = {
            'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
            'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
            '.': ' '
        }
        
        markdown = "| | a | b | c | d | e | f | g | h |\n"
        markdown += "|---|---|---|---|---|---|---|---|---|\n"
        
        board_str = str(self.board).replace(' ', '')
        rows = board_str.split('\n')
        
        for i, row in enumerate(rows):
            rank = 8 - i
            markdown += f"| {rank} |"
            for piece_char in row:
                markdown += f" {piece_map[piece_char]} |"
            markdown += "\n"
            
        return markdown

    def make_move(self, move_uci):
        """Makes a move on the board using UCI notation."""
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.moves.append(move_uci)
                return True, "Move successful."
            else:
                return False, "Illegal move."
        except ValueError:
            return False, "Invalid move format. Use UCI notation (e.g., e2e4)."

    def make_engine_move_internal(self):
        """Internal method to have the engine make a move."""
        if not self.stockfish:
            return None
        self.stockfish.set_fen_position(self.board.fen())
        best_move_uci = self.stockfish.get_best_move()
        if best_move_uci:
            move = chess.Move.from_uci(best_move_uci)
            self.board.push(move)
            self.moves.append(best_move_uci)
        return best_move_uci

    def is_game_over(self):
        """Checks if the game is over."""
        return self.board.is_game_over()

    def get_game_result(self):
        """Returns the result of the game."""
        if self.board.is_checkmate():
            return "Checkmate"
        if self.board.is_stalemate():
            return "Stalemate"
        if self.board.is_insufficient_material():
            return "Insufficient Material"
        if self.board.is_seventyfive_moves():
            return "75-move rule"
        if self.board.is_fivefold_repetition():
            return "Fivefold Repetition"
        return "Game in progress"

    def reset_game(self):
        """Resets the board to the starting position."""
        self.board.reset()
        self.moves = []

    def get_moves(self):
        """Returns the list of moves made so far."""
        return self.moves