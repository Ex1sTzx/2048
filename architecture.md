# 🏛️ Architecture: 2048 Streamlit

This document provides a high-level overview of the `2048.py` Python application.

## High-Level Design
The game uses a **monolithic architecture** contained entirely within a single Python script. By leveraging Streamlit's implicit request-response cycle, the application runs a top-down execution for each user input, rendering the updated state from `st.session_state` at every step.

## Core Components
The codebase is structured into four main components for clarity:

### 1. Configuration & Constants
- `TILE_COLORS`: A discrete mapping bridging numerical tile values (e.g., 2, 4, 128) to their frontend hexadecimal colors.

### 2. Game Logic (Engine)
Handles the fundamental mechanics of a 2048 game as pure functions that take current state inputs and return new state configurations.
* **`initialize_board()`**: Returns a clean 4x4 matrix mapped with two random starting tiles.
* **`move_left()`**: The core merging algorithm. Scans rows left-to-right to concatenate like-values.
* **`rotate_board()`**: Rotates the board 90 degrees. This allows movements in `[UP, RIGHT, DOWN]` to all use `move_left()` logic by just rotating the board into alignment, calculating the merge, and rotating back.
* **`is_game_over()`**: An exhaustive check ensuring no possible movements exist before throwing a Game Over state.

### 3. UI Render & Styling
Functions responsible for frontend visualization decoupled from game logic.
* **`apply_custom_styles()`**: Injects raw `<style>` tags for better button aesthetics.
* **`add_keyboard_support()`**: Mounts an invisible iframe containing a JavaScript `keydown` listener. This bridges DOM Arrow keys to Streamlit's Python-backend buttons.
* **`display_board()`**: Dynamically cycles the nested Python List representations of the board into UI elements (`st.columns` and `div` tags).

### 4. Main Application Execution
- The declarative `main()` block that coordinates Streamlit configurations.
- Intercepts state logic (`st.session_state`).
- Checks win/loss conditions on every re-run.

## State Management
Since Streamlit re-executes the file on every interaction, game persistence relies on Streamlit's caching dictionary: `st.session_state`.
- `st.session_state.board`: Holds the 4x4 coordinate list.
- `st.session_state.score`: Tracks incremental merges dynamically.
