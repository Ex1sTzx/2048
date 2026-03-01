import pytest
from streamlit.testing.v1 import AppTest
import streamlit as st

# Import the logic functions from our main app file
# Assuming it's in the same directory and named '2048.py'
import importlib.util
import sys

# Hack to import a module starting with numbers
spec = importlib.util.spec_from_file_location("game_2048", "2048.py")
game = importlib.util.module_from_spec(spec)
sys.modules["game_2048"] = game
spec.loader.exec_module(game)


class TestGameLogic:
    """
    Functional Tests for the core game engine to ensure that state transformations
    behave mathematically exactly as expected in 2048.
    """

    def test_initialize_board(self):
        """Test that the board initializes correctly with two tiles."""
        board = game.initialize_board()
        assert len(board) == 4
        assert all(len(row) == 4 for row in board)
        
        # Count non-zero tiles
        non_zero_tiles = sum(1 for row in board for val in row if val != 0)
        assert non_zero_tiles == 2

    def test_move_left_simple_merge(self):
        """Test simple horizontal adjacent merges."""
        st.session_state.score = 0  # Mock session state since logic relies on it
        board = [
            [2, 2, 0, 0],
            [4, 0, 4, 0],
            [8, 8, 8, 8],
            [2, 4, 8, 16]
        ]
        new_board = game.move_left(board)
        
        assert new_board[0] == [4, 0, 0, 0]
        assert new_board[1] == [8, 0, 0, 0]
        assert new_board[2] == [16, 16, 0, 0]  # First two 8s merge, second two 8s merge
        assert new_board[3] == [2, 4, 8, 16]   # No merges

    def test_rotate_board(self):
        """Test 90 degree counter-clockwise rotation."""
        board = [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12],
            [13, 14, 15, 16]
        ]
        rotated = game.rotate_board(board)
        expected = [
            [4, 8, 12, 16],
            [3, 7, 11, 15],
            [2, 6, 10, 14],
            [1, 5, 9, 13]
        ]
        assert rotated == expected

    def test_game_over_conditions(self):
        """Functional cases targeting win/loss state conditions."""
        
        # Scenario 1: Empty spaces exist
        board_with_empty = [
            [2, 4, 8, 16],
            [32, 64, 128, 256],
            [512, 1024, 2048, 0],
            [8, 4, 2, 4]
        ]
        assert game.is_game_over(board_with_empty) == False

        # Scenario 2: Full board but vertical merges available
        board_vertical_merge = [
            [2, 4, 8, 16],
            [2, 64, 128, 256],
            [512, 1024, 4, 8],
            [16, 32, 64, 128]
        ]
        assert game.is_game_over(board_vertical_merge) == False

        # Scenario 3: Full board but horizontal merges available
        board_horizontal_merge = [
            [2, 4, 8, 16],
            [32, 64, 128, 256],
            [512, 512, 4, 8],
            [16, 32, 64, 128]
        ]
        assert game.is_game_over(board_horizontal_merge) == False

        # Scenario 4: True Game Over (Full board, no merges)
        board_game_over = [
            [2, 4, 8, 16],
            [32, 64, 128, 256],
            [2, 4, 8, 16],
            [32, 64, 128, 256]
        ]
        assert game.is_game_over(board_game_over) == True


class TestRegression:
    """
    Regression Tests to ensure edge cases in moving algorithms do not regress.
    These scenarios mimic complex states where bugs often appear in 2048 clones.
    """

    def setup_method(self):
        st.session_state.score = 0

    def test_regression_triple_merge(self):
        """
        Bug: [2, 2, 2, 0] moved left might unexpectedly result in [4, 2, 0, 0] or [2, 4, 0, 0].
        Standard 2048 logic merges closest to the movement wall first.
        Left move on [2, 2, 2, 0] -> [4, 2, 0, 0].
        """
        board = [[2, 2, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        new_board = game.move_left(board)
        assert new_board[0] == [4, 2, 0, 0]

    def test_regression_cascade_merge(self):
        """
        Bug: [4, 2, 2, 0] moved left might result in [8, 0, 0, 0]
        Because 2+2=4, and then that 4 merges with the first 4.
        Standard 2048 forbids a tile from participating in multiple merges per turn.
        Expected: [4, 4, 0, 0].
        """
        board = [[4, 2, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        new_board = game.move_left(board)
        assert new_board[0] == [4, 4, 0, 0]

    def test_regression_move_full_direction(self):
        """
        Test the `move()` wrapper which utilizes rotations, ensuring the direction
        mapping has not regressed.
        """
        board = [
            [0, 0, 2, 0],
            [0, 0, 2, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        
        # Test UP
        up_board = game.move(board, "UP")
        # Ensure we check the correct columns. The board spawns a random tile, 
        # so we extract the deterministic part of the column we know must occur.
        # Two 2s moving UP in Column 2 should merge to a single 4 at (row 0, col 2)
        assert up_board[0][2] == 4
        assert up_board[1][2] == 0

    def test_regression_no_change_prevents_spawn(self):
        """
        If a user inputs a move against a wall but the tiles cannot move,
        a new tile is NOT generated.
        """
        board = [
            [2, 0, 0, 0],
            [4, 0, 0, 0],
            [8, 0, 0, 0],
            [16, 0, 0, 0]
        ]
        # Copy to compare exact equality as deepcopy is not used here to prevent spawn
        original_copy = [row[:] for row in board]
        
        new_board = game.move(board, "LEFT")
        
        # Board should be mathematically identical; length check isn't enough, we check equality
        assert new_board == original_copy
